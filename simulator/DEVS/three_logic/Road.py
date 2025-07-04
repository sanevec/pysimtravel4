from __future__ import annotations
from enum import Enum, auto
import random
import math

class RoadState(Enum):
   
    Sno = auto()     
    Ssend = auto() 
    So = auto() 


class Road:
    id = 0

    def __init__(self, road_length = 20, max_vel = 10, car_length = 5, car_generator = False, car_deletion = False, red_light = False, red_light_time = None):
        self.road_id = Road.id
        Road.id += 1

        #Road static parameters
        self.car_length = car_length
        self.road_length = road_length
        self.max_vel = max_vel
        self.car_generator = car_generator
        self.car_deletion = car_deletion
        self.max_occupancy = int(self.road_length / car_length)
        self.min_time = round(self.road_length / self.max_vel, 2)  # Minimum time to complete the road
        self.car_generator =     car_generator
        self.red_light_time = red_light_time

        # Road dynamic parameters
        self.state = RoadState.So
        #Circular queue of vehicles
        self.position_vehicles = [-1] * (self.max_occupancy )
        self.vel_vehicles = [max_vel] * (self.max_occupancy)
        self.head_queue = 0
        self.tail_queue = -1 # Start with -1 to allow first push to index 0
        self.move_min_time = self.min_time  
        self.traffic_jam = False        

        self.red_light = red_light  # If True, the road is in red light mode, no cars can go out the road

        #Road time parameters
        self.global_t = 0
        self.prev_global_t = 0    
        self.max_global_t = 0                     
        self.full = False
        

        #DEVS buffer
        self.previous_road_vehicle_buffer = None
        self.previous_road_max_global_t = None
        self.previous_road_global_t = None
        self.next_road_vehicle_position = None
        self.next_road_red_light = False
        self.next_road_nof_vehicles = 0
        self.next_road_max_nof_vehicles = 0

        self.next_road_global_t = None
        self.next_road_state = None

        self.send_car = False


    def is_full(self):
        try:
            position, _ = self.consult_last_vehicle()
        except: 
            position = None
        # If the queue is empty, it is not full
        if position is None or position >= 5 or position == -1:
            return False
        else:
            return True


    def is_empty(self):
        return self.head_queue == self.tail_queue

    def push_vehicle(self, position, velocity):

        if self.is_full():
            raise Exception("Queue is full")
        
        if self.tail_queue == -1:
            self.tail_queue = 0  
            self.position_vehicles[self.tail_queue] = position
            self.vel_vehicles[self.tail_queue] = velocity
            self.tail_queue = (self.tail_queue + 1) % (self.max_occupancy)
  
        else:
            self.position_vehicles[self.tail_queue] = position
            self.vel_vehicles[self.tail_queue] = velocity
            self.tail_queue = (self.tail_queue + 1) % (self.max_occupancy)

    def get_vehicle(self):
        
        if self.is_empty():
            raise Exception("Queue is empty")
        vehicle = self.position_vehicles[self.head_queue]
        velocity = self.vel_vehicles[self.head_queue]
        self.position_vehicles[self.head_queue] = -1
        self.vel_vehicles[self.head_queue] = self.max_vel
        self.head_queue = (self.head_queue + 1) % (self.max_occupancy )
        return vehicle, velocity
    
    def get_active_queue_data(self):
        """
        Retrieves all the active vehicle data from the circular queue
        from head to tail in order of insertion.
        Returns a list of tuples: (vehicle, velocity, queue_index)
        """
        active_data = []
        if self.tail_queue == -1:
            return active_data
        
        index = self.head_queue
        while index != self.tail_queue:
            vehicle = self.position_vehicles[index]
            velocity = self.vel_vehicles[index]
            active_data.append((vehicle, velocity, index))
            index = (index + 1) % (self.max_occupancy )

        return active_data
    
    def consult_vehicle(self):
        if self.is_empty():
            raise Exception("Queue is empty")
        vehicle = self.position_vehicles[self.head_queue]
        velocity = self.vel_vehicles[self.head_queue]
        return vehicle, velocity
    
    def consult_last_vehicle(self):
        try:
            # Calculate index of the last inserted element
            last_index = (self.tail_queue - 1 + self.max_occupancy) % self.max_occupancy
            vehicle = self.position_vehicles[last_index]
            velocity = self.vel_vehicles[last_index]
            return vehicle, velocity
        except:
            return None, None
    
    
    def update_state(self, next_road_event):
        if (self.state == RoadState.Ssend or self.state == RoadState.So) and (next_road_event == "Ocuppied") :
            self.state = RoadState.Sno
        elif (self.state == RoadState.Sno or self.state == RoadState.So)  and (next_road_event == "Free"):
            self.state = RoadState.Ssend
     

    def move_vehicles(self):
        """
        Advances vehicle positions based on time passed and their velocities.
        Prevents vehicles from moving beyond road end or violating spacing.
        """
        time_to_move = self.global_t - self.prev_global_t

        if time_to_move <= 0 or self.tail_queue == -1:
            return  # Nothing to do

        index = self.head_queue
        vehicle_idx = 0  # Logical vehicle position for spacing constraint

        while index != self.tail_queue:
            position = self.position_vehicles[index]
            velocity = self.vel_vehicles[index]

            if position is not None and velocity is not None:
                adv_space = round(time_to_move * velocity, 2)
                position += adv_space

                # Spacing rule: 4 * i offset from end of road
                max_position = self.road_length - self.car_length * vehicle_idx
                if position > max_position:
                    position = max_position
                
                self.position_vehicles[index] = position
                self.vel_vehicles[index] = velocity

            index = (index + 1) % (self.max_occupancy )
            vehicle_idx += 1

        


    # def __str__(self):
    #     return f"Road ID: {self.road_id},t {self.global_t}, Pos vehicles: {str(self.position_vehicles)}  State: {self.state.name},  head: {self.head_queue}, tail: {self.tail_queue} \n\r" \
    #            f"    Max global t: {self.max_global_t}, Global t: {self.global_t}, prev_glob: {self.prev_global_t}  \n\r" \
    #            f"    Previous road max global t: {self.previous_road_max_global_t}, Previous road global t: {self.previous_road_global_t} \n \r" \
    #            f"    Next road global t: {self.next_road_global_t}" \
    #            f", Send car: {self.send_car} \n"                
                
    def __str__(self):
        return f"ID: {self.road_id},t {self.global_t}, Pos vehicles: {str(self.position_vehicles)}  State: {self.state.name},  tj: {self.traffic_jam}, head-tail: {self.head_queue}-{self.tail_queue} " \
                # f" \n\r     traffic jam {self.traffic_jam}, send_car {self.send_car}"
                
                    

    def min_time_to_complete(self): 
        """
        Computes the minimum time for any vehicle in the queue to reach the end of the road.
        Vehicles are stored in a circular queue, and each has a position.
        All vehicles have the same velocity: self.veh_vel
        """
        
        ext_veh_pos = [self.road_length + self.car_length]
        ext_veh_vel = [0]

        if self.tail_queue != -1:
            index = self.head_queue
            while index != self.tail_queue:
                ext_veh_pos.append(self.position_vehicles[index])
                ext_veh_vel.append(self.vel_vehicles[index])
                index = (index + 1) % self.max_occupancy

        nof_vehicles = (self.tail_queue - self.head_queue + self.max_occupancy) % self.max_occupancy


           
        # Inicializamos con tiempo máximo posible
        time_to_complete = [self.road_length / self.max_vel] * (nof_vehicles)

        for i in range(nof_vehicles):
            try:
                vel_diff = ext_veh_vel[i + 1] - ext_veh_vel[i]
                if vel_diff > 0:
                    gap = ext_veh_pos[i] - ext_veh_pos[i + 1] - self.car_length
                    time_to_complete[i + 1] = gap / vel_diff
            except IndexError:
                # Esto no debería ocurrir si las listas están bien construidas
                time_to_complete.append(gap / vel_diff)
                continue
            except ZeroDivisionError:
                # Si las velocidades son iguales, no se puede calcular correctamente
                continue
        if time_to_complete:     
            if self.traffic_jam:
                min_time = min([e for e in time_to_complete if e>0 ] )
            else:
                min_time = min(time_to_complete)
        else:
            min_time = self.min_time

        self.max_global_t = round(self.global_t + min_time, 2)