#!/usr/bin/python
# -*- coding: utf-8 -*-

# Use this import to avoid cyclic imports with type checking (requires Python >= 3.7)
from __future__ import annotations

# Imports
import requests
import json

from simutack.util.Logger import logger
from simutack.core.AnnotationData import AnnotationData
from simutack.core.Unit import Unit
from simutack.api.SensorHandler import SensorHandler


class GNSSSensorHandler(SensorHandler):
    def __init__(self, controller: APIController, sensor_name: str, subscriber: str = None) -> None:
        # Call constructor of base class
        SensorHandler.__init__(self, controller, sensor_name, subscriber)

    def sensor_update(self, data: VectorData, annotation: AnnotationData):
        # Build JSON message
        position = data.get_vector()
        json_data = {
            "info": {
                "name": self.sensor_name,
                "frame": data.frame,
                "timestamp": data.timestamp,
            },
            "data": {
                "latitude": position[0],
                "longitude": position[1],
                "altitude": position[2]
            },
            "annotation": {
                "attackEnabled": annotation.isAttackEnabled(),
                "attackType": annotation.getAttackType()
            }
        }

        # logger.debug('Send update: {}'.format(json_data))

        # Update all subscribed clients
        self.notify_subscribers(json_data)

    class TornadoHandler(SensorHandler.TornadoHTTPHandler):

        def get(self):
            logger.debug("GET request received. Reply data of {}.".format(
                self.handler.sensor_name))

            # Pack sensor info in JSON object
            offset = self.handler.get_sensor().get_offset_value()
            spoofed_pos = self.handler.get_sensor().get_spoofed_value()
            sensor_info = {
                'info': {
                    'name': self.handler.sensor_name,
                    'type': 'gnss',
                    'category': self.handler.get_sensor().get_category(),
                },
                'settings': {
                    'enabled': self.handler.get_sensor().is_enabled(),
                    'updateInterval': self.handler.get_sensor().get_update_interval(),
                    'noiseAltBias': self.handler.get_sensor().get_noise_alt_bias(),
                    'noiseAltStdDev': self.handler.get_sensor().get_noise_alt_stddev(),
                    'noiseLatBias': self.handler.get_sensor().get_noise_lat_bias(),
                    'noiseLatStdDev': self.handler.get_sensor().get_noise_lat_stddev(),
                    'noiseLonBias': self.handler.get_sensor().get_noise_lon_bias(),
                    'noiseLonStdDev': self.handler.get_sensor().get_noise_lon_stddev(),
                },
                'attackEngine': {
                    'enabled': self.handler.get_sensor().is_attack_engine_enabled(),
                    'attackPeriod': self.handler.get_sensor().get_attack_period(),
                    'attackChance': self.handler.get_sensor().get_attack_chance(),
                    'messageDelay': self.handler.get_sensor().get_message_delay(),
                    'activeAttacks': self.handler.get_sensor().get_active_attacks(),
                    'spoofedValue': {
                        'lat': spoofed_pos[0],
                        'lon': spoofed_pos[1],
                        'alt': spoofed_pos[2],
                    },
                    'offsetValue': {
                        'lat': offset[0],
                        'lon': offset[1],
                        'alt': offset[2],
                    },
                },
                # 'subscription': {
                #     'subscribers': self.handler.subscribers,
                # }
            }

            logger.debug("Send data: {}".format(sensor_info))

            # Configure HTTP response
            self.set_status(200)
            response_body = json.dumps(sensor_info)

            # Send HTTP response
            return self.finish(response_body)

        def post(self):
            logger.debug("POST request received. Update settings for {}.".format(
                self.handler.sensor_name))

            # Decode data
            try:
                data = json.loads(self.request.body.decode('utf-8'))
            except:
                data = None
            logger.debug("Received data: \n{}".format(data))

            # Process data
            try:
                # Update sensor settings
                settings = {}
                if 'settings' in data:
                    settings = data['settings']
                if 'enabled' in settings:
                    enabled = bool(settings['enabled'])
                    self.handler.get_sensor().set_enabled(enabled)
                if 'updateInterval' in settings:
                    update_interval = float(settings['updateInterval'])
                    self.handler.get_sensor().set_update_interval(update_interval)
                if 'noiseAltBias' in settings:
                    bias = float(settings['noiseAltBias'])
                    self.handler.get_sensor().set_noise_alt_bias(bias)
                if 'noiseAltStdDev' in settings:
                    stddev = float(settings['noiseAltStdDev'])
                    self.handler.get_sensor().set_noise_alt_stddev(stddev)
                if 'noiseLatBias' in settings:
                    bias = float(settings['noiseLatBias'])
                    self.handler.get_sensor().set_noise_lat_bias(bias)
                if 'noiseLatStdDev' in settings:
                    stddev = float(settings['noiseLatBias'])
                    self.handler.get_sensor().set_noise_lat_stddev(stddev)
                if 'noiseLonBias' in settings:
                    bias = float(settings['noiseLonBias'])
                    self.handler.get_sensor().set_noise_lon_bias(bias)
                if 'noiseLonStdDev' in settings:
                    stddev = float(settings['noiseLonStdDev'])
                    self.handler.get_sensor().set_noise_lon_stddev(stddev)

                # Update attack engine
                attack_engine = {}
                if 'attackEngine' in data:
                    attack_engine = data['attackEngine']
                if 'enabled' in attack_engine:
                    enabled = bool(attack_engine['enabled'])
                    self.handler.get_sensor().set_attack_engine_enabled(enabled)
                if 'attackPeriod' in attack_engine:
                    attack_period = int(attack_engine['attackPeriod'])
                    self.handler.get_sensor().set_attack_period(attack_period)
                if 'attackChance' in attack_engine:
                    attack_chance = float(attack_engine['attackChance'])
                    self.handler.get_sensor().set_attack_chance(attack_chance)
                if 'messageDelay' in attack_engine:
                    message_delay = float(attack_engine['messageDelay'])
                    self.handler.get_sensor().set_message_delay(message_delay)
                if 'activeAttacks' in attack_engine:
                    active_attacks = int(attack_engine['activeAttacks'])
                    self.handler.get_sensor().clear_attacks()
                    self.handler.get_sensor().apply_attack(active_attacks)
                if 'spoofedValue' in attack_engine:
                    position = attack_engine['spoofedValue']
                    lat = float(position['lat'])
                    lon = float(position['lon'])
                    alt = float(position['alt'])
                    self.handler.get_sensor().set_spoofed_value(
                        [lat, lon, alt])
                if 'offsetValue' in attack_engine:
                    position = attack_engine['offsetValue']
                    lat = float(position['lat'])
                    lon = float(position['lon'])
                    alt = float(position['alt'])
                    self.handler.get_sensor().set_offset_value([lat, lon, alt])

                # Update subscribers
                # subscription = {}
                # if 'subscription' in data:
                #     subscription = data['subscription']
                # if 'subscribe' in subscription:
                #     subscriber = str(subscription['subscribe'])
                #     self.handler.register_subscriber(subscriber)
                # if 'unsubscribe' in subscription:
                #     subscriber = str(subscription['unsubscribe'])
                #     self.handler.ungister_subscriber(subscriber)

                # Set HTTP success code
                self.set_status(201)
            except Exception as e:
                logger.error(e)

                # Set HTTP error code
                self.set_status(400)

            # Send HTTP response
            return self.finish()
