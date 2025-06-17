# MODELO MESO: Introduccion semántica, punteros y colas circulares

En este documento se definirá un modelo MESO de colas circulares para la simulación del tráfico de una ciudad. Simultaneamente se estándarizarán y definirán todos los elementos necesarios para su funcionamiento y se pondrán ejemplos para su funcionamiento.

## Introducción
### Necesidad
Para la simulación de tráfico de una ciudad existen tradicionalmente los modelos micro y nano. En el modelo micro, se divide la calle en cuadrículas, creando una especie de automáta celular, dónde se tiene conocimiento preciso del estado de cada coche en cada instante. Por otro lado, en el modelo macro, se toma el movimiento de los vehículos como un flujo o fluido electrico. Se presentan las siguientes ventajas e inconvenientes

| MICRO     | MACRO        |
|--------------|-------------------|
| ✅ Simula tráfico     | ✅ Rapido    |
|  ❌ Lento  | ❌ No simula tráfico   |

Por lo tanto, lo interesante nace en crear un modelo entre medio de ambos, de ahí nace la idea del Modelo MESO:

### Modelo Meso
Para este modelo, se propone una división de las calles en segmentos con dirección. Es una estructura más eficiente que la micro debido a que no sabemos el estado concreto del vehículo en medio del segmento pero si se tienen datos de la entrada y salida. De todas formas, el estado intermedio se puede reconstruir después de la simulación si fuera necesario.

## Definiciones
**Vehículo**: se define la longitud del vehículo como su tamaño más la distancia de seguridad trasera. Esta distancia cambia según la velocidad. En nuestro caso, solo nos interesa el mínimo y la tomaremos como 1m.

**Segmento de carretera (road)**: se pueden ver como aristas dirigidas de un grafo. Cuentan con los siguientes elementos:
- Emisor (Source): comienzo de la calle, los vehículos entraran por este lado.
- Objetivo (Target): salida de la calle, los vehículos salen por este lado. 
- Longitud (length): en nuestro caso en metros.
- Velocidad máxima permitida (velocity). 
- 



## Punteros


## Modelo cruce