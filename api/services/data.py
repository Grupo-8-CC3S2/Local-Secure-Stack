# Módulo de acceso a datos para PostgreSQL

import os
import psycopg2
from contextlib import contextmanager
from typing import Optional, Dict

def get_db_config() -> Dict[str, str]: 
    return {
        'host': os.getenv('DB_HOST', 'db'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'port': os.getenv('DB_PORT', '5432')
    }

def iniciar_db() -> None: 
    try:
        config = get_db_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"Conexión exitosa a PostgreSQL")
                print(f"Base de datos: {config['database']}")
                print(f"Versión: {version[0][:50]}...")
    except psycopg2.OperationalError as e:
        print(f"Error conectando a PostgreSQL: {e}")
        print("Verifica que el contenedor 'db' está corriendo")
        raise
    except Exception as e:
        print(f"Error inesperado: {e}")
        raise

@contextmanager
def establecer_conexion(): 
    config = get_db_config()
    conexion = psycopg2.connect(**config)
    try:
        yield conexion
    finally:
        conexion.close()
# modificacion sin documentacion ? , se otorga contextmanager tambien al cursor __exit__()
def crear_recurso(name: str, description: Optional[str] = None) -> int: 
    with establecer_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO notes (title, content) 
                VALUES (%s, %s) 
                RETURNING id
                """,
                (name, description or "")
            )
            id_insertado = cursor.fetchone()[0]
            conexion.commit()
            print(f"- Nota creada con ID: {id_insertado}")
            return id_insertado

def listar_notas():
    with establecer_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM notes;")
        return cursor.fetchall()

def obtener_nota(id):
    with establecer_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM notes WHERE id=%s;", (id,))
        return cursor.fetchone()

def eliminar_nota(id):
    with establecer_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM notes WHERE id=%s RETURNING id;", (id,))
        eliminado = cursor.fetchone()
        conexion.commit()
        return eliminado