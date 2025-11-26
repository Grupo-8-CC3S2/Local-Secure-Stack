from fastapi import FastAPI
import uvicorn

from api import ruta_salud
from services.data import iniciar_db

def crear_app_fastapi()->FastAPI:
    app = FastAPI()
    app.include_router(ruta_salud)
    @app.on_event("startup")
    def prepara_inicio():
        print("antes de que inicie")
        iniciar_db()
    @app.on_event("shutdown")
    def prepara_finalizacion():
        print("limpieza antes de la detencion")
    return app
app = crear_app_fastapi()

if __name__=='__main__':
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)