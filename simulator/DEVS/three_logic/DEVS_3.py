# Move cars in the road and send events to next road if necessary.


from Road import Road, RoadState
import random

def step_3_5_6(road: Road, next_road: Road):

    if road.send_car and next_road is not None:
        position, velocity = road.get_vehicle()
        next_road.push_vehicle(5, velocity)
    
    if road.car_generator:
        active_data  = road.get_active_queue_data()
        position = active_data[0] if active_data else None
        max_position = min(position) if position else road.road_length

        if max_position > 5:
            random_position = random.randint(5, max_position - 5)
            road.push_vehicle(random_position, road.max_vel)
