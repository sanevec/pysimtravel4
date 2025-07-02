# Move cars in the road and send events to next road if necessary.


from Road import Road, RoadState
import random

def step_3_5_6(road: Road, next_road: Road):

    if road.car_generator and not road.is_full():
        active_data  = road.get_active_queue_data()
        position = [item[0] for item in active_data]


        max_position = min(position) if len(position) > 0 else road.road_length 
        max_position = max_position if max_position != 0 else road.road_length

        if max_position >= 10:
            if max_position - 5 == 5:
                random_position = 5
            else:
                random_position = random.randint(5, int(max_position)-5)
            road.push_vehicle(random_position, road.max_vel)
            road.min_time_to_complete()
            print(f" Push generator ")


    if road.send_car and next_road is not None:
        position, velocity = road.get_vehicle()
        next_road.push_vehicle(0, velocity)

    if road.car_deletion and road.send_car and not road.is_empty():
        position, velocity = road.get_vehicle()
    
    road.min_time_to_complete()
    

