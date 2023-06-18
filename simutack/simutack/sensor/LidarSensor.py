#!/usr/bin/python
# -*- coding: utf-8 -*-

# Avoid cyclic imports while using type hints
from __future__ import annotations

# Imports
import struct

import carla

#import simutack.core.DataController as DataController
from simutack.core.PointCloudData import PointCloudData
from simutack.core.LidarData import LidarData
from simutack.core.Unit import Unit
from simutack.sensor.Sensor import Sensor
from simutack.attack.PointCloudAttackEngine import PointCloudAttackEngine


class LidarSensor(Sensor):
    """
    """

    def __init__(self, controller: DataController, name: str, update_interval: float = 1.0) -> None:
        """Constructor"""
        # Call constructor of base class
        Sensor.__init__(self, controller, name, 'body', update_interval)

        # Init class attributes
        self.lidar_measurement = PointCloudData(Unit.LIDAR)

        # Create Lidar sensor in carla world
        self.carla_blueprint = self.controller.get_blueprint_library().find(
            'sensor.lidar.ray_cast')
        self.carla_blueprint.set_attribute(
            'sensor_tick', f'{self.update_interval}')
        self.carla_transform = carla.Transform(carla.Location(x=-0.5, z=1.8))
        self.respawn_sensor()
        self.set_enabled(True)

    def set_channels(self, channels: int) -> None:
        self.update_sensor_attribute('channels', f'{channels}')

    def set_range(self, r: float) -> None:
        self.update_sensor_attribute('range', f'{r}')

    def set_points_per_second(self, pps: int) -> None:
        self.update_sensor_attribute('points_per_second', f'{pps}')

    def set_rotation_frequency(self, frequency: float) -> None:
        self.update_sensor_attribute('rotation_frequency', f'{frequency}')

    def set_upper_fov(self, fov: float) -> None:
        self.update_sensor_attribute('upper_fov', f'{fov}')

    def set_lower_fov(self, fov: float) -> None:
        self.update_sensor_attribute('lower_fov', f'{fov}')

    def set_noise_stddev(self, stddev: float) -> None:
        self.update_sensor_attribute('noise_stddev', f'{stddev}')

    def get_channels(self) -> int:
        return self.carla_blueprint.get_attribute('channels')

    def get_range(self) -> float:
        return self.carla_blueprint.get_attribute('range')

    def get_points_per_second(self) -> int:
        return self.carla_blueprint.get_attribute('points_per_second')

    def get_rotation_frequency(self) -> float:
        return self.carla_blueprint.get_attribute('rotation_frequency')

    def get_upper_fov(self) -> float:
        return self.carla_blueprint.get_attribute('upper_fov')

    def get_lower_fov(self) -> float:
        return self.carla_blueprint.get_attribute('lower_fov')

    def get_noise_stddev(self) -> float:
        return self.carla_blueprint.get_attribute('noise_stddev')

    def get_points(self, target_unit: Unit) -> PointCloudData:
        return self.lidar_measurement

    def sensor_callback(self, data: carla.SensorData) -> None:
        self.lidar_measurement.set_frame_number(data.frame)
        self.lidar_measurement.set_timestamp(data.timestamp)
        # Save points
        measurement = []
        for i in range(len(data.raw_data) // 16):
            m = struct.unpack('ffff', data.raw_data[i*16:((i+1)*16)])
            measurement.append(LidarData(*m))
        self.lidar_measurement.set_points(measurement)
        #data = np.copy(np.frombuffer(point_cloud.raw_data, dtype=np.dtype('f4')))
        #data = np.reshape(data, (int(data.shape[0] / 4), 4))

    def save_configuration(self):
        pass

    def load_configuration(self, config):
        pass
