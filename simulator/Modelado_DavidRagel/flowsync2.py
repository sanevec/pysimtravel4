import pandas as pd
import sympy as sp
import numpy as np
import csv
import os



class Slot:
    __slots__ = ('v', 't','tReal',"length") 
    def __init__(self):
        self.v = None
        self.t = 0
        self.tReal=0
        self.length = 0

class Road:
    def __init__(self, length, velocity, name=None,lanes=1):
        self.name = name
        self.lanes = lanes
        self.length = length
        
        self.q=[Slot() for i in range(length*lanes)]
        self.outQ=0
        self.outinQ=0
        self.inQ=0
        self.lenQueue=0
        
        self.velocity = velocity
        self.lastVelocity = velocity
        self.freeInputTime=0
        self.freeOutputTime=0

        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
        filename = self.name + ".csv"
        self.filename = os.path.join(script_dir, filename) 

        



    def safetyDistance(self):
        med=4.2
        #s= (med+max(0.75, (self.velocity-self.lastVelocity)/50*(28-med)))/med
        #return s
        return (med+2)/med

    def velocityms(self):
        # Convert velocity from km/h o m/s
        return self.velocity / 3.6
    
    def freeInputTimeAll(self):
        i=self.outinQ
        while True:
            queueLength=self.q[self.inQ].length-self.q[i].length
            f= queueLength*self.safetyDistance()>self.length
            if not f or i==self.outQ:
                r=self.q[i].tReal
                return r
            i+=1
            if i>=len(self.q):
                i=0

    def full(self,t):
        while self.q[self.outinQ].tReal<t:
            if self.outinQ==self.outQ:
                break
            self.outinQ+=1
            if self.outinQ>=len(self.q):
                self.outinQ=0
        
        queueLength=self.q[self.inQ].length-self.q[self.outinQ].length
        f= queueLength*self.safetyDistance()>self.length
        return f
    
    def push(self, time, vehicle=None):
        if vehicle!=None and self.full(time):
            raise Exception("Queue is full")
        if time < self.freeInputTime:
            time=self.freeInputTime
        # Hay que hallar a que hora se admite una nueva entrada
        # Es el tiempo de entrada a la velocidad de la via
        # v= e/t => t=e/v

        if vehicle!=None:
            vehicle.log.append((time,"push",self.name))
            self.add_to_road_csv(vehicle.car_id, time, "push")
            #self.freeInputTime=time+vehicle.totalDistance(self.velocity)/self.velocityms()
            self.freeInputTime=time+(vehicle.length*self.safetyDistance())/self.velocityms()
            # A que hora sale cabeza y cola 

            en=self.q[self.inQ]
            en.t=time+self.length/self.velocityms()
            en.v=vehicle
            self.lenQueue+=1
            self.inQ+=1
            if self.inQ>=len(self.q):
                self.inQ=0
            self.q[self.inQ].length=en.length+vehicle.length
            # v= e/t => t=e/v    
        else:
            self.freeInputTime=time
        self.freeOutputTime=self.freeInputTime+self.length/self.velocityms()
        
    def get(self, time, time_to=None):
        if self.lenQueue==0:
            yield (max(self.freeOutputTime,time), None)
            return
        # puede ocurrir tres cosas: delante, en medio, detrás.
        waiting=0
        if self.q[self.outQ].t < time:
            waiting=time-self.q[self.outQ].t

       
        while True:
            if self.lenQueue==0:
                yield (self.freeOutputTime+waiting, None)
                return
            q=self.q[self.outQ]
            if time_to==None or q.t+waiting <time_to:
                q.tReal=q.t+waiting
                self.outQ+=1
                if self.outQ>=len(self.q):
                    self.outQ = 0
                self.lenQueue-=1
                
                self.lastVelocity = 0.8*self.lastVelocity+0.2*self.length/(q.tReal-q.v.log[-1][0])*3.6
                #print(self.name,"lastVelocity",self.lastVelocity)
                q.v.log.append((q.tReal,"get",self.name))
                self.add_to_road_csv(q.v.car_id, q.tReal, "get")
                #self.queueLength-=q[1].length
                yield (q.tReal,q.v)
                if self.outQ==self.inQ:
                    break
            else:
                break
    def add_to_road_csv(self, id_car, time, action):
        
        file_exists = os.path.isfile(self.filename)

        # Open the CSV file in append mode
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write the header only if the file doesn't exist yet
            if not file_exists:
                writer.writerow(['id_car', 'time', 'action', 'inQ', 'outQ', 'outinQ'])

            # Write the new row
            writer.writerow([id_car, time, action, self.inQ, self.outQ, self.outinQ])

