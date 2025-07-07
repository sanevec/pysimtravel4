from Road import Road, RoadState
import random


def step_3_5_6(road: Road, next_road: Road) -> None:
    """Step 3/5/6 combined: Move vehicles and send events to next road if applicable.

    This function assumes that DEVS mechanisms have already prepared the system
    and that sending a car to the next road is valid only if conditions are met.

    It also includes auxiliary logic for car generation and deletion if the road
    supports it via `car_generator` or `car_deletion`.

    Args:
        road (Road): The current road being processed.
        next_road (Road): The road following the current one.
    """
    # Move car to next road if allowed
    if road.send_car and next_road is not None:
        position, velocity, acceleration = road.get_vehicle()
        next_road.push_vehicle(0, velocity, acceleration)

    # Generate new car if applicable
    if road.car_generator and not road.is_full():
        active_data = road.get_active_queue_data()
        positions = [item[0] for item in active_data]
        max_position = min(positions) if positions else road.road_length
        max_position = max_position if max_position != 0 else road.road_length

        if max_position > 5:
            random_position = random.randint(0, int(max_position))
            road.push_vehicle(random_position, road.max_vel)
            print("Push generator")

    # Delete car if applicable
    if road.car_deletion and road.send_car and not road.is_empty():
        position, velocity = road.get_vehicle()
