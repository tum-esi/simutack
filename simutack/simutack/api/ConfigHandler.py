#!/usr/bin/python
# -*- coding: utf-8 -*-

# Use this import to avoid cyclic imports with type checking (requires Python >= 3.7)
from __future__ import annotations

# Imports
import requests
import json
import carla

import tornado.web

from simutack.util.Logger import logger


class ConfigHandler(tornado.web.RequestHandler):
    def initialize(self, controller: APIController) -> None:
        self.controller = controller

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin',
                        '*')  # Allow all origins (CORS)
        self.set_header('Access-Control-Allow-Headers',
                        'origin, x-requested-with, content-type, accept')
        self.set_header('Access-Control-Allow-Methods',  # Allow OPTIONS method for preflight requests (CORS)
                        'POST, GET, OPTIONS, DELETE')

    def options(self):
        self.set_status(204)
        self.finish()

    def delete(self):
        logger.debug("DELETE request received. Delete sensor.")

        # Decode data
        try:
            data = json.loads(self.request.body.decode('utf-8'))
        except:
            data = None
        logger.debug("Received data: {}".format(data))

        # Process data
        try:
            name = data['name']
            self.controller.delete_sensor(name)

            # Set HTTP success code
            self.set_status(201)
        except:
            # Set HTTP error code
            self.set_status(400)

        # Send HTTP response
        return self.finish()

    def get(self):
        logger.debug("GET request received. List available sensors.")

        # Get available sensors
        sensors = self.controller.get_sensor_list()
        logger.debug("Available sensors: {}".format(sensors))

        # Configure HTTP response
        json_data = {
            'sensors': sensors,
            'simulation': {
                'worldStep': self.controller.get_world_step()
            },
        }

        self.set_status(200)
        response_body = json.dumps(json_data)

        # Send HTTP response
        return self.finish(response_body)

    def post(self):
        logger.debug("POST request received. Create new sensor.")

        # Decode data
        try:
            data = json.loads(self.request.body.decode('utf-8'))
        except:
            data = None
        logger.debug("Received data: {}".format(data))

        # Process data
        try:
            # Create new sensors
            taken_sensor_names = [sensor['name']
                                  for sensor in self.controller.get_sensor_list()]
            new_sensors = data.get('newSensors', [])
            for sensor in new_sensors:
                name = sensor['name']
                sensor_type = sensor['type']
                # subscriber = sensor['subscriber']

                # Create sensor and appropriate handler
                if name not in taken_sensor_names:
                    self.controller.create_sensor(sensor_type, name)
                    self.controller.create_handler(sensor_type, name)
                    # self.controller.create_handler(sensor_type, name, subscriber)
                else:
                    pass
                    #raise ValueError("Name already in use!")

            # Reset simulation
            simulation = data.get('simulation', {})
            reset_simulation = simulation.get('reset', False)
            vehicle_location = simulation.get('vehicleLocation', None)
            vehicle_rotation = simulation.get('vehicleRotation', None)
            if reset_simulation:
                vehicle_transform = None
                rotation = carla.Rotation()
                if vehicle_rotation:
                    rotation = carla.Rotation(vehicle_rotation['pitch'], vehicle_rotation['yaw'], vehicle_rotation['roll'])
                if vehicle_location:
                    vehicle_transform = carla.Transform(carla.Location(vehicle_location['x'], vehicle_location['y'], vehicle_location['z']), rotation)
                self.controller.reset_simulation(vehicle_transform)
            # Set world step
            world_step = simulation.get('worldStep', -1.0)
            if world_step > 0.0:
                self.controller.set_world_step(world_step)

            # Set HTTP success code
            self.set_status(201)
        except Exception as e:
            # Log exeption
            logger.debug(e)

            # Set HTTP error code
            self.set_status(400)

        # Send HTTP response
        return self.finish()
