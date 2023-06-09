#!/usr/bin/python
# -*- coding: utf-8 -*-

# Avoid cyclic imports while using type hints
from __future__ import annotations

# Imports
import numpy as np
import math

import carla

from simutack.util.Logger import logger
from simutack.core.VectorData import VectorData
from simutack.core.AnnotationData import AnnotationData
from simutack.core.Unit import Unit
from simutack.sensor.Sensor import Sensor
from simutack.attack.VectorAttackEngine import VectorAttackEngine


class IMUSensor(Sensor):
    """
    """

    def __init__(self, controller: DataController, name: str, update_interval: float = 1.0) -> None:
        """Constructor"""
        # Call constructor of base class
        Sensor.__init__(self, controller, name, 'body', update_interval)

        # Init class attributes
        self.type = 'imu'
        self.attack_engine = VectorAttackEngine()
        self.attack_engine.set_offset_value([0.0])  # Only orientation
        self.attack_engine.set_spoofed_value([0.0])

        # Create IMU sensor in carla world
        self.carla_blueprint = self.controller.get_blueprint_library().find('sensor.other.imu')
        self.carla_blueprint.set_attribute(
            'sensor_tick', f'{self.update_interval}')
        self.carla_transform = carla.Transform(
            carla.Location(0, 0, 0), carla.Rotation(0, 0, 0))
        self.respawn_sensor()
        self.set_enabled(True)

    def set_noise_accel_stddev_x(self, stddev: float) -> None:
        """Sets standard deviation parameter in the noise model for acceleration (X axis).

        Parameters
        ----------
        stddev : float
            Standard deviation in the noise model for acceleration (X axis).
        """
        self.update_sensor_attribute('noise_accel_stddev_x', f'{stddev}')

    def set_noise_accel_stddev_y(self, stddev: float) -> None:
        self.update_sensor_attribute('noise_accel_stddev_y', f'{stddev}')

    def set_noise_accel_stddev_z(self, stddev: float) -> None:
        self.update_sensor_attribute('noise_accel_stddev_z', f'{stddev}')

    def set_noise_gyro_stddev_x(self, stddev: float) -> None:
        self.update_sensor_attribute('noise_gyro_stddev_x', f'{stddev}')

    def set_noise_gyro_stddev_y(self, stddev: float) -> None:
        self.update_sensor_attribute('noise_gyro_stddev_y', f'{stddev}')

    def set_noise_gyro_stddev_z(self, stddev: float) -> None:
        self.update_sensor_attribute('noise_gyro_stddev_z', f'{stddev}')

    def set_noise_gyro_bias_x(self, bias: float) -> None:
        self.update_sensor_attribute('noise_gyro_bias_x', f'{bias}')

    def set_noise_gyro_bias_y(self, bias: float) -> None:
        self.update_sensor_attribute('noise_gyro_bias_y', f'{bias}')

    def set_noise_gyro_bias_z(self, bias: float) -> None:
        self.update_sensor_attribute('noise_gyro_bias_z', f'{bias}')

    def get_noise_accel_stddev_x(self) -> float:
        return self.carla_blueprint.get_attribute('noise_accel_stddev_x').as_float()

    def get_noise_accel_stddev_y(self) -> float:
        return self.carla_blueprint.get_attribute('noise_accel_stddev_y').as_float()

    def get_noise_accel_stddev_z(self) -> float:
        return self.carla_blueprint.get_attribute('noise_accel_stddev_z').as_float()

    def get_noise_gyro_stddev_x(self) -> float:
        return self.carla_blueprint.get_attribute('noise_gyro_stddev_x').as_float()

    def get_noise_gyro_stddev_y(self) -> float:
        return self.carla_blueprint.get_attribute('noise_gyro_stddev_y').as_float()

    def get_noise_gyro_stddev_z(self) -> float:
        return self.carla_blueprint.get_attribute('noise_gyro_stddev_z').as_float()

    def get_noise_gyro_bias_x(self) -> float:
        return self.carla_blueprint.get_attribute('noise_gyro_bias_x').as_float()

    def get_noise_gyro_bias_y(self) -> float:
        return self.carla_blueprint.get_attribute('noise_gyro_bias_y').as_float()

    def get_noise_gyro_bias_z(self) -> float:
        return self.carla_blueprint.get_attribute('noise_gyro_bias_z').as_float()

    def set_spoofed_value(self, value: list) -> None:
        self.attack_engine.set_spoofed_value(value)

    def get_spoofed_value(self) -> list:
        return self.attack_engine.get_spoofed_value()

    def set_offset_value(self, value: list) -> None:
        self.attack_engine.set_offset_value(value)

    def get_offset_value(self) -> list:
        return self.attack_engine.get_offset_value()

    def sensor_callback(self, data: carla.SensorData) -> None:
        # Check if we want to process this update (only relevant if server rate is higher than user selected update rate)
        if (data.frame >= self.next_frame) and self.is_enabled():
            # Compute next frame when sensor data should be received
            self.next_frame = data.frame + \
                int(math.ceil(self.update_interval /
                              self.controller.get_world_step()))

        # Get data
        acceleration = VectorData(Unit.METER_PER_SECOND_PER_SECOND, data.frame, data.timestamp,
                                  np.array([data.accelerometer.x, data.accelerometer.y, data.accelerometer.z]))

        angular_velocity = VectorData(Unit.METER_PER_SECOND, data.frame, data.timestamp,
                                      np.array([data.gyroscope.x, data.gyroscope.y, data.gyroscope.z]))

        orientation = VectorData(
            Unit.RADIAN, data.frame, data.timestamp, data.compass)

        # Attack data
        # acceleration = self.attack_engine.attack_data(acceleration)
        # angular_velocity = self.attack_engine.attack_data(
        #     angular_velocity)
        orientation = self.attack_engine.attack_data(orientation)

        # Annotate data
        annotations = AnnotationData(self.attack_engine.is_enabled(
        ), self.attack_engine.get_active_attacks_list())

        # Put data in queue for further processing
        if acceleration:
            self.data_queue.put(((acceleration, angular_velocity, orientation), annotations))

    def save_configuration(self):
        pass

    def load_configuration(self, config):
        pass
