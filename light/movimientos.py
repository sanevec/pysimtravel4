#from glorietaRepublicaDominicana import data
#from glorietaDelIndio import data 
from prueba import data 
#######################################################################

puntos=data['puntos']
lineas=data['lineas']

# Halla el marco
import pygame
minX=10000000
minY=10000000
maxX=-10000000
maxY=-10000000
for i, feature in enumerate(puntos):
    x=feature["geometry"]["coordinates"][0]
    y=feature["geometry"]["coordinates"][1]
    if x<minX:
        minX=x
    if x>maxX:
        maxX=x
    if y<minY:
        minY=y
    if y>maxY:
        maxY=y
for i, feature in enumerate(lineas):
    for coord in feature["geometry"]["coordinates"]:
        if coord[0]<minX:
            minX=coord[0]
        if coord[0]>maxX:
            maxX=coord[0]
        if coord[1]<minY:
            minY=coord[1]
        if coord[1]>maxY:
            maxY=coord[1]

print("Marco:",minX,minY,maxX,maxY)
print()


import time


def identifica(lista, *listas):
    for i, feature in enumerate(lista):
        feature['id'] = i
        for l in listas:
            feature[l] = []

identifica(puntos,  "linea0", "linea2")
identifica(lineas,  "punto0", "punto2")

class Display:
    def __init__(self,c):
        import pygame
        import sys

        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Semáforos")

        def dibujar_fase():
            screen.fill((255, 255, 255))
            for i, feature in enumerate(lineas):
                color=c.linea2color(i)
                # ¿Pertenece a esta fase?
                previus = None
                for coord in feature["geometry"]["coordinates"]:
                    x = int((coord[0] - minX) / (maxX - minX) * 800)
                    y = int((coord[1] - minY) / (maxY - minY) * 600)
                    y = 600 - y  # invertir Y
                    if previus is not None:
                        pygame.draw.line(screen, color, previus, (x, y), 2)
                    previus = (x, y)
            pygame.display.flip()

        dibujar_fase()

        # Bucle de eventos
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    c.cambio()
                    dibujar_fase()

        pygame.quit()
        sys.exit()

def compare(punto,linea,indice):
    if punto["geometry"]["coordinates"]==linea["geometry"]["coordinates"][indice]:
        if indice==0:
            punto["linea0"].append(linea)
            linea["punto0"].append(punto)
        else:
            punto["linea2"].append(linea)
            linea["punto2"].append(punto)

# si tienen lineas y puntos el mismo origen los presenta.
for i, feature in enumerate(puntos):
    for j, feature2 in enumerate(lineas):
        # se compara el punto con el comienzo o fin de la linea
        compare(feature, feature2,0 )
        compare(feature, feature2,-1)

def segments_intersect_strict(p1, p2, q1, q2):
    def orientation(a, b, c):
        val = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
        if val == 0:
            return 0
        return 1 if val > 0 else 2

    def on_segment(a, b, c):
        return min(a[0], c[0]) <= b[0] <= max(a[0], c[0]) and min(a[1], c[1]) <= b[1] <= max(a[1], c[1])

    # Rechazar si comparten exactamente un extremo
    shared = {tuple(p1), tuple(p2)} & {tuple(q1), tuple(q2)}
    if len(shared) == 1:
        return False

    o1 = orientation(p1, p2, q1)
    o2 = orientation(p1, p2, q2)
    o3 = orientation(q1, q2, p1)
    o4 = orientation(q1, q2, p2)

    if o1 != o2 and o3 != o4:
        return True

    if o1 == 0 and on_segment(p1, q1, p2): return True
    if o2 == 0 and on_segment(p1, q2, p2): return True
    if o3 == 0 and on_segment(q1, p1, q2): return True
    if o4 == 0 and on_segment(q1, p2, q2): return True

    return False