class Phase:
    aux = 0
    def __init__(self,intersection,split ):
        self.intersection = intersection
        self.split = split
        self.io=[]

    def open(self, input, output,distance,velocity):
        self.io.append((input, output, Road(distance, velocity,self.intersection.name + str(Phase.aux))))
        Phase.aux += 1


class Intersection:
    def __init__(self, inputs, outputs,phases, name=None):
        self.name = name
        self.input = inputs
        self.output = outputs
        self.phases = [Phase(self,0.5) for _ in range(phases)]
        self.offset = 0
        self.cycle = 90
        self.t = 0

    def run(self):
        second_cicle=(self.t - self.offset)% self.cycle
        phase=second_cicle/self.cycle

        split=0
        can0=True
        for p in self.phases:
            change=split+p.split
            if phase < change:
                changet=self.t
                # print("Change phase", changet)
                for intersection in p.io:
                    input=self.input[intersection[0]]
                    output=self.output[intersection[1]]
                    road=intersection[2]
                    if not road.full(changet):
                        changet=(change-split)*self.cycle+self.t
                        for t,v in input.get(max(self.t,road.freeInputTime),changet):
                            if v==None:
                                can=False
                                changet=t
                                can0=False
                                break
                            else:
                                can=road.push(t,v)
                                if not can:
                                    changet=road.freeInputTime
                                    can0=False
                                    break
                               
                            if road.freeInputTime > changet:
                                break        
                    # Empty the intersection
                    if not output.full(changet):
                        for t,v in road.get(0):
                            can=output.push(t,v)
                            if not can:
                                can0=False
                                break
                    # for p in self.phases:
                    #     for intersection in p.io:
                    #         intersection[2].freeInputTime=road.freeInputTime
                if self.t==changet:
                    return False
                self.t=changet
                break
            split=change
        return can0
        
class Vehicle:
    car_id = 0
    def __init__(self, length):
        self.car_id = Vehicle.car_id
        Vehicle.car_id += 1
        self.length = length
        self.log=[]

    def totalDistance(self,velocity):
        d= velocity/50*28
        return max(d, self.length+1.5)
        # if velocity == 0:
        #     return 1.5+self.length
        # if velocity <= 30:
        #     return 17
        # if velocity <= 50:
        #     return 28

class Executor:
    def __init__(self, f):

        self.f = f

