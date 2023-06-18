import tornado.ioloop
import tornado.web
import tornado.websocket

import threading
import asyncio

from WebSocketHandler import WebSocketHandler


class StreamServer:

    def __init__(self, controller):
        self.controller = controller
        self.tornado_server = tornado.web.Application(debug=True)
        self.server_thread = threading.Thread(
            target=self._start_tornado, daemon=False)
        self.port = 4000

        # Start server
        self.start_server()

    def start_server(self) -> None:
        # Start server in new thread to prevent the framework from blocking
        self.server_thread.start()
        print("Tornado server has started at port {}".format(self.port))

    def _start_tornado(self) -> None:
        # Set event loop (required for tornado server)
        asyncio.set_event_loop(asyncio.new_event_loop())

        # Startup server listening on specified port
        self.tornado_server.listen(self.port)

        # Create handler
        handler = WebSocketHandler(self, tornado.ioloop.IOLoop.current())
        # Assign URL to handler and add it to the server (WebSocket)
        self.tornado_server.add_handlers(
            r"(.*?)", [(r'/traffic-sign/websocket', handler.TornadoWebSocketHandler, dict(handler=handler))])
        self.controller.attach_handler(handler)
        print('handler created and added')

        # Start event loop
        tornado.ioloop.IOLoop.current().start()

    def stop_server(self) -> None:
        tornado.ioloop.IOLoop.current().stop()
        print("Tornado server has stopped.")
        # Give tornado 3s to shutdown gracefully and kill thread otherwise
        self.server_thread.join(timeout=3)
