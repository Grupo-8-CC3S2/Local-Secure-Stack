#!/usr/bin/bash
set -o pipefail
set -e
set -u

umask 022
#modificar el valor de peticion cada vez
RESPUESTA=""
check_salud(){
    echo -e "checkeo de salud"
    RESPUESTA=$(curl -s -X POST http://127.0.0.1:8000/api/salud/ -H "Content-Type: application/json" -d '{"peticion":"123sdsdsdsssd"}')
    echo -e "Respuesta de la API: $RESPUESTA"
}

check_salud
#implementar