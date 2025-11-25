# Proyecto 2 :  "Local Secure Stack" 
El presente proyecto ha de ejecutarse localmente ; pero se diseña de tal modo, que el conjunto de servicios que se levanten via docker-compose sea reproducible.<br>
Desde luego, la seguridad se integra en "todas las capas" , desde el uso de **imagenes minimas y tags inmutables por imagen** , pasando por la gestión de secretos mediante .env -que el daemon de docker lerá para expandir los valores de las variables al ejecutar docker-compose up- hasta el **endurecimiento de red** -que evita la exposicion de la base de datos fuera de nuestro entorno.Ademas se definen **politicas de servicio** en el docker-compose, mediante los atributos **networks, restart,deploy** ,etc dentro del bloque **services** para cada servicio de interés.      

## Contexto
Un pequeño "servicio de notas" (API + DB) que se despliega con compose y se endurece a nivel de redes , recursos y secretos

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