class Sensor:
    def __init__(self, road):
        self.road = road
        self.intensidad=[]
        self.ocupacion=[]
        self.velocity=[]
        self.num=[]
        self.intervalo=5*60
    
    def addVehicle(self, v):
        for t,fname,name in v.log:
            if name==self.road.name:
                if fname=="push":
                    tin=t
                if fname=="get":
                    for i in range(1000):
                        if len(self.intensidad)<=i:
                            self.intensidad.append(0)
                            self.ocupacion.append(0)
                            self.velocity.append(0)
                            self.num.append(0)
                        if t<(i+1)*self.intervalo:
                            self.intensidad[i]+=1
                            # tiempo de ocupación.
                            # velocidad= e/t 
                            velocity=self.road.length/(t-tin)
                            # velocitykms=velocity*3.6
                            # print("velocidad",velocitykms)
                            # t=e/v
                            # ocupación= t/intervalo
                            self.velocity[i]+=velocity
                            self.num[i]+=1
                            self.ocupacion[i]+=v.length/velocity/self.intervalo

                            if 1<self.ocupacion[i]:
                                print("Ocupacion mayor a 1",self.ocupacion[i])

                            #self.freeInputTime=time+(vehicle.length*self.safetyDistance())/self.velocityms()
    
                            break
                    

    def study(self):
        intervalo=[]
        for i in range(len(self.intensidad)):
            intervalo.append((self.intensidad[i],self.ocupacion[i],self.velocity[i]/self.num[i]))

        #elimina el último intervalo ya que son coches sueltos
        intervalo=intervalo[:-1]

        # sort by ocupacion
        intervalo.sort(key=lambda x: x[1], reverse=True)
        # top 5%
        top5=int(len(intervalo)*0.05)
        intervalo5=intervalo[:top5]

        top33=int(len(intervalo)*0.33)
        intervalo33=intervalo[:top33]

        # promedia intensidad
        #print(f"Intensidad top5%: {sum([x[0] for x in intervalo5])/top5:.0f}({sum([x[1] for x in intervalo5])/top5*100:.0f}%)")
        #print(f"Intensidad top33%: {sum([x[0] for x in intervalo33])/top33:.0f}({sum([x[1] for x in intervalo33])/top33*100:.0f}%)")


        # matplotlib intervalo
        import matplotlib.pyplot as plt
        
        # Extract data for plotting
        intensidades = [x[0] for x in intervalo]
        ocupaciones = [x[1]*100 for x in intervalo]  # Convert to percentage

        velocidades = [x[2] for x in intervalo]
        
        plt.figure(figsize=(10, 6))
        plt.scatter(ocupaciones, intensidades, alpha=0.7)
        plt.xlabel('Ocupación (%)')
        plt.ylabel('Intensidad (vehículos/intervalo)')
        plt.title('Relación entre Ocupación e Intensidad')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add trend line
        # if len(intensidades) > 1:
        #     z = np.polyfit(ocupaciones, intensidades, 1)
        #     p = np.poly1d(z)
        #     plt.plot(ocupaciones, p(ocupaciones), "r--", alpha=0.8)
            
        plt.tight_layout()
        plt.show()

        print()

def aforo():
    # Read csv cruce4_afor.csv
    cruce4_afor = pd.read_csv('cruce4_aforo.csv', sep=',')

    print(cruce4_afor.head())
    sentido=[0,-1,1,-1,1,-1,1,-1,1]

    # Recorre las filas del dataframe
    for index, row in cruce4_afor.iterrows():
        positivo=0
        negativo=0
        for j,column in enumerate(cruce4_afor.columns):
            if sentido[j]!=0:
                if sentido[j]==1:
                    positivo+=row[column]
                else:
                    negativo+=row[column]
        if negativo>positivo:
            alfa=negativo/positivo
            beta=1
        else:
            beta=positivo/negativo
            alfa=1
        positivo=0
        negativo=0
        n=len(cruce4_afor.columns)-1

        symbols=""
        iMaxPositivo=-1
        iMaxNegativo=-1
        for j,column in enumerate(cruce4_afor.columns):
            if sentido[j]!=0:
                symbols+="r"+str(j)+str((j+1)%n)+" "
                if sentido[j]==1:
                    row[column]=int(round(row[column]*alfa))
                    if iMaxPositivo==-1 or row[column]>row[iMaxPositivo]:
                        iMaxPositivo=column
                    positivo+=row[column]
                else:
                    row[column]=int(round(row[column]*beta))
                    if iMaxNegativo==-1 or row[column]>row[iMaxNegativo]:
                        iMaxNegativo=column
                    negativo+=row[column]
        
        if positivo>negativo:
            row[iMaxNegativo]+=positivo-negativo
        
        if positivo<negativo:
            row[iMaxPositivo]+=negativo-positivo
            
        

        rs = sp.symbols(symbols)

        #eqs = [rs[-1]-0]
        eqs=[rs[-1]-273]
        eqs=[]

        for j,column in enumerate(cruce4_afor.columns):
            if sentido[j]!=0:
                
                if sentido[j]==1:
                    eqs.append(rs[j-2]+row[column]-rs[(j-1)%n])
                else:
                    eqs.append(rs[j-2]-row[column]-rs[(j-1)%n])

        sol = sp.solve(eqs, rs)
        #print(sol)
        ma=0
        for s in sol.values():
            if 0<len(s.args):
                ma=max(-s.args[0],ma.numerator)
        eqs.append(rs[-1]-ma)
        sol = sp.solve(eqs, rs)
        print(sol)

        print()
        
        # psalir=[]
        # for j,column in enumerate(cruce4_afor.columns):
        #     if sentido[j]!=0:
        #         if sentido[j]==1:
        #             pass
        #         else:
        #             psalir.append(row[column]/negativo)
        
        # print("psalir",psalir)  



    print()

