from pathlib import Path
import sqlite3
from contextlib import contextmanager
DB_RUTA = Path("app.db")

def iniciar_db():
    with sqlite3.connect(DB_RUTA) as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
        conexion.commit()
@contextmanager
def establecer_conexion():
    conexion = sqlite3.connect(DB_RUTA)
    try:
        yield conexion
    finally:
        conexion.close()

def crear_recurso(name="recurso",description=None):
    with establecer_conexion() as conexion:
        insertador = conexion.cursor()
        insertador.execute("INSERT INTO items (name, description) VALUES (?, ?)",
            (name, description))
        conexion.commit()
        id = insertador.lastrowid
        return id
