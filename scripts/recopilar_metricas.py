#!/usr/bin/env python3

# Script de recolección de métricas para Local Secure Stack

import subprocess
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any

class RecopilarMetricas:
    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        self.api_url = api_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "api_metricas": {},
            "docker_metricas": {}
        }

    def recopilar_api_health(self) -> Dict[str, Any]:
        """Mide disponibilidad y tiempo de respuesta de API."""
        print("- Recolectando métricas de API...")
        
        metrics = {
            "disponible": False,
            "tiempo_respuesta_ms": [],
            "requests_exitosas": 0,
            "requests_fallidas": 0
        }
        
        # Realizamos 10 peticiones para tener muestra estadística
        total_requests = 10
        
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
            
            time.sleep(0.1)
        
        if metrics["requests_exitosas"] > 0:
            metrics["disponible"] = True
            metrics["tiempo_respuesta_promedio"] = round(
                sum(metrics["tiempo_respuesta_ms"]) / len(metrics["tiempo_respuesta_ms"]), 2
            )
            
        return metrics

    def recopilar_recursos_de_docker(self) -> Dict[str, Any]:
        """Recolecta uso de CPU y memoria de contenedores."""
        print("- Recolectando métricas de Docker...")
        
        metrics = {
            "contenedores": {}
        }
        
        try:
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", 
                 "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"],
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
                        "uso_memoria": parts[2]
                    }
            
        except Exception as e:
            print(f"  -  Error recolectando métricas Docker: {e}")
            
        return metrics

    def recopilacion_total(self) -> Dict[str, Any]:
        print("INICIANDO RECOLECCIÓN DE MÉTRICAS")
        
        self.results["api_metricas"] = self.recopilar_api_health()
        self.results["docker_metricas"] = self.recopilar_recursos_de_docker()
        
        return self.results

    def imprimir_resumen(self):
        print("\nRESUMEN DE MÉTRICAS")
        
        # API
        api = self.results["api_metricas"]
        print("- API:")
        print(f"  Disponible: {'Si' if api.get('disponible') else 'No'}")
        if api.get('disponible'):
            print(f"  Tiempo promedio: {api.get('tiempo_respuesta_promedio', 0)} ms")
        
        # Docker
        docker = self.results["docker_metricas"]
        print(f"\n- Docker:")
        for container, stats in docker.get("contenedores", {}).items():
            print(f"  {container}:")
            print(f"    CPU: {stats['porcentaje_cpu']}")
            print(f"    Memoria: {stats['uso_memoria']}")

    def save_to_file(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n- Métricas guardadas en: {filename}")


def main():
    collector = RecopilarMetricas()
    
    try:
        collector.recopilacion_total()
        collector.imprimir_resumen()
        collector.save_to_file('metricas-output.json')
        
    except KeyboardInterrupt:
        print("\n\n-  Recolección interrumpida")
    except Exception as e:
        print(f"\n ERROR: {e}")

if __name__ == "__main__":
    main()