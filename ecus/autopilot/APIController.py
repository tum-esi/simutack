#!/usr/bin/python
# -*- coding: utf-8 -*-

# Use this import to avoid cyclic imports with type checking (requires Python >= 3.7)
from __future__ import annotations

# Imports
import tornado.ioloop
import tornado.web

import threading
import asyncio
import json


from Logger import logger
from WebSocketHandler import WebSocketHandler


class APIController:
    def __init__(self, autopilot: Autopilot, port: int = 5000) -> None:
        # Init class attributes
        self.autopilot = autopilot
        self.tornado_server = tornado.web.Application(debug=True)

        self.server_thread = threading.Thread(
            target=self._start_tornado, daemon=True)
        self.port = port

        # Start server
        self.start_server()

    def create_sensor(self, sensor_type: str, name: str) -> None:
        self.controller.create_sensor(sensor_type, name)

    def start_server(self) -> None:
        # Start server in new thread to prevent the framework from blocking
        self.server_thread.start()
        logger.info("Tornado server has started at port {}".format(self.port))

    def _start_tornado(self) -> None:
        # Set event loop (required for tornado server)
        asyncio.set_event_loop(asyncio.new_event_loop())

        # Startup server listening on specified port
        self.tornado_server.listen(self.port)

        # Add handler
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/', self.TornadoHandler, dict(autopilot=self.autopilot))])

        # Create websocket handler (After new event loop was created!)
        self.websocket_handler = WebSocketHandler(
            tornado.ioloop.IOLoop.current())
        # Assign URL to handler and add it to the server (WebSocket)
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/vehicle-control/websocket', self.websocket_handler.TornadoWebSocketHandler, dict(handler=self.websocket_handler))])
        self.autopilot.attach_handler(self.websocket_handler)

        tornado.ioloop.IOLoop.current().start()

    def stop_server(self) -> None:
        tornado.ioloop.IOLoop.current().stop()
        logger.info("Tornado server has stopped.")
        # Give tornado 3s to shutdown gracefully and kill thread otherwise
        self.server_thread.join(timeout=3)

    class TornadoHandler(tornado.web.RequestHandler):
        def initialize(self, autopilot: Autopilot) -> None:
            self.autopilot = autopilot

        def set_default_headers(self):
            # print("header")
            self.set_header('Access-Control-Allow-Origin',
                            '*')
            self.set_header('Access-Control-Allow-Headers',
                            'origin, x-requested-with, content-type, accept')
            self.set_header('Access-Control-Allow-Methods',  # Allow OPTIONS method for preflight requests (CORS)
                            'GET, OPTIONS, POST')

        def check_origin(self, origin):
            # print("Check origin was called")
            return True

        def options(self, *args):
            # no body
            # `*args` is for route with `path arguments` supports
            self.set_status(204)
            self.finish()

        def get(self):
            logger.debug("GET request received.")

            # Configure HTTP response
            self.set_status(200)
            # response_body = json.dumps(sensor_info)
            response_body = 'test_get'

            # Send HTTP response
            return self.finish(response_body)

        def post(self):
            # logger.debug("POST request received. Update settings for {}.".format(
            #     self.handler.sensor_name))

            # Decode data
            try:
                data = json.loads(self.request.body.decode('utf-8'))
            except:
                data = None
            #logger.debug("Received data: \n{}".format(data))
            # print("Received data: \n{}".format(data))

            if data:
                # Enable/Disable autopilot
                try:
                    enable = bool(data['enabled'])
                    self.autopilot.set_running(enable)
                except:
                    pass

                # Reset autopilot
                try:
                    reset = bool(data['reset'])
                    if reset:
                        self.autopilot.reset_vehicle()
                except:
                    pass

            # Process data
            try:
                # Set HTTP success code
                self.set_status(201)
            except Exception as e:
                logger.error(e)
                # Set HTTP error code
                self.set_status(400)

            # Send HTTP response
            return self.finish()
