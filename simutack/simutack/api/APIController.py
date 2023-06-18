#!/usr/bin/python
# -*- coding: utf-8 -*-

# Use this import to avoid cyclic imports with type checking (requires Python >= 3.7)
from __future__ import annotations

# Imports
import tornado.ioloop
import tornado.web
import tornado.websocket

import threading
import asyncio

from simutack.util.Logger import logger
from simutack.api.MainHandler import MainHandler
from simutack.api.ConfigHandler import ConfigHandler
from simutack.api.VehicleControlHandler import VehicleControlHandler
from simutack.api.IMUSensorHandler import IMUSensorHandler
from simutack.api.GNSSSensorHandler import GNSSSensorHandler
from simutack.api.CameraSensorHandler import CameraSensorHandler
from simutack.api.TachometerSensorHandler import TachometerSensorHandler


class APIController:
    def __init__(self, controller: Controller, port: int = 3000) -> None:
        # Init class attributes
        self.controller = controller
        self.tornado_server = tornado.web.Application(debug=True)

        self.server_thread = threading.Thread(
            target=self._start_tornado, daemon=False)
#            target=self._start_tornado, daemon=True)
        self.port = port

        # Add main handler (WebUI)
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/', MainHandler)])
        # Add handler to serve static files reloaded by the main handler (for Vue.js files)
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/js/(.*)', tornado.web.StaticFileHandler, {'path': 'webserver/simutack-web-ui/dist/js'})])
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/css/(.*)', tornado.web.StaticFileHandler, {'path': 'webserver/simutack-web-ui/dist/css'})])
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/img/(.*)', tornado.web.StaticFileHandler, {'path': 'webserver/simutack-web-ui/dist/img'})])
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/(favicon.ico)', tornado.web.StaticFileHandler, {'path': 'webserver/simutack-web-ui/dist'})])
        # Add configuration handler (create/delete sensor)
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/config', ConfigHandler, dict(controller=self))])
        # Add control handler
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/control', VehicleControlHandler, dict(controller=self))])

        # Start server
        self.start_server()

    def create_handler(self, sensor_type: str, name: str, subscriber: str = None) -> None:
        # Create handler
        if sensor_type == 'imu':
            handler = IMUSensorHandler(
                self, name, tornado.ioloop.IOLoop.current())
        elif sensor_type == 'gnss':
            handler = GNSSSensorHandler(
                self, name, tornado.ioloop.IOLoop.current())
        elif sensor_type == 'camera':
            handler = CameraSensorHandler(
                self, name, tornado.ioloop.IOLoop.current())
        elif sensor_type == 'tachometer':
            handler = TachometerSensorHandler(
                self, name, tornado.ioloop.IOLoop.current())
        else:
            raise ValueError(
                'No suitable handler available for selected sensor type!')

        # Register handler
        self.controller.get_sensor(name).attach(handler)

        # Assign URL to handler and add it to the server (HTTP and WebSocket)
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/sensor/' + sensor_type + r'/' + name, handler.TornadoHandler, dict(handler=handler))])
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/sensor/' + sensor_type + r'/' + name + r'/websocket', handler.TornadoWebSocketHandler, dict(handler=handler))])

    def create_sensor(self, sensor_type: str, name: str) -> None:
        self.controller.create_sensor(sensor_type, name)

    def get_sensor(self, name: str) -> Sensor:
        return self.controller.get_sensor(name)

    def get_sensor_list(self) -> list:
        return self.controller.get_sensor_list()

    def apply_vehicle_control(self, control: carla.VehicleControl):
        self.controller.apply_vehicle_control(control)

    def reset_simulation(self, vehicle_transform):
        self.controller.reset_simulation(vehicle_transform)

    def get_world_step(self) -> float:
        return self.controller.get_world_step()

    def set_world_step(self, world_step: float) -> None:
        self.controller.set_world_step(world_step)

    def start_server(self) -> None:
        # Start server in new thread to prevent the framework from blocking
        self.server_thread.start()
        logger.info("Tornado server has started at port {}".format(self.port))

    def _start_tornado(self) -> None:
        # Set event loop (required for tornado server)
        asyncio.set_event_loop(asyncio.new_event_loop())

        # Startup server listening on specified port
        self.tornado_server.listen(self.port)
        tornado.ioloop.IOLoop.current().start()

    def stop_server(self) -> None:
        tornado.ioloop.IOLoop.current().stop()
        logger.info("Tornado server has stopped.")
        # Give tornado 3s to shutdown gracefully and kill thread otherwise
        self.server_thread.join(timeout=3)
