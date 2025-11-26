from fastapi import HTTPException,status,APIRouter
from pydantic  import BaseModel,Field
from typing import Optional
from services import logica

ruta_salud = APIRouter(prefix = "/api/salud",tags=["salud"])
ruta_notas = APIRouter(prefix = "/notes", tags=["notas"])

class SolicitudSalud(BaseModel):
    peticion:str=Field(...)

class RespuestaSalud(BaseModel):
    status:int=Field(...)

@ruta_salud.post(
    "/",
    response_model=RespuestaSalud,
    status_code=status.HTTP_200_OK,
    summary="check salud")
def checkeo_salud(request:SolicitudSalud)->RespuestaSalud:
    try:
        resultado = logica.verificar_salud(nombre=request.peticion)
        print(resultado)
        return RespuestaSalud(status=200)
    except Exception as e:
        raise HTTPException(
            status_code =500,
            detail=f"stack no saludable{e}")
                
@ruta_salud.get(
    "/check",
    summary="Healthcheck puro"
)
def healthcheck_puro():
    return {"status": 200}

class NotaEntrada(BaseModel):
    titulo:str
    contenido:str | None = None

class NotaSalida(BaseModel):
    id:int
    titulo:str
    contenido:str | None

@ruta_notas.post(
    "/",
    response_model=NotaSalida,
    status_code=status.HTTP_201_CREATED)
def crear_nota(info:NotaEntrada):
    try:
        nota_id = logica.crear_nota(info.titulo,info.contenido)
        return NotaSalida(id=nota_id, titulo=info.titulo, contenido=info.contenido)
    except Exception as e:
        raise HTTPException(
            status_code =500,
            detail=f"stack no saludable : {e}")

@ruta_notas.get(
    "/",
    response_model=list[NotaSalida],
    summary="Listando tabla notes"
)
def listar_notas():
    try:
        notas = logica.listar_notas()
        l = []
        for e in notas: 
            salida = NotaSalida(id=e[0],titulo=e[1],contenido=e[2])
            l.append(salida)
        return l
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar notas: {e}")


@ruta_notas.get(
    "/{nota_id}",
    response_model=NotaSalida,
    summary="Obtener nota por ID"
)
def obtener_una_nota(nota_id: int):
    try:
        n = logica.obtener_nota(nota_id)
        if not n:
            raise HTTPException(status_code=404, detail="Nota no encontrada")
        return NotaSalida(id=n[0], titulo=n[1], contenido=n[2])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener nota: {e}")

@ruta_notas.delete(
    "/{nota_id}",
    response_model=dict,
    summary="Eliminar nota por ID"
)
def eliminar_una_nota(nota_id: int):
    try:
        eliminado = logica.eliminar_nota(nota_id)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Nota no encontrada")
        return {"id": eliminado[0], "status": "eliminada"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar nota: {e}")