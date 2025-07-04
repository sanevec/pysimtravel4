from Road import Road


def step_3(road: Road, next_road: Road) -> None:
    """Step 3: Send event to the next road.

    Calculates the minimum time required to complete the current road and updates
    the next road's buffer with this information.

    This assumes all moves have already been performed by the other DEVS mechanism.

    Args:
        road (Road): The current road.
        next_road (Road): The next road to which the event will be sent.
    """
    road.min_time_to_complete()

    if next_road is not None:
        if road.traffic_jam:
            next_road.previous_road_max_global_t = road.global_t
            next_road.previous_road_global_t = road.global_t
        else:
            next_road.previous_road_max_global_t = road.max_global_t
            next_road.previous_road_global_t = road.global_t


def step_5(road: Road) -> None:
    """Step 5: Process event from the previous road and update current time.

    Compares the current road's `max_global_t` with the previous road's `max_global_t`,
    and assigns the minimum of the two as the new `global_t` of the current road.

    Args:
        road (Road): The current road being updated.
    """
    road.global_t = min(road.max_global_t, road.previous_road_max_global_t)


def step_6(road: Road) -> None:
    """Step 6: Move vehicles and update time state.

    Moves vehicles forward within the same road based on their velocity and
    the elapsed time, without transitioning to another road.

    Args:
        road (Road): The road whose vehicles will be moved.
    """
    road.move_vehicles()
    road.prev_global_t = road.global_t
