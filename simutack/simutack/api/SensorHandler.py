#!/usr/bin/python
# -*- coding: utf-8 -*-

# Use this import to avoid cyclic imports with type checking (requires Python >= 3.7)
from __future__ import annotations

# Imports
import requests
import json

import tornado.web

from simutack.util.Logger import logger
from simutack.core.SensorObserver import SensorObserver
from simutack.core.Unit import Unit


class SensorHandler(SensorObserver):
    def __init__(self, controller: APIController, sensor_name: str, main_loop = None) -> None:
        # Init class attributes
        self.controller = controller
        self.sensor_name = sensor_name
        self.main_loop = main_loop
        self.subscribers = []  # websocket clients

        # # Add subscriber if given
        # if subscriber != None:
        #     self.subscribers.append(subscriber)

    def sensor_update(self, data: SensorData) -> None:
        raise NotImplementedError(
            "Please implement this method in the inherited class.")

    def get_sensor(self) -> Sensor:
        return self.controller.get_sensor(self.sensor_name)

    def notify_subscribers(self, data: dict) -> None:
        self.main_loop.add_callback(self._notify_subscribers, data)

    def _notify_subscribers(self, data: dict) -> None:
        for subscriber in self.subscribers:
            try:
                subscriber.write_message(data)
            except Exception as e:
                print(e)
                logger.error("Cannot reach {}!".format(subscriber))

    def register_subscriber(self, subscriber) -> None:
        self.subscribers.append(subscriber)

    def unregister_subscriber(self, subscriber) -> None:
        self.subscribers.remove(subscriber)

    class TornadoHTTPHandler(tornado.web.RequestHandler):
        def initialize(self, handler: SensorHandler) -> None:
            self.handler = handler

        def set_default_headers(self):
            self.set_header('Access-Control-Allow-Origin',
                            '*')  # Allow all origins (CORS)
            self.set_header('Access-Control-Allow-Headers',
                            'origin, x-requested-with, content-type, accept')
            self.set_header('Access-Control-Allow-Methods',  # Allow OPTIONS method for preflight requests (CORS)
                            'POST, GET, OPTIONS')

        def options(self):
            self.set_status(204)
            self.finish()

    class TornadoWebSocketHandler(tornado.websocket.WebSocketHandler):
        def initialize(self, handler: SensorHandler) -> None:
            self.handler = handler

        # def set_default_headers(self):
        #     self.set_header('Access-Control-Allow-Origin',
        #                     '*')
        #     # self.set_header('Access-Control-Allow-Headers',
        #     #                 'origin, x-requested-with, content-type, accept')
        #     # self.set_header('Access-Control-Allow-Methods',  # Allow OPTIONS method for preflight requests (CORS)
        #     #                 'GET, OPTIONS')

        # def get(self):
        #     self.set_header('Connection', 'Upgrade')
        #     self.set_header('Upgrade', 'WebSocket')

        def check_origin(self, origin):
            logger.debug("Check origin was called")
            return True

        def open(self):
            logger.debug("WebSocket to {} opened".format(self))
            self.handler.register_subscriber(self)

        def on_message(self, message):
            logger.debug("WebSocket message received: {}".format(message))

        def on_close(self):
            logger.debug("WebSocket to {} closed".format(self))
            self.handler.unregister_subscriber(self)
