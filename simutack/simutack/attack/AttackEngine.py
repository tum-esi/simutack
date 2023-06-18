#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
import random
import copy
import carla

from simutack.util.Logger import logger
from simutack.core.SensorData import SensorData


class AttackEngine:
    """
    alle period sekunden in der simulation (bzw. der Sensor Update danach) einmal, dauerhaft bei 0, zufällig mit chance attack_chance bei negativ
    attack_chance : 0..1
    """

    def __init__(self) -> None:
        """
        """
        # Constants
        self.NO_DATA_ATTACK = 2**0
        self.NO_UPDATE_ATTACK = 2**1
        self.SPOOFED_VALUE_ATTACK = 2**2
        self.CONSTANT_OFFSET_ATTACK = 2**3
        self.DELAY_MESSAGE_ATTACK = 2**4
        self.CAMERA_BLINDING_ATTACK = 2**5
        self.ATTACK_LABELS = [
            "No Data",
            "No Update",
            "Spoofed Value",
            "Constant Offset",
            "Delay Message",
            "Camera Blinding",
        ]

        # Init class attributes
        self.enabled = False
        self.active_attacks = 0
        self.attack_period = 0
        self.attack_chance = 0.5
        self.message_delay = 0
        self.previous_data = None
        self.last_attack_time = 0  # Timestamp of last update

    def get_active_attacks_list(self):
        """
        """
        # Iterate through all attacks
        attacks = []
        for i in range(len(self.ATTACK_LABELS)):
            # Check for active attack
            if (self.is_attack_active(2**i)):
                # Add to list if active
                attacks.append(self.ATTACK_LABELS[i])
        return attacks

    def set_attack_period(self, period: float) -> None:
        """
        """
        self.attack_period = period
        logger.info("New attack period set (period = {}).".format(period))

    def get_attack_period(self) -> float:
        """
        """
        return self.attack_period

    def set_attack_chance(self, chance: float) -> None:
        """
        """
        self.attack_chance = chance
        logger.info("New attack chance set (chance = {}).".format(chance))

    def get_attack_chance(self) -> float:
        """
        """
        return self.attack_chance

    def set_message_delay(self, delay: float) -> None:
        """
        """
        self.message_delay = delay
        logger.info("New message delay set (delay = {}).".format(delay))

    def get_message_delay(self) -> float:
        """
        """
        return self.message_delay

    def remove_attack(self, attack: int) -> None:
        """
        """
        self.active_attacks = self.active_attacks & (~attack)
        logger.debug("'{}' removed.".format(attack))

    def clear_attacks(self) -> None:
        """
        """
        self.active_attacks = 0
        logger.debug("All attacks removed.")

    def apply_attack(self, attack: int) -> None:
        """
        """
        self.active_attacks = self.active_attacks | attack
        logger.debug("'{}' applied.".format(attack))

    def is_attack_active(self, attack: int) -> bool:
        """
        """
        return (self.active_attacks & attack) == attack

    def get_active_attacks(self) -> int:
        """
        """
        return self.active_attacks

    def set_enabled(self, enabled: bool) -> None:
        """
        """
        self.enabled = enabled
        if enabled:
            logger.debug("Attack engine enabled.")
        else:
            logger.debug("Attack engine disabled.")

    def is_enabled(self) -> bool:
        """
        """
        return self.enabled

    def attack_data(self, data: SensorData, vehicle_transform: carla.Transform = None, camera_transform: carla.Transform = None, fov: float = 90.0) -> SensorData:
        """
        """
        # Only attack data if engine is enabled
        if self.is_enabled():
            # Check whether attack should actually be performed on this sensor update
            perform_attack = False
            if self.attack_period == 0:  # Continuously
                perform_attack = True
            elif self.attack_period > 0:  # Periodically
                if data.timestamp > (self.last_attack_time + self.attack_period):
                    perform_attack = True
            else:  # Randomly
                if random.random() < self.attack_chance:
                    perform_attack = True

            if perform_attack:
                # Update last attack time
                self.last_attack_time = data.timestamp

                # Apply attacks
                if (self.active_attacks & self.NO_DATA_ATTACK):
                    data = None  # Drop packet
                if (self.active_attacks & self.NO_UPDATE_ATTACK):
                    data = self.no_update_attack(data)
                if (self.active_attacks & self.DELAY_MESSAGE_ATTACK):
                    data = self.delay_message_attack(data)
                if (self.active_attacks & self.SPOOFED_VALUE_ATTACK):
                    data = self.spoofed_value_attack(data)
                if (self.active_attacks & self.CONSTANT_OFFSET_ATTACK):
                    data = self.constant_offset_attack(data)
                if(self.active_attacks & self.CAMERA_BLINDING_ATTACK):
                    data = self.camera_blinding_attack(data, vehicle_transform, camera_transform, fov)

            # Save data
            self.previous_data = copy.copy(data)  # Can be expensive!

        return data

    def delay_message_attack(self, data: SensorData) -> SensorData:
        """
        """
        data.timestamp = data.timestamp + self.message_delay
        return data

    def no_update_attack(self, data: SensorData) -> SensorData:
        """
        """
        raise NotImplementedError(
            "Please implement this method in the inherited class.")

    def spoofed_value_attack(self, data: SensorData) -> SensorData:
        """
        """
        raise NotImplementedError(
            "Please implement this method in the inherited class.")

    def constant_offset_attack(self, data: SensorData) -> SensorData:
        """
        """
        raise NotImplementedError(
            "Please implement this method in the inherited class.")

    # def invalidate_data_attack(self, data: SensorData) -> SensorData:
    #     """
    #     """
    #     raise NotImplementedError(
    #         "Please implement this method in the inherited class.")

    # def glitch_attack(self, data: SensorData) -> SensorData:
    #     """
    #     """
    #     raise NotImplementedError(
    #         "Please implement this method in the inherited class.")

    # def random_value_attack(self, data: SensorData) -> SensorData:
    #     """
    #     """
    #     raise NotImplementedError(
    #         "Please implement this method in the inherited class.")
