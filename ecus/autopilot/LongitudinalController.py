#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
from PIDController import PIDController
from Logger import logger


class LongitudinalController:

    # PID controller settings (Steering)
    K_P = 0.5       # Proportional gain
    K_I = 0.01     # Integral gain
    K_D = 0.02      # Differential gain

    def __init__(self, dt: float):
        # PID controller settings (Acceleration)
        self.pid_controller = PIDController(self.K_P, self.K_I, self.K_D, dt)

    def compute_acceleration(self, current_speed, target_speed):
        # PID controller to estimate throttle/brake input
        error = target_speed - current_speed
        measurement = current_speed

        # print(f"Meas: {measurement:5.3f}, Error: {error:5.3f}")

        # Update controller state and get response
        pid_response = self.pid_controller.update(measurement, error)

        # print(f"PID Response: {pid_response:5.3f}")

        # Return response
        return pid_response

    def reset_controller(self):
        # Reset PID state variables
        self.pid_controller.reset()