def segments_intersect(p1, p2, q1, q2):
    def orientation(a, b, c):
        val = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
        if val == 0:
            return 0  # colineales
        return 1 if val > 0 else 2  # horario o antihorario

    def on_segment(a, b, c):
        return min(a[0], c[0]) <= b[0] <= max(a[0], c[0]) and min(a[1], c[1]) <= b[1] <= max(a[1], c[1])

    o1 = orientation(p1, p2, q1)
    o2 = orientation(p1, p2, q2)
    o3 = orientation(q1, q2, p1)
    o4 = orientation(q1, q2, p2)

    # Caso general
    if o1 != o2 and o3 != o4:
        return True

    # Casos especiales (colineales y dentro del segmento)
    if o1 == 0 and on_segment(p1, q1, p2): return True
    if o2 == 0 and on_segment(p1, q2, p2): return True
    if o3 == 0 and on_segment(q1, p1, q2): return True
    if o4 == 0 and on_segment(q1, p2, q2): return True

    return False


# incompatibilidades
incompatibles = {}

# Identifica segmentos que se solapan
for i, linea1 in enumerate(lineas):
    coordenadas1=linea1["geometry"]["coordinates"]
    for j in range(i+1, len(lineas)):
        linea2=lineas[j]
        coordenadas2=linea2["geometry"]["coordinates"]
        for k in range(len(coordenadas1)-1):
            for l in range(len(coordenadas2)-1):
                p1 = coordenadas1[k]
                p2 = coordenadas1[k + 1]
                q1 = coordenadas2[l]
                q2 = coordenadas2[l + 1]
                if segments_intersect_strict(p1, p2, q1, q2):
                    # imprime vectores normalizados
                    if i not in incompatibles:
                        incompatibles[i] = []
                    if j not in incompatibles:
                        incompatibles[j] = []
                    incompatibles[i].append(j)
                    incompatibles[j].append(i) 
            
def filtrarPuntosTipo(tipo):
    semaforos = []
    for i, feature in enumerate(puntos):
        if feature["properties"].get("tipo")==None:
             continue
        if feature["properties"]["tipo"] == tipo:
            semaforos.append(feature)
    return semaforos

semaforos=filtrarPuntosTipo("Semáforo")
    
print("Permutaciones:",2**len(semaforos))
print()

def filtrarPuntosDireccion(direccion):
    semaforos = []
    for i, feature in enumerate(puntos):
        if feature["properties"].get("tipo")==None:
            continue
        if feature["properties"]["direccion"] ==direccion:
            semaforos.append(feature)
    return semaforos

origens=filtrarPuntosDireccion("Origen")
# Halla semáforos incompatibles
# empieza con bidirecionales y origen.


# aquí es donde se halla la incompatibilidad y tenemos que programarlo mejor
for o in origens:
    # A*
    vecinos=[o]
    visitados=set()
    visitados.add(o["id"])
    lineaRecorrida=set()
    lineaIncompatible=set()
    while len(vecinos)>0:
        v=vecinos.pop(0)
        for l in v["linea0"]: #v["linea2"]: #
            # desdoblar aclarar.
            if l["id"] in lineaRecorrida:
                continue
            lineaRecorrida.add(l["id"])
            if not incompatibles.get(l["id"]) is None:
                for l2 in incompatibles[l["id"]]:
                    lineaIncompatible.add(l2)
            for p2 in l["punto2"]:
                # si no es semáforo
                if p2["properties"]["tipo"] != "Semáforo":
                    if p2["id"] not in visitados:
                        visitados.add(p2["id"])
                        vecinos.append(p2)
    o["lineaIncompatible"]=lineaIncompatible
    o["lineaRecorrida"]=lineaRecorrida

# es fácil hallar las incompatibilidades:

class ControladorIncompatibilidad:
    def __init__(self):
        self.voy=0

    def cambio(self):
        self.voy+=1
        if self.voy>=len(origens):
            self.voy=0
    def linea2color(self,linea):
        o=origens[self.voy]
        color=(128, 128, 128)
        if linea in o["lineaIncompatible"]:
            color= (255,0,0)
        if linea in o["lineaRecorrida"]:
            color = (0,255,0)
        return color

