# After the cars have been move, send the state of the road and the road before and check if cars can be send


from Road import Road, RoadState

def step_3(road: Road, before_road: Road):
    """
    Step 3: Send event to next road.
    """

    if before_road is not None:

        before_road.next_road_global_t = road.global_t

        try:
            position, _ = road.get_last_vehicle()
        except:
            position = None
        
        position = position if position is not None else road.road_length
        before_road.next_road_state_buffer = "Ocuppied" if road.is_full() or (position <10) else "Free"


def step_5_6(road: Road):
    if not road.is_empty():
        position, velocity = road.consult_vehicle()

        verify_position = (position is not None) and (position == road.road_length)
        verify_next_road = (road.state == RoadState.Ssend) and (road.next_road_global_t == road.prev_global_t) and road.next_road_state_buffer == "Free"
        verify_road_car_deletion = road.car_deletion

        road.send_car =  verify_position and (verify_next_road or verify_road_car_deletion)
                                                                                       


        #print(f"Road {road.road_id} send car: {road.send_car}; next_road_global_t: {road.next_road_global_t}, global_t: {road.global_t}, position: {position}, velocity: {velocity}")
    
    
    else:
        road.send_car = False

    road.update_state(road.next_road_state_buffer)