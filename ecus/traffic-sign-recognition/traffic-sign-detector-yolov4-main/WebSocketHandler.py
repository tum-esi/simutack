#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
import simplejpeg
import StreamServer
import tornado.web


class WebSocketHandler:
    def __init__(self, controller: StreamServer, main_loop=None) -> None:
        # Init class attributes
        self.controller = controller
        self.main_loop = main_loop
        self.subscribers = []  # websocket clients

        # # Add subscriber if given
        # if subscriber != None:
        #     self.subscribers.append(subscriber)

    def stream_update(self, processed_frame, detected_sign):
        # Convert image from raw to jpg
        if processed_frame is not None:
            processed_frame = simplejpeg.encode_jpeg(
                image=processed_frame,
                colorspace='RGB',
            )

        # Encode image with base64
        if processed_frame is not None:
            processed_frame = base64.b64encode(processed_frame).decode('utf-8')

        # Build message
        json_data = {
            "data": {
                "image": processed_frame,
                "sign": detected_sign,
            }
        }

        self.notify_subscribers(json_data)

    def notify_subscribers(self, data: dict) -> None:
        self.main_loop.add_callback(self._notify_subscribers, data)

    def _notify_subscribers(self, data: dict) -> None:
        for subscriber in self.subscribers:
            try:
                subscriber.write_message(data)
            except Exception as e:
                print(e)
                print("Cannot reach {}!".format(subscriber))

    def register_subscriber(self, subscriber) -> None:
        self.subscribers.append(subscriber)

    def unregister_subscriber(self, subscriber) -> None:
        self.subscribers.remove(subscriber)

    class TornadoWebSocketHandler(tornado.websocket.WebSocketHandler):
        def initialize(self, handler) -> None:
            # print("init")
            self.handler = handler

        def set_default_headers(self):
            # print("header")
            self.set_header('Access-Control-Allow-Origin',
                            '*')
            # self.set_header('Access-Control-Allow-Headers',
            #                 'origin, x-requested-with, content-type, accept')
            # self.set_header('Access-Control-Allow-Methods',  # Allow OPTIONS method for preflight requests (CORS)
            #                 'GET, OPTIONS')

        # def get(self):
        #     print("get")
        #     self.set_header('Connection', 'Upgrade')
        #     self.set_header('Upgrade', 'WebSocket')

        def check_origin(self, origin):
            # print("Check origin was called")
            return True

        def open(self):
            print("WebSocket to {} opened".format(self))
            self.handler.register_subscriber(self)

        def on_message(self, message):
            print("WebSocket message received: {}".format(message))

        def on_close(self):
            print("WebSocket to {} closed".format(self))
            self.handler.unregister_subscriber(self)
