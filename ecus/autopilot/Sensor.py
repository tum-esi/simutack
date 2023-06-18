import websocket
import threading
import json


class Sensor:
    def __init__(self, url):
        self.url = url
        websocket.setdefaulttimeout(30)
        self.websocket = websocket.WebSocketApp(
            self.url + '/websocket', on_open=self.on_open, on_close=self.on_close, on_message=self.on_message, on_error=self.on_error)
        self.thread = threading.Thread(
            target=self.listen_for_updates, daemon=False)
        self.data = None

    def on_open(self, ws):
        print(f'Connection with {ws.url} was opened.')

    def on_message(self, ws, msg):
        try:
            j = json.loads(msg)
            self.data = j['data']
            #print(self.data)
        except:
            print('Failed to read data')

    def on_close(self, ws):
        print(f'Connection with {ws.url} was closed.')

    def on_error(self, ws, error):
        print(error)

    def listen_for_updates(self):
        self.websocket.run_forever()
        print("shouldn't reach")

    def start_listening(self):
        self.thread.start()

    def get_data(self):
        return self.data

    def get_speed_limit(self):
        try:
            speed_limit_string = self.data['sign']
            speed_limit = int(speed_limit_string)
        except:
            speed_limit = -1
        return speed_limit

    def get_speed(self):
        try:
            speed = self.data['speed']
        except:
            speed = 0
        if speed == None:
            speed = 0
        return speed

    def get_location(self):
        try:
            location = self.data
        except:
            location = {'altitude': 0.0, 'longitude': 0.0, 'latitude': 0.0}
        if location == None:
            location = {'altitude': 0.0, 'longitude': 0.0, 'latitude': 0.0}
        return location

    def get_heading(self):
        try:
            orientation = self.data['orientation']
        except:
            orientation = 0
        if orientation == None:
            orientation = 0
        return orientation
    
    def get_acceleration(self):
        try:
            acceleration = self.data['acceleration']
        except:
            acceleration = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        if acceleration == None:
            acceleration = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        return acceleration

    def get_angular_velocity(self):
        try:
            angularVelocity = self.data['angularVelocity']
        except:
            angularVelocity = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        if angularVelocity == None:
            angularVelocity = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        return angularVelocity

