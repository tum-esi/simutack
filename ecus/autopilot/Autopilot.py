import requests
import json
import time
import asyncio
import sys
from requests.adapters import HTTPAdapter, Retry

import Sensor
from Logger import logger
from LongitudinalController import LongitudinalController
from LateralController import LateralController
from APIController import APIController


class Autopilot:
    ### Constants ###
    # Networking
    SIMUTACK_ADDRESS = "http://simutack:3000"
    TRAFFIC_SIGN_ECU_ADDRESS = "http://traffic-sign-ecu:4000"

    # Vehicle Control Limits
    MAX_THROTTLE = 0.8
    MAX_BRAKE = 1.0
    MAX_STEER = 1.0
    MAX_STEER_DIFF = 0.55

    def __init__(self, port: int = 5000) -> None:
        '''
        Constructor.
        '''
        # Configure vehicle control
        self.running = False
        self.autopilot_interval = 0.1    # s
        self.dt = 0.1   # s

        # Need to wait until simutack is up and running (before accessing sensors)
        # time.sleep(10.0)

        # Setup API
        self.api_controller = APIController(self, port)

        # Setup required sensors
        # self.camera1 = Sensor.Sensor(
        #     'ws://' + self.SIMUTACK_ADDRESS[7:] + '/sensor/camera/autopilot-camera1')
        # self.camera2 = Sensor.Sensor(
        #     'ws://' + self.SIMUTACK_ADDRESS[7:] + '/sensor/camera/autopilot-camera2')
        self.gnss = Sensor.Sensor(
            'ws://' + self.SIMUTACK_ADDRESS[7:] + '/sensor/gnss/autopilot-gnss')
        self.imu = Sensor.Sensor(
            'ws://' + self.SIMUTACK_ADDRESS[7:] + '/sensor/imu/autopilot-imu')
        self.tachometer = Sensor.Sensor(
            'ws://' + self.SIMUTACK_ADDRESS[7:] + '/sensor/tachometer/autopilot-tachometer')
        self.speed_limit = Sensor.Sensor(
            'ws://' + self.TRAFFIC_SIGN_ECU_ADDRESS[7:] + '/traffic-sign')

        # Init sensors
        self.init_sensors()

        # Init PID controllers
        self.acceleration_controller = LongitudinalController(self.dt)
        self.steering_controller = LateralController(self.dt)

        # Load waypoints for target location
        self.vehicle_track = json.load(open(
            './tracks/speed_limit_crash.json'))  # List of waypoints that are used for navigation
        self.target_waypoint_index = 0   # Waypoint index in vehicle track

    def send_request(self, url, json_data):
        # Create HTTP session
        s = requests.Session()
        retries = Retry(total=10, backoff_factor=0.1)
        s.mount('http://', HTTPAdapter(max_retries=retries))

        # Make request
        try:
            response = s.post(url=url, json=json_data,
                                     headers={'content-type': 'application/json'}, timeout=30.0)
            logger.debug(response)
        except requests.ConnectionError:
            print("Connection to server failed")
        except requests.HTTPError:
            print("HTTP Error")
        except requests.Timeout:
            print("Connection to server timed out")
        except Exception as e:
            print(e)

    def attach_handler(self, handler):
        self.handler = handler

    def init_sensors(self):
        # Create required sensors if not already available
        data = {
            'newSensors': [
                {'name': "autopilot-gnss", 'type': "gnss"},
                {'name': "autopilot-imu", 'type': "imu"},
                {'name': "autopilot-tachometer", 'type': "tachometer"},
                # {'name': "autopilot-camera1", 'type': "camera"},
                # {'name': "autopilot-camera2", 'type': "camera"}
            ]
        }
        url = self.SIMUTACK_ADDRESS + '/config'
        self.send_request(url, data)
        # response = requests.post(url=url, json=data, headers={
        #     "content-type": "application/json"}, timeout=30.0)

        # Apply custom sensor settings when all sensors were successfully created
        # Dash camera
        # camera1_settings = {
        #     'settings': {
        #         'enabled': True,
        #         'updateInterval': self.dt,
        #         'imageWidth': 800,
        #         'imageHeight': 600,
        #         'fov': 90.0,
        #         'position': {
        #             'x': 1.5,
        #             'y': 0.0,
        #             'z': 2.4,
        #         },
        #         'rotation': {
        #             'roll': 0.0,
        #             'pitch': 0.0,
        #             'yaw': 0.0,
        #         }
        #     }
        # }
        # camera1_url = self.SIMUTACK_ADDRESS + "/sensor/camera/autopilot-camera1"
        # self.send_request(camera1_url, camera1_settings)

        # Third person camera
        # camera2_settings = {
        #     'settings': {
        #         'enabled': True,
        #         'updateInterval': self.dt,
        #         'imageWidth': 800,
        #         'imageHeight': 600,
        #         'fov': 90.0,
        #         'position': {
        #             'x': -6.0,
        #             'y': 0.0,
        #             'z': 5.0,
        #         },
        #         'rotation': {
        #             'roll': 0.0,
        #             'pitch': -35.0,
        #             'yaw': 0.0,
        #         }
        #     }
        # }
        # camera2_url = self.SIMUTACK_ADDRESS + "/sensor/camera/autopilot-camera2"
        # self.send_request(camera2_url, camera2_settings)

        # IMU
        imu_settings = {
            'settings': {
                'enabled': True,
                'updateInterval': self.dt,
            }
        }
        imu_url = self.SIMUTACK_ADDRESS + "/sensor/imu/autopilot-imu"
        self.send_request(imu_url, imu_settings)

        # GNSS
        gnss_settings = {
            'settings': {
                'enabled': True,
                'updateInterval': self.dt,
            }
        }
        gnss_url = self.SIMUTACK_ADDRESS + "/sensor/gnss/autopilot-gnss"
        self.send_request(gnss_url, gnss_settings)

        # Tachometer
        tacho_settings = {
            'settings': {
                'enabled': True,
                'updateInterval': self.dt,
            }
        }
        tacho_url = self.SIMUTACK_ADDRESS + "/sensor/tachometer/autopilot-tachometer"
        self.send_request(tacho_url, tacho_settings)

        # Set up the websocket connections to receive data
        # self.camera1.start_listening()
        # self.camera2.start_listening()
        self.gnss.start_listening()
        self.imu.start_listening()
        self.tachometer.start_listening()
        self.speed_limit.start_listening()

        # Notify user about success
        logger.info(
            "The required sensors for the autopilot have been successfully created.")

    def autopilot_update(self, current_speed, current_location, current_heading, target_speed, target_location):
        """
        Based on Carla local_planner.py example

        current_speed: m/s
        current_location: geo location (lat/lon/alt)
        current_speed: degree [0, 360]

        target_speed: m/s
        target_location: geo location (lat/lon/alt)
        """

        # Computed vehicle controls for this update
        control = dict()
        control['throttle'] = 0.0
        control['brake'] = 0.0
        control['steer'] = 0.0

        #print(f"Current: {current_speed} m/s, Target: {target_speed} m/s")
        #print(f"Current: {current_location}, Target: {target_location}")

        # Compute new inputs
        acceleration = self.acceleration_controller.compute_acceleration(
            current_speed, target_speed)
        steering, dist_to_target = self.steering_controller.compute_steering(
            current_location, current_heading, target_location)

        # Update waypoints
        # If the vehicle is closer than a certain (minimal) distance to the approaching waypoint, select next one
        if current_speed < 6:
            dist_threshold = 3.0
            index_count = 1
        elif current_speed < 10:
            dist_threshold = 4.0
            index_count = 1
        elif current_speed < 13:
            dist_threshold = 6.0
            index_count = 2
        elif current_speed < 16:
            dist_threshold = 8.0
            index_count = 3
        else:
            dist_threshold = 10.0
            index_count = 4
        #dist_threshold = 2.0 + (current_speed * 1.0) # This distance depends on current speed and sensor update rate (e.g., at 50m/s and 1s update rate, the vehicle drives 50m between two updates!)
        # print(dist_threshold)
        if dist_to_target < dist_threshold:
            # Update list index
            self.target_waypoint_index += index_count

            # Check for overflow (for infinite round trip)
            if self.target_waypoint_index >= len(self.vehicle_track):
                self.target_waypoint_index = 0

        #print(f"Computed Acceleration: {acceleration}, Steering: {steering}")

        # Steering regulation: changes cannot happen abruptly, can't steer too much.
        if steering > (control['steer'] + self.MAX_STEER_DIFF):
            steering = control['steer'] + self.MAX_STEER_DIFF
        elif steering < (control['steer'] - self.MAX_STEER_DIFF):
            steering = control['steer'] - self.MAX_STEER_DIFF

        # Check for acceleration boundaries
        accel = self.imu.get_acceleration()
        angular_vel = self.imu.get_angular_velocity()
        if abs(angular_vel['x']) + abs(angular_vel['y']) > 1:
            steering = 0.0
            acceleration = -0.1
            self.set_running(False)

        # print(f" A: x = {accel['x']:6.3f}, y = {accel['y']:6.3f}, z = {accel['z']:6.3f}")
        # print(f"AV: x = {angular_vel['x']:6.3f}, y = {angular_vel['y']:6.3f}, z = {angular_vel['z']:6.3f}")
        
        # Apply steering
        if steering >= 0:
            control['steer'] = min(self.MAX_STEER, steering)
        else:
            control['steer'] = max(-self.MAX_STEER, steering)

        # Apply throttle and brake
        if acceleration >= 0.0:
            control['throttle'] = min(acceleration, self.MAX_THROTTLE)
            control['brake'] = 0.0

            # Slow down when steering
            # if abs(steering) > 0.05:
            #     control['throttle'] = 0.2 * control['throttle']

        else:
            control['throttle'] = 0.0
            control['brake'] = min(abs(acceleration), self.MAX_BRAKE)

        #print(f"Throttle: {control['throttle']}, Brake: {control['brake']}, Steer: {control['steer']}")

        return control

    def get_target_speed(self):
        limit = self.get_speed_limit()
        if limit > 0:
            return limit / 3.6  # convert to m/s
        else:
            return 12.5  # m/s = 45 km/h

    def get_speed_limit(self):
        limit = self.speed_limit.get_speed_limit()
        if limit > 0:
            self.last_speed_limit = limit
        return self.last_speed_limit

    def applyControl(self, control):
        url = self.SIMUTACK_ADDRESS + "/control"
        self.send_request(url, control)
        # Notify subscribers about update (e.g., web dashboard)
        if self.handler:
            self.handler.control_update(control)

    def set_running(self, running: bool) -> None:
        self.running = running
        if self.running:
            print("Autopilot enabled")
        else:
            print("Autopilot disabled")

    def is_running(self) -> bool:
        return self.running

    def reset_vehicle(self):
        # Debug Output
        print("Reset vehicle...")

        # Reset control input
        control = dict()
        control['throttle'] = 0.0
        control['brake'] = 1.0
        control['steer'] = 0.0
        self.applyControl(control)

        # Reset speed limit memory
        self.last_speed_limit = -1

        # Reset track
        self.target_waypoint_index = 0

        # Reset PID controllers
        self.acceleration_controller.reset_controller()
        self.steering_controller.reset_controller()

        # Reset vehicle at server
        vehicle_location = dict()    # m
        vehicle_location['x'] = self.vehicle_track[0]['longitude'] * 60 * 1852
        vehicle_location['y'] = self.vehicle_track[0]['latitude'] * - \
            1 * 60 * 1852
        vehicle_location['z'] = self.vehicle_track[0]['altitude']

        vehicle_rotation = dict()    # degree
        vehicle_rotation['pitch'] = 0
        vehicle_rotation['yaw'] = -90
        vehicle_rotation['roll'] = 0

        # Adjust vehicle position to be centered on the road
        vehicle_location['x'] += 0.7
        vehicle_location['y'] += 0.5

        url = self.SIMUTACK_ADDRESS + '/config'
        data = {
            'simulation': {
                'reset': True,
                'vehicleLocation': vehicle_location,
                'vehicleRotation': vehicle_rotation
            }
        }
        self.send_request(url, data)

        # Wait until vehicle has reset and is standing still
        time.sleep(2.0)

    def main_loop(self):
        # Debug Output
        print("Start Main Loop...")

        # Reset simulation
        self.reset_vehicle()

        while True:
            # Measure time
            start_time = time.perf_counter()

            # Check if autopilot is running
            if self.running:
                # Get sensor input (Hanled via callbacks in Sensor class)
                current_speed = self.tachometer.get_speed()
                current_location = self.gnss.get_location()
                current_heading = self.imu.get_heading()

                # Get next targets
                target_speed = self.get_target_speed()
                target_location = self.vehicle_track[self.target_waypoint_index]

                # Compute new vehicle inputs
                vehicle_input = self.autopilot_update(
                    current_speed, current_location, current_heading, target_speed, target_location)

                # Apply control
                self.applyControl(vehicle_input)

            # Measure time
            elapsed = time.perf_counter() - start_time
            # print(f"Elapsed: {elapsed}, Max: {self.autopilot_interval}")
            if (self.autopilot_interval - elapsed) > 0:
                time.sleep(self.autopilot_interval - elapsed)
            else:
                print(f"Time exceeded by {elapsed - self.autopilot_interval:5.3f}s")



if __name__ == "__main__":
    pilot = Autopilot()
    pilot.main_loop()
