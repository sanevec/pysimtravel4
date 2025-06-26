from __future__ import annotations
from enum import Enum, auto
import random
import math

class RoadState(Enum):
    So = auto()      
    Sno = auto()     
    Ssend = auto() 


class Road:
    id = 0

    def __init__(self, road_length = 20, max_vel = 10, car_length = 5, car_generator = False, last_road = False):
        self.road_id = Road.id
        Road.id += 1

        #Road static parameters
        self.car_length = car_length
        self.road_length = road_length
        self.max_vel = max_vel
        self.car_generator = car_generator
        self.max_occupancy = int(self.road_length / car_length)
        self.min_time = self.road_length / self.max_vel  # Minimum time to complete the road
        self.car_generator =     car_generator

        # Road dynamic parameters
        self.state = RoadState.So
        #Circular queue of vehicles
        self.position_vehicles = [None] * self.max_occupancy
        self.vel_vehicles = [None] * self.max_occupancy
        self.head_queue = 0
        self.tail_queue = 0
        self.move_min_time = self.min_time  

        #Road time parameters
        self.global_t = 0
        self.prev_global_t = 0    
        self.max_global_t = 0                     
        self.max_occupancy = int(self.road_length / car_length)
        self.full = False
        

        #DEVS buffer
        self.previous_road_vehicle_buffer = None
        self.previous_road_min_time_buffer = None
        self.next_road_state_buffer = None


    def is_full(self):
        return (self.tail_queue + 1) % self.max_occupancy == self.head_queue

    def is_empty(self):
        return self.head_queue == self.tail_queue

    def push_vehicle(self, position, velocity):
        if self.is_full():
            raise Exception("Queue is full")
        self.position_vehicles[self.tail_queue] = position
        self.vel_vehicles[self.tail_queue] = velocity
        self.tail_queue = (self.tail_queue + 1) % self.max_occupancy

    def get_vehicle(self):
        
        if self.is_empty():
            raise Exception("Queue is empty")
        vehicle = self.position_vehicles[self.head_queue]
        velocity = self.vel_vehicles[self.head_queue]
        self.position_vehicles[self.head_queue] = None
        self.vel_vehicles[self.head_queue] = None
        self.head_queue = (self.head_queue + 1) % self.max_occupancy
        return vehicle, velocity
    
    def get_active_queue_data(self):
        """
        Retrieves all the active vehicle data from the circular queue
        from head to tail in order of insertion.
        Returns a list of tuples: (vehicle, velocity, queue_index)
        """
        active_data = []
        index = self.head_queue

        while index != self.tail_queue:
            vehicle = self.position_vehicles[index]
            velocity = self.vel_vehicles[index]
            active_data.append((vehicle, velocity, index))
            index = (index + 1) % self.max_occupancy

        return active_data
    
    def consult_vehicle(self):
        if self.is_empty():
            raise Exception("Queue is empty")
        vehicle = self.position_vehicles[self.head_queue]
        velocity = self.vel_vehicles[self.head_queue]
        return vehicle, velocity
    
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

        if time_to_move <= 0:
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
                max_position = self.road_length - 4 * vehicle_idx
                if position > max_position:
                    position = max_position
                
                self.position_vehicles[index] = position
                self.vel_vehicles[index] = velocity

            index = (index + 1) % self.max_occupancy
            vehicle_idx += 1


    def __str__(self):
        return f"Road ID: {self.road_id},t {self.global_t}, Pos vehicles: {str(self.position_vehicles)}  State: {self.state.name} \r\n" \
               f"                        Head: {self.head_queue  } Tail: {self.tail_queue}  \r\n" \
               f"                        Previous road vehicle buffer: {self.previous_road_vehicle_buffer}, Previous road min time buffer: {self.previous_road_min_time_buffer}, Next road state buffer: {self.next_road_state_buffer} \r\n" \
               f"                        Max global time: {self.max_global_t}, Previous global time: {self.prev_global_t}\r\n"      
    
    def min_time_to_complete(self):
        """
        Computes the minimum time for any vehicle in the queue to reach the end of the road.
        Vehicles are stored in a circular queue, and each has a position and velocity.
        """
        time_to_complete = []

        index = self.head_queue
        while index != self.tail_queue:
            position = self.position_vehicles[index]
            velocity = self.vel_vehicles[index]

            if position is not None and velocity is not None and velocity > 0:
                # Assuming vehicle has an attribute `position` (relative to start of road) 
                distance_remaining = self.road_length - position
                time = round(distance_remaining / velocity, 2)
                if time > 0:
                    time_to_complete.append(time)

            index = (index + 1) % self.max_occupancy

        print(f"time to complete for road {self.road_id}: {time_to_complete}, global_t: {self.global_t}")
        time_to_complete = min(time_to_complete) if len(time_to_complete)>0 else 0
        self.max_global_t = self.global_t + time_to_complete

    

    def DEVS_send_event(self, previous_road: Road, next_road:Road): 
        # Calculate the minimun time to complete the road, safe it and 
        
        if next_road is not None:
            next_road.previous_road_min_time_buffer = self.max_global_t
            if self.is_empty() or self.state == RoadState.Sno:
                next_road.previous_road_vehicle_buffer = None
            else:
                position, velocity = self.consult_vehicle()
                if (position == self.road_length) and (self.state == RoadState.Ssend) and (next_road.prev_global_t == self.prev_global_t):
                    # Move vehicle to next road
                    next_road.previous_road_vehicle_buffer = (0, velocity)
                    self.get_vehicle()   
        

        if previous_road is not None:
        # Send event to previous road
            previous_road.next_road_state_buffer = "Ocuppied" if self.is_full() else "Free"

    
    def DEVS_process_event(self):
        self.min_time_to_complete()
        if self.global_t == 0:
            self.global_t = self.max_global_t

        
        self.move_vehicles()
        self.prev_global_t = self.global_t



        #Simulate insrertion of a new car in the road, if it is a car generator
        active_data = self.get_active_queue_data()
    
        ## Add car to road if its a car generator
        if self.car_generator and not self.is_full():
            if len(active_data) < self.max_occupancy:
                new_position = 5
                new_velocity = self.max_vel
                self.push_vehicle(new_position, new_velocity)



        # Process events from previous road -> insert car in queue
        if self.previous_road_vehicle_buffer is not None:
            _, velocity = self.previous_road_vehicle_buffer
            self.push_vehicle(5, velocity)

        # Update state bsaed on next road event
        if self.next_road_state_buffer is not None:
            self.update_state(self.next_road_state_buffer)
        else:
            self.state = RoadState.Sno


    def DEVS_modify_state(self):
        #Update times, move cars in road depending on minimum time and calculate the next global time
        

        
        # Calculate the minimum time to complete the road
        
        # Move vehicles in road
        
        #Compare with the time from the previous road
        if self.global_t == self.max_global_t:
            self.global_t = self.previous_road_min_time_buffer if self.previous_road_min_time_buffer is not None else self.max_global_t
        elif self.previous_road_min_time_buffer is None or self.is_full:
            self.global_t = self.max_global_t
        else:
            self.global_t = min(self.max_global_t, self.previous_road_min_time_buffer)



        
            
        






        #Upadte the new max_global_t
        #self.min_time_to_complete()

    


        






        




