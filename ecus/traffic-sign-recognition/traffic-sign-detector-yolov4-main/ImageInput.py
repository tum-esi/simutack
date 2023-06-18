import websocket
import threading
import json
import base64
import requests

class ImageInput:
    def __init__(self, simutack_url):
        """
        Constructor.
        target = Address of targeted websocket connection (string)
        """
        # Init variables
        self.simutack_url = simutack_url
        self.image = None

        # Init camera
        self.init_camera()

        # Create websocket to receive the camera images
        input_url = "ws://" + self.simutack_url + "/sensor/camera/autopilot-camera1/websocket"
        self.websocket = websocket.WebSocketApp(
            input_url, on_open=self.on_open, on_close=self.on_close, on_message=self.on_message, on_error=self.on_error)

        # Create thread which listens for updates without blocking the main application
        self.thread = threading.Thread(target=self.listen_for_updates)

    def on_open(self, ws):
        print(f'Connection with {ws.url} was opened.')

    def on_message(self, ws, msg):
        try:
            # simutack output format
            j = json.loads(msg)
            data = j['data']['image']
            self.image = base64.b64decode(data)
        except:
            print('Failed to decode image')

    def on_close(self, ws):
        print(f'Connection with {ws.url} was closed.')

    def on_error(self, ws, error):
        print(error)

    def listen_for_updates(self):
        self.websocket.run_forever()

    def start_listening(self):
        self.thread.start()

    def get_image(self):
        return self.image

    def init_camera(self):
        # Create required camera sensor if not already available
        data = {
            'newSensors': [{
                'name': "autopilot-camera1",
                'type': "camera",
            }]
        }
        url = "http://" + self.simutack_url + '/config'
        response = requests.post(url=url, json=data, headers={
            "content-type": "application/json"}, timeout=30.0)
        print(f"Camera created: {response}")

        # Apply custom sensor settings when camera was successfully created
        camera1_settings = {
            'settings': {
                'enabled': True,
                'updateInterval': 0.1,
                'imageWidth': 700,
                'imageHeight': 300,
                'fov': 20.0,
                'position': {
                    'x': 1.5,
                    'y': 0.0,
                    'z': 1.5,
                },
                'rotation': {
                    'roll': 0.0,
                    'pitch': 0.0,
                    'yaw': 5.0,
                }
            }
        }
        url = "http://" + self.simutack_url + "/sensor/camera/autopilot-camera1"
        response = requests.post(url=url, json=camera1_settings, headers={
            "content-type": "application/json"}, timeout=30.0)
        print(f"Settings applied: {response}")
