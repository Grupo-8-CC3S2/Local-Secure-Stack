#!/usr/bin/bash
set -o pipefail
set -e
set -u

umask 022 

RESPUESTA=""

check_salud(){
    echo -e "checkeo de salud"
    RESPUESTA=$(curl -s -X POST http://127.0.0.1:8000/api/salud/ -H "Content-Type: application/json" -d '{"peticion":"123sdsdsdsssd"}')
    echo -e "Respuesta de la API: $RESPUESTA"
}
PASS=true
check_salud_puro(){
    echo -e "chequeo de salud:"
    RESPUESTA=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/salud/check)
    echo -e "Respuesta $RESPUESTA\n"
    if [ "$RESPUESTA" != "200" ]; then
        PASS=false
    fi
    echo -e "PASS : $PASS"
    RESPUESTA=""
}

if ! command -v jq &> /dev/null
then
    if command -v apt-get &>/dev/null; then
        sudo apt-get update 
        sudo apt-get install -y jq
    else
        echo "no linux"
    fi
fi
    
insertar_nota(){
    echo -e "crear nota:"
    RESPUESTA=$(curl -X POST http://localhost:8000/notes/ -H "Content-Type: application/json" -d '{"titulo": "Mi nota", "contenido": "Cclearontenido de prueba"}')
    echo -e "\nrespuesta $RESPUESTA"
    ID=$(echo $RESPUESTA | jq -r '.id')
    echo -e " \nse creo la nota con id = $ID"
    RESPUESTA=""
}

listar_notas(){
    echo -e "listar notas :"
    RESPUESTA=$(curl -s http://localhost:8000/notes/)
    echo -e "$RESPUESTA" | jq .
}

listar_notas_tiempo(){
    echo -e "tiempo de listar notas:"
    FLAG=true
    INICIO=$(date +%s%3N)
    RESPUESTA=$(curl -s http://localhost:8000/notes/)
    FIN=$(date +%s%3N)
    TIEMPO=$((FIN-INICIO))
    #echo -e "$RESPUESTA" | jq .   
    echo -e "el tiempo de respuesta : $TIEMPO ms "
}


check_salud_puro
insertar_nota
listar_notas
listar_notas_tiempo
#check_salud
