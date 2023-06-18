#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
from simutack.attack.AttackEngine import AttackEngine
from simutack.core.VectorData import VectorData


class VectorAttackEngine(AttackEngine):
    """
    """

    def __init__(self) -> None:
        """
        """
        # Call constructor of base class
        AttackEngine.__init__(self)

        # Init class attributes
        self.spoofed_value = []
        self.offset_value = []

    def set_spoofed_value(self, value: list) -> None:
        self.spoofed_value = value

    def get_spoofed_value(self) -> list:
        return self.spoofed_value

    def set_offset_value(self, value: list) -> None:
        self.offset_value = value

    def get_offset_value(self) -> list:
        return self.offset_value

    def no_update_attack(self, data: VectorData) -> VectorData:
        """
        """
        # Use previous data but with current timestamp/frame
        data.vector = self.previous_data.vector
        return data

    def spoofed_value_attack(self, data: VectorData) -> VectorData:
        data.vector = self.spoofed_value
        return data

    def constant_offset_attack(self, data: VectorData) -> VectorData:
        data.vector += self.offset_value
        return data
