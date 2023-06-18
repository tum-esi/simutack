#!/usr/bin/python
# -*- coding: utf-8 -*-

# Use this import to avoid cyclic imports with type checking (requires Python >= 3.7)
from __future__ import annotations

# Imports
import threading
import math
from queue import Queue, Empty

import carla

from simutack.util.Logger import logger
from simutack.core.SensorObserver import SensorObserver


class Sensor:
    """Abstract base class for all sensor implementations.

    This class shall serve as a template for all sensor implementations. It provides
    some interfaces for other software components (e.g. sensor observers) to deal with
    all sensors in a uniform fashion.

    Attributes
    ----------
    controller: DataController
        Reference to the data controller object which maintains the simulation
        environment including this sensor.
    name: str
        Name of the sensor.
    category: str
        Category of the sensor (i.e. powertrain, body, chassis).
    update_interval: float
        Sensor update rate in seconds.
    enabled: bool
        If true, the sensor receives periodically updated sensor values. If false, no
        updates are received.
    observers: list
        List of subscribed observers which are notified on sensor updates.
    carla_actor: carla.Actor
        Reference to actor in CARLA simulator.
    carla_blueprint: carla.ActorBlueprint
        Blueprint of created CARLA actor.
    carla_transform: carla.Transform
        Transformed position of sensor in the CARLA world relative to parent vehicle.
    """

    def __init__(self, controller: DataController, name: str = '', category: str = '', update_interval: float = 1.0) -> None:
        """Constructor

        Parameters
        ----------
        controller: DataController
            Reference to the data controller object which maintains the simulation
            environment including this sensor.
        name: str
            Name of the sensor (default = '').
        category: str
            Category of the sensor, i.e. powertrain, body, chassis (default = '').
        update_interval: float
            Sensor update rate in seconds (default = 1.0).

        Returns
        -------
        None
            Nothing is returned.
        """
        # Init class attributes
        self.controller = controller
        self.name = name
        self.type = ""
        self.category = category
        self.update_interval = update_interval
        self.enabled = False
        self.observers = []
        self.carla_actor = None
        self.carla_blueprint = None
        self.carla_transform = None
        self.pending_respawn = False
        self.attack_engine = None
        self.data_queue = Queue()
        self.next_frame = 0

    def __del__(self) -> None:
        """Destructor

        Parameters
        ----------

        Returns
        -------
        None
            Nothing is returned.
        """
        # Destroy object in carla simulation world
        if self.carla_actor:
            self.carla_actor.destroy()

    def sensor_callback(self, data: carla.SensorData) -> None:
        """Callback for sensor update (abstract).

        Parameters
        ----------
        data: carla.SensorData
            The data produced by the carla simulation framework

        Returns
        -------
        None
            Nothing is returned.
        """
        raise NotImplementedError(
            "Please implement this method in the inherited class.")

    def is_enabled(self) -> bool:
        """Returns the sensor's activation state

        Parameters
        ----------

        Returns
        -------
        bool
            Returns whether the sensor is enabled, i.e. periodically producing
            data, or not.
        """
        return self.enabled

    def set_enabled(self, enabled: bool) -> None:
        """Set the sensor's activation state.

        Parameters
        ----------
        enabled: bool
            Sensor activation state.

        Returns
        -------
        None
            Nothing is returned.

        Raises
        ------
        ValueError
            If the carla_actor object has not been initialized yet.
        """
        # Update class attribute
        self.enabled = enabled

        # Update carla listening state if necessary
        if self.carla_actor:
            if self.carla_actor.is_listening != self.enabled:
                if self.enabled:
                    self.carla_actor.listen(
                        lambda data: self.sensor_callback(data))
                else:
                    self.carla_actor.stop()
        else:
            raise ValueError("Carla actor is None!")

    def respawn_sensor(self) -> None:
        """Respawn the carla actor from the configured blueprint.

        Parameters
        ----------

        Returns
        -------
        None
            Nothing is returned.
        """
        # Destroy current sensor object (carla actor)
        if self.carla_actor:
            self.carla_actor.destroy()
        # Spawn new sensor object (carla actor)
        self.carla_actor = self.controller.get_world().spawn_actor(
            self.carla_blueprint, self.carla_transform, attach_to=self.controller.get_vehicle())
        # Add sensor callback on new carla_actor if necessary
        self.set_enabled(self.is_enabled())
        # Reset respawn flag
        self.pending_respawn = False

    def update_sensor_attribute(self, attribute: str, value: str, respawn: bool = True) -> None:
        """Update a specific attribute of the sensor configuration.

        Parameters
        ----------
        attribute: str
            Name of the sensor attribute.
        value: str
            Attribute value.
        respawn: bool
            If True, the sensor will be respawned in the CARLA world to apply changes.
            Respawn can be avoided if multiple settings change at once and only be triggered
            for the last attribute change.

        Returns
        -------
        None
            Nothing is returned.
        """
        # Update attribute and respawn sensor
        self.carla_blueprint.set_attribute(
            attribute, value)
        if respawn:
            self.pending_respawn = True

    def attach(self, observer: SensorObserver) -> None:
        """Add new observer to observer list.

        Parameters
        ----------
        observer: SensorObserver
            Observer which will be added to observer list.

        Returns
        -------
        None
            Nothing is returned.
        """
        self.observers.append(observer)

    def detach(self, observer: SensorObserver) -> None:
        """Remove observer from observer list.

        Parameters
        ----------
        observer: SensorObserver
            Observer which will be removed to observer list.

        Returns
        -------
        None
            Nothing is returned.
        """
        self.observers.remove(observer)

    def get_name(self) -> str:
        """Return the sensor's name.

        Parameters
        ----------

        Returns
        -------
        str
            Name of the sensor.
        """
        return self.name

    def set_name(self, name: str) -> None:
        """Set the sensor's name.

        Parameters
        ----------
        name: str
            Name of the sensor.

        Returns
        -------
        None
            Nothing is returned.
        """
        self.name = name

    def get_type(self) -> str:
        return self.type

    def get_category(self) -> str:
        """Return the sensor's category.

        Parameters
        ----------

        Returns
        -------
        str
            Category of the sensor.
        """
        return self.category

    def set_category(self, category: str) -> None:
        """Set the sensor's category.

        Parameters
        ----------
        category: str
            Category of the sensor.

        Returns
        -------
        None
            Nothing is returned.
        """
        self.category = category

    def get_update_interval(self) -> float:
        """Return the sensor's update rate.

        Parameters
        ----------

        Returns
        -------
        float
            Update rate of the sensor in seconds.
        """
        return self.update_interval

    def set_update_interval(self, update_interval: float) -> None:
        """Set the sensor's update rate.

        Parameters
        ----------
        update_interval: float
            Update rate of the sensor in seconds.

        Returns
        -------
        None
            Nothing is returned.
        """
        self.update_interval = update_interval
        self.update_sensor_attribute('sensor_tick', f'{update_interval}')
        self.next_frame = 0

    def set_attack_engine_enabled(self, enabled: bool) -> None:
        self.attack_engine.set_enabled(enabled)

    def is_attack_engine_enabled(self) -> bool:
        return self.attack_engine.is_enabled()

    def clear_attacks(self) -> None:
        self.attack_engine.clear_attacks()

    def is_attack_active(self, attack: int) -> bool:
        return self.attack_engine.is_attack_active(attack)

    def get_active_attacks(self) -> int:
        return self.attack_engine.get_active_attacks()

    def apply_attack(self, attack: int) -> None:
        self.attack_engine.apply_attack(attack)

    def remove_attack(self, attack: int) -> None:
        self.attack_engine.remove_attack(attack)

    def set_attack_period(self, period: float) -> None:
        self.attack_engine.set_attack_period(period)

    def get_attack_period(self) -> float:
        return self.attack_engine.get_attack_period()

    def set_attack_chance(self, chance: float) -> None:
        self.attack_engine.set_attack_chance(chance)

    def get_attack_chance(self) -> float:
        return self.attack_engine.get_attack_chance()

    def set_message_delay(self, message_delay: float) -> None:
        self.attack_engine.set_message_delay(message_delay)

    def get_message_delay(self) -> float:
        return self.attack_engine.get_message_delay()

    def get_attack_list(self):
        # TODO: Implement attack list
        raise NotImplementedError(
            "Please implement this method in the inherited class.")

    def save_configuration(self):
        # TODO: Implement save configuration
        """JSON string containing sensor configuration"""
        pass

    def load_configuration(self, config):
        # TODO: Implement load configuration
        """e.g. JSON string"""
        pass

    def notify_observers(self):
        # Get data (if available)
        try:
            data = self.data_queue.get(block=True, timeout=0.01)
            while data:
                # Notify observers if data is available
                for observer in self.observers:

                    # try:
                    #     vehicle_transform = self.controller.get_vehicle().get_transform()
                    #     camera_transform = self.carla_actor.get_transform() # vehicle + local sensor offset
                    # except:
                    #     vehicle_transform = None
                    #     camera_transform = None
                    # image = self.attack_engine.attack_data(data[0], vehicle_transform, camera_transform)

                    # Pass actual data and annotations
                    observer.sensor_update(data[0], data[1])
                data = self.data_queue.get(block=True, timeout=0.01)
        except Empty:
            pass

    def tick(self, frame: int):
        """frame: frame that is currently processed"""
        if self.is_enabled():
            # Update data
            # -> this is done asynchronously by the server calling sensor_callback()

            # Notify observers (the internal queue mechanism ensures data synchronicity)
            self.notify_observers()

        # Allow for sensor setting changes here (in this thread) to avoid async access to 
        # class members in respawn_sensor() (memory access violation may occur otherwise)
        if self.pending_respawn:
            self.respawn_sensor()
