#!/usr/bin/python
# -*- coding: utf-8 -*-

# Avoid cyclic imports while using type hints
from __future__ import annotations

# Imports
import numpy as np
import math

import carla

from simutack.core.ScalarData import ScalarData
from simutack.core.AnnotationData import AnnotationData
from simutack.core.Unit import Unit
from simutack.sensor.Sensor import Sensor
from simutack.attack.ScalarAttackEngine import ScalarAttackEngine


class TachometerSensor(Sensor):
    """
    """

    def __init__(self, controller: DataController, name: str, update_interval: float = 1.0) -> None:
        """Constructor"""
        # Call constructor of base class
        Sensor.__init__(self, controller, name, 'powertrain', update_interval)

        # Init class attributes
        self.type = 'tachometer'
        self.attack_engine = ScalarAttackEngine()
        self.set_enabled(True)

    def tick(self, frame: int) -> None:
        """
        Overwrite base class method since there is no async callback from carla for this sensor
        """
        # Check if we want to process this update (only relevant if server rate is higher than user selected update rate)
        if (frame >= self.next_frame) and self.is_enabled():
            # Compute next frame when sensor data should be received
            self.next_frame = frame + \
                int(math.ceil(self.update_interval /
                              self.controller.get_world_step()))

            # Get data
            timestamp = self.controller.get_world().get_snapshot().timestamp.elapsed_seconds
            velocity_vector = self.controller.get_vehicle().get_velocity()  # 3D velocity vector
            # Vector's length is actual speed in driving direction
            velocity = math.sqrt(velocity_vector.x ** 2 +
                                 velocity_vector.y ** 2 + velocity_vector.z ** 2)
            speed = ScalarData(Unit.METER_PER_SECOND,
                               frame, timestamp, velocity)

            # Attack data
            speed = self.attack_engine.attack_data(speed)

            # Annotate data
            annotations = AnnotationData(self.attack_engine.is_enabled(
            ), self.attack_engine.get_active_attacks_list())

            # Put data in queue for further processing
            if speed:
                self.data_queue.put((speed, annotations))

            # Notify observers
            self.notify_observers()

    def set_enabled(self, enabled: bool) -> None:
        """Overwrite from base class since no carla actor is available for this sensor"""
        # Update class attribute
        self.enabled = enabled

    def respawn_sensor(self) -> None:
        """Overwrite from base class since no carla actor is available for this sensor"""
        pass

    def update_sensor_attribute(self, attribute: str, value: str, respawn: bool = True) -> None:
        """Overwrite from base class since no carla actor is available for this sensor"""
        pass
    
    def set_spoofed_value(self, value: float) -> None:
        self.attack_engine.set_spoofed_value(value)

    def get_spoofed_value(self) -> float:
        return self.attack_engine.get_spoofed_value()

    def set_offset_value(self, value: float) -> None:
        self.attack_engine.set_offset_value(value)

    def get_offset_value(self) -> float:
        return self.attack_engine.get_offset_value()

    def load_configuration(self, config):
        pass

    def save_configuration(self):
        pass
