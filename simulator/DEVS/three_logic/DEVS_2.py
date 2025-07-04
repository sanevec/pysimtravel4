# After the cars have been move, send the state of the road and the road before and check if cars can be send


from Road import Road, RoadState

def step_3(road: Road, before_road: Road):
    """
    Step 3: Send event to next road.
    """

    if before_road is not None:

        before_road.next_road_global_t = road.global_t
        nof_vehicles = (road.tail_queue - road.head_queue + road.max_occupancy) % road.max_occupancy
        try:
            position, _ = road.consult_last_vehicle()
        except:
            position = road.road_length
        
        before_road.next_road_vehicle_position = position
        before_road.next_road_nof_vehicles = (road.tail_queue - road.head_queue + road.max_occupancy) % road.max_occupancy
        before_road.next_road_max_nof_vehicles = road.max_occupancy # it could be done in a prephase as this will never change
        before_road.next_road_red_light = road.red_light


def step_5_6(road: Road):
    next_road_state = "Free" if road.next_road_vehicle_position is  None or road.next_road_vehicle_position>=5 else "Ocuppied"
    road.update_state(next_road_state)

    try:
        position, _ = road.consult_vehicle()
    except:
        position = -1

    #print(f"1: {road.road_length - position < 1e-6} 2: {road.next_road_global_t == road.global_t} 3:{road.next_road_nof_vehicles != road.next_road_max_nof_vehicles} 4: ")
    if (road.road_length - position < 1e-6) and \
        (road.next_road_global_t == road.global_t) and \
            (road.next_road_nof_vehicles != road.next_road_max_nof_vehicles):
        # print(f"{road.road_id} next_road_position{road.next_road_vehicle_position}")
        if (road.next_road_nof_vehicles == 0) or (road.next_road_vehicle_position >= road.car_length):
            road.send_car = True
            road.traffic_jam = False 
        else:
            road.send_car = False
            road.traffic_jam = True
 
    else:
        road.send_car = False
        road.traffic_jam = False


    #road.update_state(road.next_road_vehicle_position)