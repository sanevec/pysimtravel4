 # THREE LOGIC DEVS

 ## DEVS 
Discrete Event System Specification (Especificación de Sistemas de Eventos Discretos).
Referencia a [DEVS](https://en.wikipedia.org/wiki/DEVS)

### Formalismo de Atomic DEVS

El modelo DEVS atómico se define como una tupla de 7 elementos como sigue:

**M = ⟨X, Y, S, s₀, ta, δext, δint, λ⟩**

- **X** ⇒ eventos de entrada (input events)
- **Y** ⇒ eventos de salida (output events)
- **S** ⇒ conjunto de estados secuanciales (set of sequential states) 
- **s₀ ∈ S** ⇒ estado inicial
- **ta: S → T⁺** ⇒ función de avance de tiempo  ⇒ define la vida de un estado  
- **δext: Q × X → S** ⇒ funcion de transicion external (external transition function)  
  - como un evento de entrada cambia el estado   
  - Q = { (s, te) | s ∈ S, te ∈ (ℝ⁺ ∩ [0, ta(s)]) }  
    - te: tiempo que ha trancurrido desde el ultimo evento   
- **δint: S → S** ⇒ funcion interna (internal function) 
  - como un estado cambia internamente (cuando la vida de un estado llega a su fin)  
- **λ: S → Y^Φ**  
  - (Y⁰: Y, Y⁰ ⊆ Y, ∅ ≠ Y) ⇒ como un estado genera una salida 



## Modelo para tráfico
Se desea generar un modelo donde cada carretera sea modular y pueda llevar su tiempo independiente al resto, pero pueda coordinarse mediante eventos con las carreteras colindantes para lograr pasar los vehiculos de carretera en carretera.

### Definicion de propiedades
Se van a tomar secciones de la carretera, preferiblemente segmentada por semáforos, interseccione o bifurcaciones. Cada carretera posee unas propiedades estáticas cómo es la velocidad máxima, el largo de la calle. De las cuales se puede calcular la ocupación máxima de la calle y el minimo tiempo para recorrer la calle. 

Por otro lado, se tienen unas propiedades dinámicas que nacen naturalmente del movimiento de los coches en la carretera. Se tomará una cola circular de tamaño fijo para incluir la posición del vehículo y su velocidad, acompañado de los punteros de cabeza y cola. Con relacion a los tiempos se usará:
- **global_t**: tiempo global de la calle
- **max_global_t**: tiempo global máximo de la calle, se toma como el tiempo necesario del primer vehículo en llegar al final de la carretera
- **prev_global_t**: almacenaje del tiempo global anterior para calcular cuanto se tienen que mover los vehículos.

Por último, se han definido unos buffers en la carretera para poder seguir con el formalismo del DEVS.

### Modelado
#### Ideas previas
Tomemos una carretera i, la anterior y la siguiente y pensemos que valores se necesitan transmitir de una a otra para lograr mandar y recibir vehiculos.
- Necesito, siendo la carretera i, saber el tiempo en el que la carretera i-1 tendrá un coche al final de la carretera. Asi podremos calcular el tiempo que me debo mover para sincronizarme, en este caso será el tiempo minimo entre el que recibo y el mio propio para llegar al final.
- Para poder mandar un coche, siendo la carretera i, necesito recibir el tiempo global de la carretera i+1 y su estado (si puedo o no mandar coche, por ahora si la calle está llena o no).
- Una vez todo lo anterior, puedo mandar el coche a la siguiente carretera.

Cómo se puede ver, cada envio de mensajes, necesita la información anterior. Cómo en el DEVS sólo hay un envio y una recepión. Se va a formalizar el modelo de tráfico como tres DEVS que van procediendo uno detrás del otro.

### Modelado.

#### **DEVS 1:**
Este se encargará de mover los coches dentro de una carretera. Para ello, se tienen los siguientes pasos:
- **Paso 3**: Envia a la carretera siguiente el tiempo máximo que se pueden desplazar los coches en la carretera (max_global_t) y el tiempo global actual (global_t). Este tiempo ya se ha calculado previamente.
- **Paso 5**: Se procesan los datos recibidos de la carretera anterior y se calcula el nuevo global_t 
- **Paso 6**: Se mueven los vehículos la distancia que han debido de desplazarse en ese rango de tiempo. Se actualiza la variable prev_global_t


#### **DEVS 2:**
Es el encargado de determinar si se pueden mandar o no coches a la siguiente calle debido a los movimientos del DEVS anterior. Tiene los siguientes pasos:
- **Paso 3**: Envia a la carretera anterior el tiempo global actual y si puede mandar coche, es decir si no está ocupada la calle.
- **Paso 5 y 6**: Se combinan los pasos debido a la simplicidad. Con los datos recibidos del estado de la carretera siguiente, se evalua si el primer vehículo de la cola cumple las condiciones para realizar el cambio de carrtera. Si es así, actualiza la variable "send_car" a True.


#### **DEVS 3:***
Tramitará el envio y recepción de vehículos. Se han juntado todos los pasos debido a la simplicidad. En este DEVS también se incluye la lógica para incluir coches y borralos.










 