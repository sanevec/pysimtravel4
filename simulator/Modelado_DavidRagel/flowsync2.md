# Control de flujo por lista rotatoria

La idea es hallar una lista suficientemente grande con dos punteros de salida y uno de entrada.
Se trata de llevar el tamaño de la cola como una recta.
Al conocer si se puede entrar a una hora se desplaza el puntero de salida.

Anillo = Road

voy a usar la tecnología de slots es la más rápida.

```python
class Slot:
    __slots__ = ('v', 't',"length") 
    def __init__(self):
        self.v = None
        self.t = 0
        self.tReal=0
        self.length = 0
```

Por cada metro por lane reservo un slot.
Hay dos punteros de salida y uno de entrada.

```python
        self.q=[Slot() for i in range(length*lanes)]
        self.outQ=0
        self.outinQ=0
        self.inQ=0
```

hay dos tiempo, salida estimada
y salida real.

para qué se utiliza 

# 23 Abril de 2025

+ control de flujo por lista rotatoria
+ resolver las ecuaciones
- dibujo gráfico. medidas: descargar raster gmail.
- bifurcaciones 
- uniones, la transmisión de nul.
- lane model
- descargar detectores

Me he quedado en que la carretera se llena.
Y no sé por qué hora preguntar.

Paso a otra tarea, resolver las ecuaciones.

¿Para resolver las ecuaciones, se necesita hallar el máximo, y añadirlo a la ecuación. No se tiene toda la información solo con medir las entradas y salidas. Hay que medir un segmento también. 

Si hay un descuadre entre las entradas y salidas añado uno al segmento correspondiente.

Y hay que prestar atención si sale un cero en el solver.

Con estos tres detalles se cuadra la función de aforo.

![](assets/17454102455232.jpg)
OSM en principio parece que no me sirve para usar el grafo.
En concreto lopez de gomara no tiene dos carriles.

# 24 de Abril de 2025

+ control de flujo por lista rotatoria
+ resolver las ecuaciones
- dibujo gráfico. medidas: descargar raster gmail.
- bifurcaciones 
- uniones, la transmisión de nul.
- lane model
- descargar detectores

Ejecuto el generador hasta la última salida.

# Viernes 25 de Abril.

Aun sigue habiendo algunos momentos donde se supera el throughput.

No consigo depurar en el entorno de desarrollo, pero esta tarea es mejor para abordarla cuando esté mas cansado.

Tienen un problema, no son capaces de detectar la fluidez del tráfico. Voy a representar la velocidad en el simulador.

Hay una relación inversa entre ocupación y velocidad, pero claro, mi espira es un promedio de la carretera, un ideal.

En la realidad espacio vs velocidad (tiempo) parado:

![](assets/17455674788412.jpg)

Se podría sacar un patrón de calle. 
En cada punto tiene una ocupación desplazada.

La dificultad está en las paraditas. 
Efecto látigo, los coches no copian al coche de adelante al instante. La velocidad está con respecto a la distancia restante.

Hay que pensar que la mayoría de los sensores se ubican tras el semáforo.
Depende de si es verde o ambar el comportamiento del conductor difiere.

La ventaja es que se puede pedir según ocupación la curva, sabiendo desde que punto arranca, y a que punto para.

Modelo sencillo:

Una sigmoide, ¿Qué verticalidad?
Posición del detector?

# Miércoles 30 Abril de 2025
x Flechas
- Donde se guarda
- Transmitir al servidor
- Cargar del servidor

Con turf se puede empezar a mirar capas, calles, de momento todo lo que se ve es gráficos de fondos, no es vectorial. 
Si usamos turf ya no habrá python. 
Se podrán medir distancias.
La simulación irá mas rápida.
No habrá solve.

- Reemplazar servidor node con python

x cargar capa de semáforos, báculos.
- información de la fase.

https://idesevilla.maps.arcgis.com/home/webmap/viewer.html?webmap=ecd6068ead12406eb28cbe34bedd0d67

Señalar 
- Postes semafóricos
- Anotaciones grupos y postes
- Grupos y postes


curl -X GET \
 'https://services.arcgis.com/.../FeatureServer/0/query?where=1=1&outFields=*&f=geojson' \
 --header 'Authorization: Bearer <tu-token>'
 
 https://idesevilla.maps.arcgis.com/home/webmap/viewer.html?webmap=ecd6068ead12406eb28cbe34bedd0d67
 
 Postes semaforicos
 
 ¿ Consultar si felix tiene exportación de postes semafóricos.
 
 al consultar pefil, veo una capa con postes semafóricos y exportar datos.
 
 Hay csv, kml, geoJson
 
 https://arcg.is/1inLeu2
 compartir da restricciones.
 
 Tipo de usuario Creator
 
 Hosted Feature Layer, vaya a Settings → Data → Export Data y marque Allow others to export to different formats.

Map Viewer Classic está obsoleto y se eliminará en el primer trimestre de 2026.

Me puedo descargar cosas de una carpeta?

2_Movilidad
Lamparas_Vehículo
GeoJSON

 https://idesevilla.maps.arcgis.com/home/item.html?id=3e3c5d9768694fc2803384c0bbf1cd34
 
 Descargable.
 
 
 Equipamiento de Regulación Semafórica (CGM de Sevilla)
 
 Se lige el elemento y se exporta.
 
 Postes semaforicos
 
 
 # Viernes 2 de mayo de 2025
 
- fuente - destino
- semáforo - bifurcación - join
- peaton, coche, tranvia 
- anchura.
 
 Vienen todos el lunes.

 