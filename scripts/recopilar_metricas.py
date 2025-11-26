#!/usr/bin/env python3

# Script de recolección de métricas para Local Secure Stack

import subprocess
import json
import time
import requests
import sys
from datetime import datetime
from typing import Dict, List, Any

class RecopilarMetricas:
    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        self.api_url = api_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "api_metricas": {},
            "docker_metricas": {},
            "database_metricas": {},
            "arranque_metricas": {}
        }

    def recopilar_api_health(self) -> Dict[str, Any]:
        """Mide disponibilidad y tiempo de respuesta de API."""
        print("- Recolectando métricas de API...")
        
        metrics = {
            "disponible": False,
            "tiempo_respuesta_ms": [],
            "error_rate": 0,
            "requests_exitosas": 0,
            "requests_fallidas": 0
        }
        
        # Realizamos 20 peticiones para tener muestra estadística
        total_requests = 20
        
        for i in range(total_requests):
            try:
                start = time.time()
                response = requests.post(
                    f"{self.api_url}/api/salud/",
                    json={"peticion": f"metric-test-{i}"},
                    timeout=5
                )
                elapsed_ms = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    metrics["requests_exitosas"] += 1
                    metrics["tiempo_respuesta_ms"].append(round(elapsed_ms, 2))
                else:
                    metrics["requests_fallidas"] += 1
                    
            except Exception as e:
                metrics["requests_fallidas"] += 1
                print(f"  -  Request {i+1} falló: {e}")
            
            time.sleep(0.1)  # pausa entre requests
        
        if metrics["requests_exitosas"] > 0:
            metrics["disponible"] = True
            metrics["tiempo_respuesta_promedio"] = round(
                sum(metrics["tiempo_respuesta_ms"]) / len(metrics["tiempo_respuesta_ms"]), 2
            )
            metrics["tiempo_respuesta_minimo"] = min(metrics["tiempo_respuesta_ms"])
            metrics["tiempo_respuesta_maximo"] = max(metrics["tiempo_respuesta_ms"])
            metrics["p90_tiempo_respuesta_ms"] = self.percentil(metrics["tiempo_respuesta_ms"], 90)
            
        metrics["error_rate"] = round(
            (metrics["requests_fallidas"] / total_requests) * 100, 2
        )
        
        return metrics

    def recopilar_recursos_de_docker(self) -> Dict[str, Any]:
        """Recolecta uso de CPU, memoria y red de contenedores."""
        print("- Recolectando métricas de Docker...")
        
        metrics = {
            "contenedores": {}
        }
        
        try:
            # obtener stats de contenedores
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", 
                 "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    container_name = parts[0]
                    
                    metrics["contenedores"][container_name] = {
                        "porcentaje_cpu": parts[1],
                        "uso_memoria": parts[2],
                        "network_io": parts[3]
                    }
            
            # obtener info de volúmenes
            vol_result = subprocess.run(
                ["docker", "volume", "ls", "-q"],
                capture_output=True,
                text=True
            )
            metrics["volumes_count"] = len(vol_result.stdout.strip().split('\n'))
            
        except Exception as e:
            print(f"  -  Error recolectando métricas Docker: {e}")
            
        return metrics

    def recopilar_metricas_de_base_de_datos(self) -> Dict[str, Any]:
        """Métricas de PostgreSQL."""
        print("- Recolectando métricas de PostgreSQL...")
        
        metrics = {
            "conexion_test": False,
            "conteo_filas_tabla": 0,
            "database_size": 0
        }
        
        try:
            # verificar que el contenedor está corriendo
            result = subprocess.run(
                ["docker", "exec", "local_secure_db", 
                 "psql", "-U", "notes_user", "-d", "notes_db", 
                 "-t", "-c", "SELECT COUNT(*) FROM notes;"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                metrics["conexion_test"] = True
                metrics["conteo_filas_tabla"] = int(result.stdout.strip())
            
            # tamaño de la base de datos
            size_result = subprocess.run(
                ["docker", "exec", "local_secure_db",
                 "psql", "-U", "notes_user", "-d", "notes_db",
                 "-t", "-c", "SELECT pg_size_pretty(pg_database_size('notes_db'));"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if size_result.returncode == 0:
                metrics["database_size"] = size_result.stdout.strip()
                
        except Exception as e:
            print(f"  -  Error recolectando métricas DB: {e}")
            
        return metrics

    def recopilar_metricas_de_arranque(self) -> Dict[str, Any]:
        """Mide tiempo de arranque de servicios."""
        print("- Midiendo tiempos de arranque...")
        
        metrics = {
            "tiempo_arranque_stack_segundos": 0,
            "db_listo_segundos": 0,
            "api_listo_segundos": 0
        }
        
        try:
            # apagar servicios primero
            subprocess.run(
                ["docker", "compose", "-f", "compose/docker-compose.yml", "down"],
                capture_output=True,
                timeout=30
            )
            
            # medir tiempo de arranque completo
            start_time = time.time()
            
            subprocess.run(
                ["docker", "compose", "-f", "compose/docker-compose.yml", "up", "-d"],
                capture_output=True,
                timeout=60
            )
            
            # esperar a que DB esté lista
            db_start = time.time()
            db_ready = False
            for _ in range(30):  # Máximo 30 segundos
                result = subprocess.run(
                    ["docker", "exec", "local_secure_db", "pg_isready", "-U", "notes_user"],
                    capture_output=True
                )
                if result.returncode == 0:
                    metrics["db_listo_segundos"] = round(time.time() - db_start, 2)
                    db_ready = True
                    break
                time.sleep(1)
            
            # esperar a que API esté lista
            api_start = time.time()
            api_ready = False
            for _ in range(30):  # máximo 30 segundos
                try:
                    response = requests.get(f"{self.api_url}/api/salud/", timeout=2)
                    if response.status_code in [200, 405]:  # 405 = método no permitido pero API responde
                        metrics["api_listo_segundos"] = round(time.time() - api_start, 2)
                        api_ready = True
                        break
                except:
                    pass
                time.sleep(1)
            
            metrics["tiempo_arranque_stack_segundos"] = round(time.time() - start_time, 2)
            metrics["arranque_exitoso_stack_30s"] = db_ready and api_ready
            
        except Exception as e:
            print(f"  -  Error midiendo arranque: {e}")
            metrics["arranque_exitoso_stack_30s"] = False
            
        return metrics

    def percentil(self, data: List[float], percentile: int) -> float:
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return round(sorted_data[min(index, len(sorted_data) - 1)], 2)

    def recopilacion_total(self) -> Dict[str, Any]:
        
        print("INICIANDO RECOLECCIÓN DE MÉTRICAS")
        
        self.results["api_metricas"] = self.recopilar_api_health()
        self.results["docker_metricas"] = self.recopilar_recursos_de_docker()
        self.results["database_metricas"] = self.recopilar_metricas_de_base_de_datos()
        # self.results["arranque_metricas"] = self.recopilar_metricas_de_arranque()
        
        return self.results

    def imprimir_resumen(self):

        print("\nRESUMEN DE MÉTRICAS")
        
        # API
        api = self.results["api_metricas"]
        print("- API:")
        print(f"  Disponible: {'Si' if api.get('disponible') else 'No'}")
        if api.get('disponible'):
            print(f"  Tiempo promedio: {api.get('tiempo_respuesta_promedio', 0)} ms")
            print(f"  P90: {api.get('p90_tiempo_respuesta_ms', 0)} ms")
            print(f"  Tasa de error: {api.get('error_rate', 0)}%")
        
        # Docker
        docker = self.results["docker_metricas"]
        print(f"\n- Docker:")
        for container, stats in docker.get("contenedores", {}).items():
            print(f"  {container}:")
            print(f"    CPU: {stats['porcentaje_cpu']}")
            print(f"    Memoria: {stats['uso_memoria']}")
        
        # base de datos
        db = self.results["database_metricas"]
        print(f"\n- PostgreSQL:")
        print(f"  Conexión: {'Si' if db.get('conexion_test') else 'No'}")
        print(f"  Registros en tabla notes: {db.get('conteo_filas_tabla', 0)}")
        print(f"  Tamaño DB: {db.get('database_size', 'N/A')}")

    def save_to_file(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n- Métricas guardadas en: {filename}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Recolector de métricas')
    parser.add_argument('--output', default='metricas-output.json', 
                       help='Archivo de salida JSON')
    parser.add_argument('--api-url', default='http://127.0.0.1:8000',
                       help='URL de la API')
    parser.add_argument('--arranque', action='store_true',
                       help='Incluir métricas de arranque (reinicia servicios)')
    
    args = parser.parse_args()
    
    collector = RecopilarMetricas(api_url=args.api_url)
    
    try:
        collector.recopilacion_total()
        
        if args.arranque:
            collector.results["arranque_metricas"] = collector.recopilar_metricas_de_arranque()
        
        collector.imprimir_resumen()
        collector.save_to_file(args.output)
        
    except KeyboardInterrupt:
        print("\n\n-  Recolección interrumpida")
        sys.exit(1)
    except Exception as e:
        print(f"\n ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()