from services import data

def verificar_salud(nombre="recurso salud",descripcion=None):
    id = data.crear_recurso(nombre,descripcion)
    recurso  = {"id":id,"nombre":nombre,"descripcion":descripcion}
    return recurso