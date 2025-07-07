from Road import Road, RoadState


def step_3(road: Road, before_road: Road) -> None:
    """Step 3: Send event to the previous road.

    Information about the current road's state is sent to the road before it.
    This includes:
      - The position of the last car (to verify if a new car can enter).
      - The number of vehicles currently on the road.
      - The road's maximum capacity.
      - Whether the road has a red light.

    Args:
        road (Road): The current road.
        before_road (Road): The road behind the current one.
    """
    if before_road is not None:
        before_road.next_road_global_t = road.global_t

        try:
            position, _, _ = road.consult_last_vehicle()
        except Exception:
            position = road.road_length


        before_road.next_road_vehicle_position = position
        before_road.next_road_nof_vehicles = (
            (road.tail_queue - road.head_queue + road.max_occupancy) % road.max_occupancy
        )
        before_road.next_road_max_nof_vehicles = road.max_occupancy
        before_road.next_road_red_light = road.red_light


def step_5_6(road: Road) -> None:
    """Steps 5 and 6: Update road state based on next road's conditions.

    Step 5: Receives data from the next road.
    Step 6: Updates state and determines whether a car can be sent.

    The decision is based on:
      - Whether the front car is at the end of the road.
      - Whether the next road is ready to receive a car.
      - Whether there is enough space on the next road.

    Args:
        road (Road): The current road being updated.
    """
    next_road_state = (
        "Free"
        if road.next_road_vehicle_position is None or road.next_road_vehicle_position >= 5
        else "Ocuppied"
    )

    road.update_state(next_road_state)

    try:
        position, _, _ = road.consult_vehicle()
    except Exception:
        position = -1

    if (
        (road.road_length - position < 1e-6)
        and (road.next_road_global_t == road.global_t)
        and (road.next_road_nof_vehicles != road.next_road_max_nof_vehicles)
    ):
        if (road.next_road_nof_vehicles == 0) or (
            road.next_road_vehicle_position >= road.car_length
        ):
            road.send_car = True
            road.traffic_jam = False
        else:
            road.send_car = False
            road.traffic_jam = True
    else:
        road.send_car = False
        road.traffic_jam = False
