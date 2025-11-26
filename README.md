# Proyecto 2 :  "Local Secure Stack" 
El presente proyecto ha de ejecutarse localmente ; pero se diseña de tal modo, que el conjunto de servicios que se levanten via docker-compose sea reproducible.<br>
Desde luego, la seguridad se integra en "todas las capas" , desde el uso de **imagenes minimas y tags inmutables por imagen** , pasando por la gestión de secretos mediante .env -que el daemon de docker leerá para expandir los valores de las variables al ejecutar docker-compose up- hasta el **endurecimiento de red** -que evita la exposicion de la base de datos fuera de nuestro entorno.Ademas se definen **politicas de servicio** en el docker-compose, mediante los atributos **networks, restart,deploy** ,etc dentro del bloque **services** para cada servicio de interés.      

## Contexto
Un pequeño "servicio de notas" (API + DB) que se despliega con compose y se endurece a nivel de redes , recursos y secretos.

## Sprint 1 : API PYTHON + VISION + DEFINITION OF DONE
Antes que nada veamos en que consiste una API
```bash
Cliente (curl, Postman)
┌─────────────────────────┐
│   Solicita/Consume API  │
└─────────────────────────┘
            ▲
            │
            ▼
┌───────────────────────────────────────────────┐
│                     API                       │
│ ┌───────────────┐  ┌───────────────┐          │
│ │ Endpoint POST │  │ Endpoint GET  │          │
│ │ /api/items/   │  │ /api/items/   │          │
│ │ ┌───────────┐ │  │ ┌───────────┐ │          │
│ │ │ Modelos   │ │  │ │ Modelos   │ │          │
│ │ │ ItemIn/Out│ │  │ │ ItemOut   │ │          │
│ │ │ Códigos   │ │  │ │ Códigos   │ │          │
│ │ │ 201,400   │ │  │ │ 200,500   │ │          │
│ │ └───────────┘ │  │ └───────────┘ │          │
│ └───────┬───────┘  └───────┬───────┘          │
└───────────────────────────────────────────────┘
                ▲
                │
                ▼
          Lógica de negocio
          (business_logic)
```
Como bien indica el nombre es la interfaz de programacion de aplicaciones, la forma como interactuamos con el sistema. Para profundizar revise microservice/api/routes.py en  el labs/Laboratorio10 del presente curso. 

Siguiendo la estructura recomendada para el repositorio,se crean las sucarpetas api y scripts. Dentro de api implementamos la interfaz de programacion de aplicacion.

Se requiere **fastapi** y sus modulos APIRoute -para agrupar endpoints de acuerdo a una logica comun- y status que tiene las variables cuyos valores son los codigos de estado de nuestras peticiones. Del mismo modo **pydantic** que agilizara la verificacion de los campos de la solicitud, caso contrario se usaria una verificaicion manual via operadores condicionales. Esto mediante dos clases que definen el formato de las entradas y salidas **SolicitudSalud** y **RespuestaSalud** . En tanto que el metodo **checkeo_salud** posee el decorador @ruta_salud, quien permite capturar info para el log y ya en el cuerpo del metodo , ejecutamos los .sh respectivos.

Para main.py , donde se crea la instancia FastAPI , asociando la ruta_salud visto anteiormente,para agregar dos metodos con naturalezas definidas mediante etiquetas **on_event(startup)** y **on_event(shutdown)**, se encargan de preparar el arranque y la terminacion respectivamente.      
Y desde luego en **main**, corremos uvicorn quien maneja la concurrencia a nivel de red.
**uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)** 

Ahora se define el cuerpo de los "formatos" de solicitud y respuesta que llegaran hacia nuestra API , para **SolicitudSalud** definimos el campo peticion que será de un tipo str pero opcional (el usuario no esta obligado a pasar valores via **curl -d**), a este campo se asigna la salida de Field(valor por defecto, info adicional..). Se hace otro tanto para **RespuestaSalud**la respuesta proveniente del modulo del recurso .sh, en este caso el campo status es de tipo int(ej 200) y es **...** obligatorio. 

