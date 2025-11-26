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