#!/usr/bin/python
# -*- coding: utf-8 -*-

from simutack.sensor.Sensor import Sensor
from simutack.attack.VectorAttackEngine import VectorAttackEngine


class VectorSensor(Sensor):
    """
    """
    def __init__(self, controller, name, category='', update_interval=1.0):
        # Call constructor of base class
        Sensor.__init__(self, controller, name, category, update_interval)

        # Init class attributes
        self.attack_engine = VectorAttackEngine()

    def set_attack_engine_enabled(self, enabled: bool) -> None:
        self.attack_engine.set_enabled(enabled)

    def is_attack_engine_enabled(self, ):
        pass

    def clear_attacks(self):
        pass

    def is_attack_active(self, attack):
        pass

    def get_active_attacks(self, ):
        pass

    def apply_attack(self, attack):
        self.attack_engine.apply_attack(attack)

    def remove_attack(self, attack):
        pass

