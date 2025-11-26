from services import data

def verificar_salud(nombre,descripcion=None):
    id = data.crear_recurso(nombre,descripcion)
    recurso  = {"id":id,"nombre":nombre,"descripcion":descripcion}
    return recurso

def crear_nota(titulo:str,contenido:str ):
    return data.crear_recurso(titulo,contenido)

def listar_notas():
    return data.listar_notas()
    
def obtener_nota(id):
    return data.obtener_nota(id)

def eliminar_nota(id):
    return data.eliminar_nota(id)