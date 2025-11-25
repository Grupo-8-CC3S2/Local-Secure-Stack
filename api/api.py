from fastapi import HTTPException,status,APIRouter
from pydantic  import BaseModel,Field
from typing import Optional
from services import logica
ruta_salud = APIRouter(prefix = "/api/salud",tags=["salud"])

class SolicitudSalud(BaseModel):
    peticion:Optional[str]=Field(None )
class RespuestaSalud(BaseModel):
    status:int=Field(...)
@ruta_salud.get(
    "/",
    response_model=RespuestaSalud,
    status_code=status.HTTP_200_OK,
    summary="check salud")
def checkeo_salud()->RespuestaSalud:
    try:
        resultado = logica.verificar_salud()
        print(resultado)
        return RespuestaSalud(status=200)
    except Exception as e:
        raise HTTPException(
            status_code =500,
            detail=f"stack no saludable{e}")
        
        