### test-stack
En este punto se tiene la api , con los modelos que verifican las respuesta y un main.py que crea una instancia appifast , ahora se implementa test-stack , archivo en el cual se realiza la solicitud. Precisemos antes,que es stack , este termino (en nuestro contexto) hace referencia a todas las tecnologias que nos permiten realizar una peticion , procesarla, recibir la respuesta, validarla y enviar la respuesta al cliente. Entonces esto se realiza en test-check ; de modo que si el endpoint responde correctamente, consideraremos que el stack es saludable.
Pero la ejecucion es transparente, una sencilla peticion GET via cliente curl, recibe por respuesta el codigo de estado 200.Sin embargo la adicion de funcionalidad hecha a api.py  y la creacion de services/data.py donde se crea el recurso , merecen atencion especial.Asimismo services/logica.py quien crea el recurso llamando a la base de datos.

Desde api.py llamamos a verificar.salud() detro de un bloque try, de modo que nos aseguramos de obtener el resultado deseado, devolviendo este segun el modelo **RespuestaSalud** defino antes.Caso contrario se captura la exception tipo **HTTPException**. La invocacion  a **verificar_salud()** nos conduce al modulo logica , este metodo su vez llama a **crear_recurso** de la base de datos(modulo data en terminos prácticos) , una vez creado el recurso  se construye la respuesta que sera enviado a nuestra API. Ahora seguiendo el flujo de invocaciones profundicemos en el modulo data. Este usa sqlite , definimos la ruta para la data, y 3 metodos principales, iniciar_db(que luego se invocara desde main.py) establece la conexion con el motor Sqlite de justamente modulo python  sqlite3 **with sqlite3.connect()** luego la data creada se guardara en la ruta DB_RUTA, se envia y actualiza **execute , commit**.

Para posteriores actualizaciones definimos el metodo **establecer_conexion()**, quien posee una naturaleza identica pero esta vez para la insercion de nuevos item, en este punto cabe resaltar algo de la sintaxis "pythonica" que en ocasiones resulta nada pythonica, en particular este bloque requiere atencion especial
```bash
@contextmanager
def establecer_conexion():
    conexion = sqlite3.connect(DB_RUTA)
    try:
        yield conexion
    finally:
        conexion.close()
```
Tenemos que **yield** modifica una funcion normal , reemplazando el clasico **return** de modo que no devuelva un valor simplemente, sino que se convierta en un generador. Osea para añadir info a la data que esta en app.db (DB_DATA), sin embargo este metodo sera llamado desde **crear_recurso** en su bloque **with**, quien espera manejar un **context_manager**, del mismo modo que se manejaria un archivo via **with open("archivo.txt") as f**. Esto implica poder salir de un contexto o entrar en este contexto(archivo) via **__enter__() , __exit__()** metodos que un generador **yield** no  tiene, luego la solucion practica es hacerle context manager, es decir otorgarle esas funciones mediante **@contextmanager**.

Hecho esto el flujo continua, en **crear_recurso** se accede al motor sqlite que grabara en la ruta, se inserta mediante **conexion.cursor()** y devolvemos el id hacia logica que a su vez devolvera la estructura construida hacia api, quien sera en ultima instancia quien responda al cliente.
 
Un esquema hecho en caliente del flujo (se corrgira adelante)
```bash
 CLIENTE
   |
   | GET /api/salud/
   v
───────────────────────────────────────────────────────
 API  (api.py)
───────────────────────────────────────────────────────
 checkeo_salud()
        |
        | → llama a
        v
───────────────────────────────────────────────────────
 LÓGICA  (services/logica.py)
───────────────────────────────────────────────────────
 verificar_salud()
        |
        | → usa base de datos
        v
───────────────────────────────────────────────────────
 DATA (services/data_access.py)
───────────────────────────────────────────────────────
 establecer_conexion()        ← context manager
 ejecutar_consulta()          ← ejemplo
        |
        | → SELECT 1 FROM items;
        v
<--------- resultado OK   ----------------------------->
        |
───────────────────────────────────────────────────────
  LÓGICA
───────────────────────────────────────────────────────
 verificar_salud() retorna OK
        |
        v
───────────────────────────────────────────────────────
  API
───────────────────────────────────────────────────────
 checkeo_salud() → RespuestaSalud(status=200)
        |
        v
 CLIENTE recibe:
 { "status": 200 }

```
La consulta se realiza via cliente curl al dominio:puerto/endpoint de salud
```bash
esau@DESKTOP-A3RPEKP:~/Local-Secure-Stack$ curl -X GET http://127.0.0.1:8000/api/salud/
{"status":200}
```
Esta respuesta es la que se construye en **return RespuestaSalud(status=200)** en el endpoint de api.py precisamente

