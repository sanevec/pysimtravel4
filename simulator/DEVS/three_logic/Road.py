from __future__ import annotations
from enum import Enum, auto
import random
import math


class RoadState(Enum):
    """Enumeration representing the states of a road."""

    Sno = auto()
    Ssend = auto()
    So = auto()


class Road:
    """Class representing a road with a circular vehicle queue."""

    id = 0

    def __init__(
        self,
        road_length=20,
        max_vel=10,
        car_length=5,
        car_generator=False,
        car_deletion=False,
        red_light=False,
        red_light_time=None,
    ):
        """Initializes a Road instance.

        Args:
            road_length (int): Length of the road.
            max_vel (int): Maximum velocity allowed on the road.
            car_length (int): Length of each car.
            car_generator (bool): Whether this road generates cars.
            car_deletion (bool): Whether this road deletes cars at the end.
            red_light (bool): Whether this road is governed by a red light.
            red_light_time (float): Duration of the red light.
        """
        self.road_id = Road.id
        Road.id += 1

        # Static road parameters
        self.car_length = car_length
        self.road_length = road_length
        self.max_vel = max_vel
        self.car_generator = car_generator
        self.car_deletion = car_deletion
        self.max_occupancy = int(self.road_length / car_length)
        self.min_time = round(self.road_length / self.max_vel, 2)
        self.red_light_time = red_light_time

        # Dynamic road parameters
        self.state = RoadState.So
        self.vehicles = [(-1.0, self.max_vel, 0.0)] * self.max_occupancy
        self.head_queue = 0
        self.tail_queue = -1
        self.move_min_time = self.min_time
        self.traffic_jam = False
        self.red_light = red_light

        # Time parameters
        self.global_t = 0
        self.prev_global_t = 0
        self.max_global_t = 0
        self.full = False

        # DEVS buffer
        self.previous_road_vehicle_buffer = None
        self.previous_road_max_global_t = None
        self.previous_road_global_t = None
        self.next_road_vehicle_position = None
        self.next_road_red_light = False
        self.next_road_nof_vehicles = 0
        self.next_road_max_nof_vehicles = 0
        self.next_road_global_t = None
        self.next_road_state = None
        self.send_car = False

    def is_full(self) -> bool:
        """Checks whether the road is full.

        Returns:
            bool: True if the road is full, False otherwise.
        """
        try:
            position, _, _ = self.consult_last_vehicle()
        except Exception:
            position = None

        return not (position is None or position >= 5 or position == -1)

    def is_empty(self) -> bool:
        """Checks whether the road is empty.

        Returns:
            bool: True if the road is empty, False otherwise.
        """
        return self.head_queue == self.tail_queue

    def push_vehicle(self, position: float, velocity: float, acceleration: float) -> None:
        """Adds a vehicle to the road queue.

        Args:
            position (float): Position of the vehicle.
            velocity (float): Velocity of the vehicle.
            acceleration (float): Acceleration of the vehicle.

        Raises:
            Exception: If the road queue is full.
        """
        if self.is_full():
            raise Exception("Queue is full")

        if self.tail_queue == -1:
            self.tail_queue = 0

        self.vehicles[self.tail_queue] = (position, velocity, acceleration)
        self.tail_queue = (self.tail_queue + 1) % self.max_occupancy

    def get_vehicle(self) -> tuple[float, float, float]:
        """Retrieves and removes the vehicle at the head of the queue.

        Returns:
            tuple[float, float, float]: Position, velocity and acceleration.

        Raises:
            Exception: If the queue is empty.
        """
        if self.is_empty():
            raise Exception("Queue is empty")

        vehicle = self.vehicles[self.head_queue]
        self.vehicles[self.head_queue] = (-1.0, self.max_vel, 0.0)
        self.head_queue = (self.head_queue + 1) % self.max_occupancy
        return vehicle

    def get_active_queue_data(self) -> list[tuple[float, float, float, int]]:
        """Retrieves all active vehicles from the circular queue in order.

        Returns:
            list[tuple[float, float, float, int]]: A list of (position, velocity, acceleration, index).
        """
        active_data = []
        if self.tail_queue == -1:
            return active_data

        index = self.head_queue
        while index != self.tail_queue:
            position, velocity, acceleration = self.vehicles[index]
            active_data.append((position, velocity, acceleration, index))
            index = (index + 1) % self.max_occupancy

        return active_data

    def consult_vehicle(self) -> tuple[float, float, float]:
        """Consults the vehicle at the head of the queue.

        Returns:
            tuple[float, float, float]: Position, velocity and acceleration.

        Raises:
            Exception: If the queue is empty.
        """
        if self.is_empty():
            raise Exception("Queue is empty")

        return self.vehicles[self.head_queue]

    def consult_last_vehicle(self) -> tuple[float | None, float | None, float | None]:
        """Retrieves the last inserted vehicle in the queue.

        Returns:
            tuple[float | None, float | None, float | None]: Position, velocity, acceleration.
        """
        try:
            last_index = (self.tail_queue - 1 + self.max_occupancy) % self.max_occupancy
            return self.vehicles[last_index]
        except Exception:
            return None, None, None

    def update_state(self, next_road_event: str) -> None:
        """Updates the road state based on the next road's availability.

        Args:
            next_road_event (str): Either 'Occupied' or 'Free'.
        """
        if (self.state in [RoadState.Ssend, RoadState.So]) and next_road_event == "Ocuppied":
            self.state = RoadState.Sno
        elif (self.state in [RoadState.Sno, RoadState.So]) and next_road_event == "Free":
            self.state = RoadState.Ssend

    def move_vehicles(self) -> None:
        """Updates positions of all vehicles based on elapsed time and velocity."""
        time_to_move = self.global_t - self.prev_global_t

        if time_to_move <= 0 or self.tail_queue == -1:
            return

        index = self.head_queue
        vehicle_idx = 0

        while index != self.tail_queue:
            position, velocity, acceleration = self.vehicles[index]

            if position is not None and velocity is not None:
                adv_space = round(time_to_move * velocity, 2)
                position += adv_space
                max_position = self.road_length - self.car_length * vehicle_idx
                if position > max_position:
                    position = max_position

                self.vehicles[index] = (position, velocity, acceleration)

            index = (index + 1) % self.max_occupancy
            vehicle_idx += 1

    def __str__(self) -> str:
        """Returns a string representation of the road.

        Returns:
            str: String with road ID, time, positions, state, and queue info.
        """
        positions = [f"{p:.2f}" if p != -1 else "-1" for p, _, _ in self.vehicles]
        return (
            f"ID: {self.road_id},t {self.global_t}, Pos vehicles: "
            f"{positions}  State: {self.state.name},  "
            f"tj: {self.traffic_jam}, head-tail: {self.head_queue}-{self.tail_queue}"
        )

    def min_time_to_complete_simple(self) -> None:
        """Computes and updates the estimated max_global_t to complete the road."""
        ext_veh_pos = [self.road_length + self.car_length, ]
        ext_veh_vel = [0, ]
        

        if self.tail_queue != -1:
            index = self.head_queue
            while index != self.tail_queue:
                position, velocity, _ = self.vehicles[index]
                ext_veh_pos.append(position)
                ext_veh_vel.append(velocity)
                index = (index + 1) % self.max_occupancy

        nof_vehicles = (
            (self.tail_queue - self.head_queue + self.max_occupancy)
            % self.max_occupancy
        )


        time_to_complete = [self.road_length / self.max_vel] * (nof_vehicles+1)
    

        for i in range(nof_vehicles):
            try:
                vel_diff = ext_veh_vel[i + 1] - ext_veh_vel[i]
                if vel_diff > 0:
                    gap = ext_veh_pos[i] - ext_veh_pos[i + 1] - self.car_length
                    time_to_complete[i + 1] = gap / vel_diff
                   
            except IndexError:
                continue
            except ZeroDivisionError:
                continue
        

        if time_to_complete:
            if self.traffic_jam:
                min_time = min(e for e in time_to_complete if e > 0)
            else:
                min_time = min(time_to_complete)
        else:
            min_time = self.min_time

        self.max_global_t = round(self.global_t + min_time, 2)

    def min_time_to_complete(self) -> None:

        ext_veh_pos = [self.road_length + self.car_length, ]
        ext_veh_vel = [0, ]
        ext_veh_acc = [0, ]

        if self.tail_queue != -1:
            index = self.head_queue
            while index != self.tail_queue:
                position, velocity, acceleration = self.vehicles[index]
                ext_veh_pos.append(position)
                ext_veh_vel.append(velocity)
                ext_veh_acc.append(acceleration)
                index = (index + 1) % self.max_occupancy

        nof_vehicles = (
            (self.tail_queue - self.head_queue + self.max_occupancy)
            % self.max_occupancy
        )
        time_to_complete = [self.road_length / self.max_vel] * (nof_vehicles+1)

        # Calculation of time of each 
        # Lower index are first in the road
        for i in range(nof_vehicles):
            a = 0.5 * (ext_veh_acc[i+1] - ext_veh_acc[i])
            b = ext_veh_vel[i+1] - ext_veh_vel[i]
            c = ext_veh_pos[i+1] - ext_veh_pos[i ] + self.car_length

            disc = b**2 - 4*a*c
            var_t = (-b + math.sqrt(disc))/2*a

            time_to_complete[i+1] = var_t

        if time_to_complete:
            if self.traffic_jam:
                min_time = min(e for e in time_to_complete if e > 0)
            else:
                min_time = min(time_to_complete)
        else:
            min_time = self.min_time

        self.max_global_t = round(self.global_t + min_time, 2)






   



    

