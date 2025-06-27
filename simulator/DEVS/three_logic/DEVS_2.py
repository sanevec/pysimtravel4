# After the cars have been move, send the state of the road and the road before and check if cars can be send


from Road import Road, RoadState

def step_3(road: Road, before_road: Road):
    """
    Step 3: Send event to next road.
    """

    if before_road is not None:

        before_road.next_road_global_t = road.global_t
        before_road.next_road_state_buffer = "Ocuppied" if road.is_full() else "Free"


def step_5_6(road: Road):
    if not road.is_empty() and road.next_road_state_buffer == "Free":
        position, velocity = road.consult_vehicle()
        road.send_car = (position is not None) and (position == road.road_length) and (road.state == RoadState.Ssend) and (road.next_road_global_t == road.prev_global_t)
        #print(f"Road {road.road_id} send car: {road.send_car}; next_road_global_t: {road.next_road_global_t}, global_t: {road.global_t}, position: {position}, velocity: {velocity}")
    
    
    else:
        road.send_car = False

    road.update_state(road.next_road_state_buffer)