# Métricas del Proyecto

Se hizo un experimento, se levanto el stack con `make dev`:

```
CONTAINER ID   IMAGE                COMMAND                  CREATED         STATUS                   PORTS                                       NAMES
d51f469e3d79   compose-api          "uvicorn main:app --…"   8 minutes ago   Up 8 minutes (healthy)   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   local_secure_api
b5a843d00dc9   postgres:16-alpine   "docker-entrypoint.s…"   8 minutes ago   Up 8 minutes (healthy)   5432/tcp                                    local_secure_db
```

Y luego gracias a la ejecucion del script `recopilar_metricas.py` se generó un `metricas-output.json` con las siguientes métricas:

### Stack Health

| Métrica               | Valor   | Target |
| --------------------- | ------- | ------ |
| Tiempo arranque DB    | 0.21 s  | < 2 s  |
| Tiempo arranque API   | 5.03 s  | < 8 s  |
| Tiempo arranque stack | 17.15 s | < 30 s |
| Stack listo < 30s     | Sí      | Sí     |

### API Metrics

| Métrica                   | Valor    |
| ------------------------- | -------- |
| Disponible                | Sí       |
| Requests exitosas         | 20       |
| Requests fallidas         | 0        |
| Error rate                | 0%       |
| Tiempo respuesta promedio | 45.29 ms |
| Tiempo respuesta mínimo   | 32.13 ms |
| Tiempo respuesta máximo   | 58.91 ms |
| P90 tiempo de respuesta   | 50.32 ms |

### Docker Metrics

| Contenedor       | CPU % | Memoria           | Network I/O     |
| ---------------- | ----- | ----------------- | --------------- |
| local_secure_api | 0.34% | 40.15MiB / 512MiB | 91.8kB / 73.5kB |
| local_secure_db  | 0.04% | 29.51MiB / 512MiB | 65.3kB / 59.8kB |

### Volúmenes

* Total de volúmenes: **3**

### Database Metrics

| Métrica              | Valor   |
| -------------------- | ------- |
| Conexión             | Sí      |
| Filas en tabla notes | 43      |
| Tamaño base de datos | 7604 kB |