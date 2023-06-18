#!/usr/bin/python
#-*- coding: utf-8 -*-

# Imports
import requests
import json

import tornado.web

from simutack.core.Unit import Unit
from simutack.api.SensorHandler import SensorHandler


class LidarSensorHandler(SensorHandler):
    def __init__(self, sensor_name):
        # Call constructor of base class
        SensorHandler.__init__(self, sensor_name)

    def sensor_update(self, data):
        # Build JSON message
        json_data = {
            "name": self.sensor_name,
            "frame": data.get_frame_number(),
            "timestamp": data.get_timestamp(),
        }

        # Update all subscribed clients
        for subscriber in self.subscribers:
            requests.post(subscriber, json=json_data)

    class TornadoHandler(tornado.web.RequestHandler):

        def get(self):
            pass

        def post(self):
            pass