#Display(ControladorIncompatibilidad())

import random

# Si detecta violación lo cambia de fase
class Detector:
    def __init__(self):
        self.lineaRecorrida=set()
        self.lineaIncompatible=set()

    def add(self,candidato):
        if len(self.lineaRecorrida & candidato["lineaIncompatible"])==0 and len(self.lineaIncompatible & candidato["lineaRecorrida"])==0:
            self.lineaRecorrida=self.lineaRecorrida | candidato["lineaRecorrida"]
            self.lineaIncompatible=self.lineaIncompatible | candidato["lineaIncompatible"]
            return True
        else:
            return False
        

fases=2
# cada semáforo a un número de fase
intento=0
maximo=0
while True:
    enFase=[]
    for i, semaforo in enumerate(semaforos):
        enFase.append(random.randint(0,fases-1))
    detectores=[Detector() for i in range(fases)]

    # Hasta que no puede ser asignado o hasta que termina
    exito0=True
    for s, semaforo in enumerate(semaforos):
        exito=False
        for i in range(fases):
            en=(enFase[s]+i)%fases
            if detectores[en].add(semaforo):
                enFase[s]=en
                exito=True
                break
        if not exito:
            exito0=False
            break
    if exito0:
        print("Asignación de semáforos exitosa")
        break
    else:
        print("Acierto",s/len(semaforos))
        maximo=max(maximo,s/len(semaforos))
    intento+=1
    if intento%1000==0:
        print("Intentos:",intento,"Máximo:",maximo)
    # else:
    #     print("No se puede asignar semáforo")


# dibuja en pygame
coloresFase=[(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)] 


class Controlador:
    def __init__(self):
        self.fase_actual = 0

    def linea2color(self,linea):
        if linea not in detectores[self.fase_actual].lineaRecorrida:
            color= (128, 128, 128)
        else:
            color = coloresFase[self.fase_actual]
        return color

    def cambio(self):
        total_fases = len(detectores)
        self.fase_actual = (self.fase_actual + 1) % total_fases


Display(Controlador())


# def permutaciones(isemaforo,semaforosAbiertos,lineaRecorrida,lineaIncompatible):
#     if isemaforo==len(semaforos):
#         yield (semaforosAbiertos, lineaRecorrida, lineaIncompatible)
#         return

#     candidato=semaforos[isemaforo]
#     if len(lineaRecorrida & candidato["lineaIncompatible"])==0 and len(lineaIncompatible & candidato["lineaRecorrida"])==0:
#         semaforosAbiertos2=semaforosAbiertos+[1]
#         lineaRecorrida2=lineaRecorrida | candidato["lineaRecorrida"]
#         lineaIncompatible2=lineaIncompatible | candidato["lineaIncompatible"]
#         for a,b,c in permutaciones(isemaforo+1,semaforosAbiertos2,lineaRecorrida2,lineaIncompatible2):
#             yield (a,b,c)
#     for a,b,c in permutaciones(isemaforo+1,semaforosAbiertos+[0],lineaRecorrida,lineaIncompatible):
#         yield (a,b,c)

# n=0
# start=time.time()
# for semaforosAbiertos, lineaRecorrida, lineaIncompatible in permutaciones(0,[],set(),set()):
#     n+=1
#     if n%10000==0:
#         t=time.time()-start
#         print(n)
#         print("Rendimiento:",n/t)

    # print("Semáforos abiertos:",semaforosAbiertos)
    # print("Lineas recorridas:", end=" ")
    # for l in lineaRecorrida:
    #     print(l, end=" ")
    # print()
    # print("Lineas incompatibles:",end=" ")
    # for l in lineaIncompatible:
    #     print(l, end=" ")
    # print()
