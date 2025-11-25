# Proyecto 2 :  "Local Secure Stack" 
El presente proyecto ha de ejecutarse localmente ; pero se diseña de tal modo, que el conjunto de servicios que se levanten via docker-compose sea reproducible.<br>
Desde luego, la seguridad se integra en "todas las capas" , desde el uso de **imagenes minimas y tags inmutables por imagen** , pasando por la gestión de secretos mediante .env -que el daemon de docker lerá para expandir los valores de las variables al ejecutar docker-compose up- hasta el **endurecimiento de red** -que evita la exposicion de la base de datos fuera de nuestro entorno.Ademas se definen **politicas de servicio** en el docker-compose, mediante los atributos **networks, restart,deploy** ,etc dentro del bloque **services** para cada servicio de interés.      

## Contexto
Un pequeño "servicio de notas" (API + DB) que se despliega con compose y se endurece a nivel de redes , recursos y secretos
