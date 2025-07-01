# We need to send the minimum time to complete the road to the next road, so it can calculate its own time to complete.


from Road import Road

def step_3(road:Road, next_road: Road):
    """
    Step 3: Send event to next road.

    """
    #road.min_time_to_complete()
    if next_road is not None:
        next_road.previous_road_max_global_t = road.max_global_t
        next_road.previous_road_global_t = road.global_t 
    
def step_5(road:Road):
    """
    Step 5: Process event from previous road and update times
    """

    # if road.previous_road_global_t is None:
    #     road.global_t = road.max_global_t
    # else:
    #     if road.max_global_t == road.global_t:
    #         ppglobal_t = road.previous_road_max_global_t if road.previous_road_max_global_t > road.global_t else road.global_t
    #     else:
    #         ppglobal_t = min(road.max_global_t, road.previous_road_max_global_t)
    #     road.global_t = ppglobal_t
    #print(f"Road {road.road_id} - Previous Road Max Global T: {road.previous_road_max_global_t},  Max Global T: {road.max_global_t}")
    road.global_t = min(road.max_global_t, road.previous_road_max_global_t) if road.previous_road_max_global_t is not None else road.max_global_t

def step_6(road:Road):
    """
    Step 6: Modify state based on the current global time and previous road's minimum time.
    """
    # Move vehicles in road
    road.move_vehicles()
    road.prev_global_t = road.global_t



