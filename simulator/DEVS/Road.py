

from __future__ import annotations
import random
import math

class Road:
    n = 0

    def __init__(self, road_length = 100, veh_vel = 10, car_generator = False):
        self.road_id = Road.n
        Road.n += 1
        self.road_length = road_length
        self.veh_vel = veh_vel
        self.car_size = 30
        self.max_occupancy = self.road_length/self.car_size

        self.max_global_t = 0 # Determines the time the vehicle can leave the road
        self.global_t = 0 # Currrent time
        self.prev_global_t = 0

        self.veh_pos_list = []
        self.light_states = [0, 1]
        self.full = 0
        
        self.light_change = 30

        self.car_generator = car_generator





    def min_time_to_complete(self):
        """
        Processes the minimum time for all the vehicles to reach the end. 
        If the time is 0 it means that the car is at the end of the road from the previous iteration. 
        So the rest vehicles of the road should be the ones to move. Right now is done so that we count
        the minimum of the times to reach the end, as all the cars have constant velocity. Nevertheless,
        if the speed is variable some more calculations should be done as the lcm
        """
        #time_to_complete = [round((self.road_length - veh_pos )/self.veh_vel, 2) for veh_pos in self.veh_pos_list] 
        time_to_complete = [round((self.road_length - i*4- self.veh_pos_list[i])/self.veh_vel,2) for i in range(len(self.veh_pos_list))]
        time_to_complete = [t for t in time_to_complete if t>0]
    

        if len(time_to_complete) > 0:
            self.max_global_t = self.global_t + min(time_to_complete)
        else:
            #If there are no cars in the road, the max_time is the global
            self.max_global_t = self.global_t
        # Traffic Light
        # if self.max_global_t % (2*self.light_change) >self.light_change:
        #     #Second cicle of trafic light
        #     time_to_add = self.light_change * 2 - self.max_global_t % (2*self.light_change)
        #     self.max_global_t += time_to_add


    def comparison_times(self, road_before: Road=None):
        """
        
        """
        if road_before is None or self.full:
            self.global_t = self.max_global_t
        else:
            if self.max_global_t == self.global_t:
                ppglobal_t = road_before.global_t
            else:
                ppglobal_t = min(self.max_global_t, road_before.max_global_t)
            self.global_t = ppglobal_t

    
    def move_vehicles_in_road(self):
        if self.car_generator:
            if len(self.veh_pos_list) > 0 and len(self.veh_pos_list) < self.max_occupancy:
                self.veh_pos_list.append(random.randint(0, math.floor(self.veh_pos_list[-1])))
            elif len(self.veh_pos_list) < self.max_occupancy :
                self.veh_pos_list.append(random.randint(self.road_length-20, self.road_length))




        time_to_move = self.global_t -self.prev_global_t
        if time_to_move > 0: 
            #Move vehicles inside road
            for i in range(len(self.veh_pos_list)):
                adv_space = time_to_move * self.veh_vel
                self.veh_pos_list[i] += round(adv_space,2)

                if self.veh_pos_list[i] > self.road_length - 4*i :
                    # Trafic light in red, I cannot advance more 
                    self.veh_pos_list[i] = self.road_length - 4*i

            
        self.full = len(self.veh_pos_list) >= self.max_occupancy

    def move_vehicle_next_road(self, road_after:Road = None):
        #Move cars next road

        
        if len(self.veh_pos_list)>0 and (self.veh_pos_list[0] == self.road_length) and (self.global_t == road_after.global_t) and (not road_after.full or road_after is None):
            road_after.veh_pos_list.append(0)
            self.veh_pos_list.pop(0)

            self.full = len(self.veh_pos_list) >= self.max_occupancy
            road_after.full = len(road_after.veh_pos_list) >= road_after.max_occupancy



    def move_time(self):
        self.prev_global_t = self.global_t

    
    def __str__(self):
        return str(self.road_id) + " Global Time:" + str(self.global_t) + ": " + str(self.veh_pos_list) + "-> Full? " + str(self.full)
    


            


    
             
    




    



    