def rotonda():
    Road(length=100, velocity=50, name="in blas infante", lanes=2)
    Road(length=100, velocity=50, name="in santa fe", lanes=2)
    Road(length=100, velocity=50, name="in republica argentina", lanes=2)
    Road(length=100, velocity=50, name="in lópez de gomara", lanes=2)
    Road(length=100, velocity=50, name="out blas infante", lanes=2)
    Road(length=100, velocity=50, name="out santa fe", lanes=2)
    Road(length=100, velocity=50, name="out republica argentina", lanes=2)
    Road(length=100, velocity=50, name="out lópez de gomara", lanes=2)


def main():
    road0= Road(100, 40,name="road0")
    road1= Road(100, 40,name="road1")

    road3= Road(100, 40,name="road3")
    road4= Road(100, 40,name="road4")

    # Create an intersection with 2 inputs and 2 outputs
    intersection = Intersection([road0,road1], [road3,road4],2,name="intersection")


    intersection.phases[0].open(0,0,8,22)
    intersection.phases[1].open(1,1,8,22)

    inCars=0
    outCars=0
    time=[0,0]


    def insert():
        nonlocal time, inCars
        
        for i,road in enumerate([road0,road1]):
            if time[i]>60*60*10: # 10 hour of simulation
                time[i]+=60
                road.push(time[i])
                continue

            time[i]=max(time[i],road.freeInputTimeAll())
            if road.full(time[i]):
                continue

            vehicle=Vehicle(np.random.normal(4.2,1))
            inCars+=1
            road.push(time[i],vehicle)
            #print("Vehicles in ",road.name,len(road.queue))
            # v=e/t => t=e/v
            road_intersection=intersection.phases[0].io[0][2]
            #time=original+ vehicle.totalDistance(road_intersection.velocity)/road_intersection.velocityms()*3
            #time+=np.random.normal(2,0.5)
            time[i]+=np.random.uniform(0,0)
        return False
    
    s=Sensor(road0)
    #s=Sensor(road1)
    #s=Sensor(intersection.phases[0].io[0][2])

    def remover():
        nonlocal outCars
        for t,v in road3.get(0):
            if v==None:
                break
            # for l in v.log:
            #     print(l)
            # print()
            outCars+=1
            s.addVehicle(v)
        for t,v in road4.get(0):
            if v==None:
                break
            # for l in v.log:
            #     print(l)
            # print()
            outCars+=1
            s.addVehicle(v)
        
        return False

    programa=[
        insert,
        intersection.run,
        remover,
    ]
    times_done = 0
    ip=0
    while True:
        while programa[ip]():
            pass
        ip=(ip+1)%len(programa)
        #print(inCars-outCars)
        if inCars>100:
            break
    s.study()


if __name__ == "__main__":
    #aforo()
    main()
    #rotonda()