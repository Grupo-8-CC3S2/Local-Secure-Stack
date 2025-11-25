from fastapi import HTTPException,status,APIRouter
from pydantic  import BaseModel
import subprocess

ruta_salud = APIRouter(prefix = "/api/salud",tags=["salud"])

class SolicitudSalud(BaseModel):
    print()
class RespuestaSalud(BaseModel):
    print()
@ruta_salud.get(
    "/",
    response_model=RespuestaSalud,
    status_code=status.HTTP_200_OK,
    summary="check salud")
def checkeo_salud()->RespuestaSalud:
    try:
        resultado #implementar logica
    except:
        raise Exception