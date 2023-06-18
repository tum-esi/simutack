#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
import numpy as np
import sys
try:
    import carla
except:
    pass

from PIDController import PIDController
from Logger import logger


class LateralController:

    # Carla magnetic north vector (reference for IMU); from Carla docs
    NORTH_VECTOR = np.array([0.0, -1.0, 0.0])

    # PID controller settings (Steering)
    K_P = 0.012 # good: 0.15    # 0.01   # Proportional gain
    K_I = 0.00     # 0.0    # Integral gain
    K_D = 0.00   # 0.01   # Differential gain

    def __init__(self, dt: float):
        # PID controller settings (Steering)
        self.pid_controller = PIDController(self.K_P, self.K_I, self.K_D, dt)

        # For debugging
        if 'carla' in sys.modules:
            client = carla.Client('carla', 2000)
            self.world = client.get_world()

    def compute_steering(self, curr_loc, curr_head, target_loc):
        """
        curr_loc: current location, [lat, lon, alt]
        curr_head: current location, float, degree
        target_loc: current location, [lat, lon, alt]
        """
        # PID controller to estimate steering input
        logger.debug(
            f"Current Location: lat = {curr_loc['latitude']:.4f}, lon = {curr_loc['longitude']:.4f}, alt = {curr_loc['altitude']:.2f}\n"
            f"Target Location:  lat = {target_loc['latitude']:.4f}, lon = {target_loc['longitude']:.4f}, alt = {target_loc['altitude']:.2f}\n"
            f"Current Heading:  {curr_head:5.2f}"
        )

        # Get vehicle-target vector
        target_vec = np.array([
            # Convert geo position(degree) to m; 60 angular minutes, 1852m <-> 1 nautic mile
            (target_loc['longitude'] - curr_loc['longitude']) * 60 * 1852,
            # Convert geo position(degree) to m; 60 angular minutes, 1852m <-> 1 nautic mile, *-1 because north directs towards -y
            -1 * (target_loc['latitude'] - curr_loc['latitude']) * 60 * 1852,
            0.0,
        ])

        # Get angle between target vector and magnetic north (magnetic direction towards target waypoint)
        target_head = np.arccos(min(max(np.dot(target_vec, self.NORTH_VECTOR) / (
            np.linalg.norm(target_vec) * np.linalg.norm(self.NORTH_VECTOR)), -1.0), 1.0))
        # Convert rad to deg
        target_head = np.rad2deg(target_head)
        # Check for turning direction(error will be always positive between 0 .. 180 degree from upper formula)
        if np.cross(self.NORTH_VECTOR, target_vec)[2] < 0.0:
            target_head = 360.0 - target_head

        # Debug output
        logger.debug(f"Target Heading:  {target_head:5.2f}")

        # Get difference in magnetic orientations (error); consider over-/underflow
        error = target_head - curr_head
        if error > 180.0:
            error = error - 360
        elif error < -180.0:
            error = error + 360
        measurement = curr_head

        # Debug output
        logger.debug(f"Meas: {measurement:5.2f}, Error: {error:5.2f}")

        # Update controller state and get response
        pid_response = self.pid_controller.update(measurement, error)

        # Get distance to current target waypoint
        dist_to_target = np.linalg.norm(target_vec)

        # Debug Visualization
        #print(f"Target  Vector: x = {target_vec[0]:.7f}, y = {target_vec[1]:.7f}, z = {target_vec[2]:.7f}")
        if 'carla' in sys.modules:
            current_vector = [
                curr_loc['longitude'] * 60 * 1852,
                -curr_loc['latitude'] * 60 * 1852,
                curr_loc['altitude'],
            ]
            loc = carla.Location(
                x=current_vector[0], y=current_vector[1], z=current_vector[2])
            loc2 = carla.Location(
                x=loc.x+target_vec[0], y=loc.y+target_vec[1], z=loc.z+target_vec[2])

            vector = carla.Location(target_loc['longitude'] * 60 * 1852, -
                                    target_loc['latitude'] * 60 * 1852, target_loc['altitude'])

        return pid_response, dist_to_target

    def reset_controller(self):
        # Reset PID state variables
        self.pid_controller.reset()
