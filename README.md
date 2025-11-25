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