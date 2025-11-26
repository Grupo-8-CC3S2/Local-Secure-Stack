# Risk Register - Local Secure Stack

### Incompatibilidad de Versiones Docker

Docker Compose v2 (nuevo) usa sintaxis diferente a v1. Miembros del equipo pueden tener versiones distintas causando errores al ejecutar `docker compose`.

### Secretos Expuestos en Git

Archivo `.env` con credenciales reales puede committearse accidentalmente, exponiendo passwords de DB en repositorio público.

### Pérdida de Datos por Volumen Mal Configurado

Si volumen `db_data` no está correctamente configurado o se usa `-v` en `down.sh`, todos los datos de PostgreSQL se eliminan permanentemente.

### Dependencia de Internet No Documentada

Docker debe descargar imágenes (postgres, python) en primer `up`. Si no hay internet o es lento, el setup falla sin mensaje claro.

### Incompatibilidad de Puertos con Otros Servicios

Puerto 8000 (API) o 5432 (PostgreSQL) pueden estar ocupados por otros servicios en laptop de desarrollador (otro proyecto, Postgres nativo, etc.).

### Falta de Sincronización Entre Miembros del Equipo

Tres personas trabajando en paralelo sin comunicación pueden crear código incompatible o duplicado.