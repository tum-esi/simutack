#!/usr/bin/python
# -*- coding: utf-8 -*-

from simutack.attack.AttackEngine import AttackEngine
from simutack.core.ScalarData import ScalarData


class ScalarAttackEngine(AttackEngine):
    def __init__(self):
        # Call constructor of base class
        AttackEngine.__init__(self)

        # Init class attributes
        self.spoofed_value = 0.0
        self.offset_value = 0.0

    def set_spoofed_value(self, value) -> None:
        self.spoofed_value = value

    def get_spoofed_value(self):
        return self.spoofed_value

    def set_offset_value(self, value) -> None:
        self.offset_value = value

    def get_offset_value(self):
        return self.offset_value

    def no_update_attack(self, data: ScalarData) -> ScalarData:
        # Use previous data but with current timestamp/frame
        data.value = self.previous_data.value
        return data

    def spoofed_value_attack(self, data: ScalarData) -> ScalarData:
        data.value = self.spoofed_value
        return data

    def constant_offset_attack(self, data: ScalarData) -> ScalarData:
        data.value += self.offset_value
        return data