Ahora lo que se precisa es un .sh para la ejecucion automatizada del chequeo de salud
una funcion sencilla con un comando de sustitucion que ejecuta **curl** ,la salida es asignada a la variable bash **RESPUESTA**
```bash
curl -s -X POST http://127.0.0.1:8000/api/salud/ -H "Content-Type: application/json" -d '{"peticion":"123"}'
```
En apy.py se ha definido el modelo para las solicitudes , mediante **SolicitudSalud(BaseModel)** se espera un diccionario en formato JSON **{"peticion":"123sdsdsdd"}** y es el valor de **peticion** el insumo para la creacion del nombre de nuestro nuevo recurso via **logica.verificar_salud(nombre=request.peticion)** donde request es el argumento para la funcion **checkeo_salud**mediante **checkeo_salud(request:SolicitudSalud)->RespuestaSalud:**. Entonces es preciso que el valor de esa clave peticion sea distinto , de modo que 
```bash
conexion.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
```
Cree recursos con nombres distintos , tal como se espera.Esto al ser invocados desde crear_recurso mediante **insertador.execute("INSERT INTO items (name, description) VALUES (?, ?)",(name, description))**.
La ejecucion  del .sh se realiza del modo siguiente:
```bash
esau@DESKTOP-A3RPEKP:~/Local-Secure-Stack$ bash scripts/test-stack.sh
checkeo de salud
Respuesta de la API: {"status":200}
```


## Sprint 2: API COMPLETA 
Tanto el arbol de archivos como data.py sufrieron modificaciones, que sin ser drasticas , son considerables (cosas de trabajar en equipo) . Sin embargo se obtuvo una migracion exitosa de sqlite a Postgres , asimismo se logro integrar api a docker-compose, esto es , se logro contenerizar nuestra API. Detallemos brevemente las modificaciones substanciales.<br>
En data.py se obtienen las variables desde docker-compose, aquellas con las cuales tendremos acceso a la base de datos, desde luego luego de crear el **.env** en el directorio de docker-compose; iniciar_db() se ajusta a la logica postgres , ahora se usa **psycopg2** para establecer la conexion. Asimismo **establecer_conexion()** se ajusta a la misma logica , en particular el uso de ** config , este diccionario representa los vlaores de las variables de entorno con cuyas claves se pedira acceso a la tabla postgres, entonces  
```bash
 psycopg2.connect(**config) 
```
valida y obtiene acceso . **Crear_recurso()** sufre una mejora respecto al anterior codigo  se otorga a cursor el poder ser context manager(tener un __exit__) de modo que pueda finalizarse si hay algun error. La insercion de un nuevo elemento sigue la logica anterior.

Detallado ello, precisemos lo abarcado en el sprint 2(hasta el momento) , se completa el CRUD de notas con la adicion de una nueva ruta **ruta_notas = APIRouter(/notes,...)** y sus endpoints asociados, **@ruta_notas.post("/") def crear_nota()** se recibe la peticion del cliente que debe seguir formato definido por el modelo pydantic (schema). Luego , el flujo es conocido, la peticion viaja a logica.py y finalmente a data.py ,donde se ejecuta **crear_recurso** con el establecimiento de la conexion y la escritura de la nueva linea en la tabla. Una vez obtenido la respuesta se devuelve el recurso al cliente, otra vez, en el formato **NotaSalida** modelo pydantic definido. Listar_notas, obtener_una_nota y eliminar_una_nota siguen este estilo.
La ejecucion se realiza del modo siguiente
```bash
pip install -r requirements.txt
lsof -i :8080
#matar el proceso de ser necesario
#kill -9 <PID>
docker compose up --build
#crear_nota
curl -X POST http://localhost:8000/notes/ -H "Content-Type: application/json" -d '{"titulo": "Mi nota", "contenido": "Cclearontenido de prueba"}'
#listar notas
curl http://localhost:8000/notes/
#eliminar una nota
curl -X DELETE http://localhost:8000/notes/1
```
