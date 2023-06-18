#!/usr/bin/python

# Imports
import time
import sys

import carla

from simutack.sensor.Sensor import Sensor
from simutack.core.DataController import DataController
from simutack.api.APIController import APIController

# Constants
VERSION_MAJOR = 0
VERSION_MINOR = 4


class Controller:
    def __init__(self, carla_ip: str = 'localhost', carla_port: int = 2000):
        # Init class attributes
        self.data_controller = DataController(
            self, carla_ip=carla_ip, carla_port=carla_port)
        self.api_controller = APIController(self)

        # Start simulation
        self.data_controller.start_simulation()

    def create_sensor(self, sensor_type, name, update_interval=1.0):
        self.data_controller.create_sensor(sensor_type, name, update_interval)

    def delete_sensor(self, name):
        self.data_controller.delete_sensor(name)

    def create_handler(self, sensor_type, name):
        self.api_controller.create_handler(sensor_type, name)

    def get_sensor(self, name) -> Sensor:
        return self.data_controller.get_sensor(name)

    def get_sensor_list(self) -> list:
        return self.data_controller.get_sensor_list()

    def get_encoder(self, name):
        pass

    def apply_vehicle_control(self, control: carla.VehicleControl):
        self.data_controller.apply_vehicle_control(control)

    def reset_simulation(self, vehicle_transform):
        self.data_controller.reset_simulation(vehicle_transform)

    def get_world_step(self) -> float:
        return self.data_controller.get_world_step()

    def set_world_step(self, world_step: float) -> None:
        self.data_controller.set_world_step(world_step)

    def shut_down(self):
        self.data_controller.stop_simulation()
        self.api_controller.stop_server()

    def _ask_for_sensor(self):
        # Get list of available sensors
        sensor_names = [sensor['name']
                        for sensor in self.data_controller.get_sensor_list()]

        # Ask for sensor name
        print("Select sensor: ")
        for i, name in enumerate(sensor_names):
            print("-> {}: {}".format(i, name))
        print("")

        # Get sensor name
        option = int(input("Select an option: "))
        if option < len(sensor_names):
            sensor_name = sensor_names[option]
        else:
            print("Wrong input! Aborting, going back to main menu...")
            sensor_name = None
        return sensor_name

    def _get_user_option(self) -> int:
        try:
            option = int(input("Select an option: "))
        except:
            option = -1
        return option

    def main_loop(self):
        print("#######################################################################")
        print("Welcome to Simutack - A data generation framework for automotive sensors!")
        print("You are running version {}.{}".format(
            VERSION_MAJOR, VERSION_MINOR))
        print("#######################################################################")

        while True:
            # Show main menu
            print("\nMain Menu\n-----------------------------------------------")
            print("Please select one of the following options:")
            print("-> 1: Create new sensor")
            print("-> 2: Configure sensor")
            print("-> 3: Delete sensor")
            print("-> 4: Attack data")
            print("-> 5: Exit")
            print("")

            # Read user input
            option = self._get_user_option()
            if option == 1:
                # Ask for sensor type of new sensor
                print("\nSelect sensor type: ")
                print("-> 1: IMU sensor")
                print("-> 2: GNSS sensor")
                print("-> 3: Camera sensor")
                print("-> 4: Back")
                print("")

                # Get sensor type
                option = int(input("Select an option: "))
                if option == 1:
                    sensor = 'imu'
                elif option == 2:
                    sensor = 'gnss'
                elif option == 3:
                    sensor = 'camera'
                elif option == 4:
                    continue
                else:
                    print(
                        "Wrong input! Please enter an interger value in the range [1, 5].")
                    print("Aborting, going back to main menu...\n")
                    continue

                # Ask for sensor name
                name = input("Enter sensor name: ")

                # Create sensor and appropriate handler
                self.create_sensor(sensor, name)
                self.create_handler(sensor, name)
                print("Sensor created.")
            elif option == 2:
                # Get sensor
                sensor_name = self._ask_for_sensor()

                # Ask for configuration option
                while True:
                    print("\nSelect configuration option: ")
                    print("-> 1: Change update rate")
                    print("-> 2: Activate sensor")
                    print("-> 3: Deactivate sensor")
                    print("-> 4: Return to main menu")
                    print("")

                    option = self._get_user_option()
                    if option == 1:
                        rate = float(input("Enter new update rate [s]: "))
                        self.get_sensor(sensor_name).set_update_interval(rate)
                        print("New update rate is {} s.".format(rate))
                    elif option == 2:
                        self.get_sensor(sensor_name).set_enabled(True)
                        print("Sensor is enabled.")
                    elif option == 3:
                        self.get_sensor(sensor_name).set_enabled(False)
                        print("Sensor is disabled.")
                    elif option == 4:
                        break
                    else:
                        print("Wrong input! Aborting, going back to main menu...")
                        break
            elif option == 3:
                print("Not implemented yet!")
            elif option == 4:
                # Get sensor
                sensor_name = self._ask_for_sensor()

                # Ask for attack option
                while True:
                    print("\nSelect attack option: ")
                    print("->  1: No Data Attack")
                    print("->  2: No Update Attack")
                    print("->  3: Message Delay Attack")
                    print("->  4: Change attack period")
                    print("->  5: Change attack chance")
                    print("->  6: Change message delay")
                    print("->  7: Clear attacks")
                    print("->  8: Enable attack engine")
                    print("->  9: Disable attack engine")
                    print("-> 10: Return to main menu")
                    print("")

                    option = self._get_user_option()
                    if option == 1:
                        self.get_sensor(sensor_name).apply_attack(1)
                        print("'No Data Attack' applied.")
                    elif option == 2:
                        self.get_sensor(sensor_name).apply_attack(2)
                        print("'No Update Attack' applied.")
                    elif option == 3:
                        self.get_sensor(sensor_name).apply_attack(2**6)
                        print("'Message Delay Attack' applied.")
                    elif option == 4:
                        period = float(input("Enter new attack period: "))
                        self.get_sensor(sensor_name).set_attack_period(period)
                        print("Attack period changed to {}.".format(period))
                    elif option == 5:
                        chance = float(input("Enter new attack chance: "))
                        self.get_sensor(sensor_name).set_attack_chance(chance)
                        print("Attack chance changed to {}.".format(chance))
                    elif option == 6:
                        delay = float(input("Enter new message delay: "))
                        self.get_sensor(sensor_name).set_message_delay(delay)
                        print("Message delay changed to {}.".format(delay))
                    elif option == 7:
                        self.get_sensor(sensor_name).clear_attacks()
                        print("All attacks cleared.")
                    elif option == 8:
                        self.get_sensor(
                            sensor_name).set_attack_engine_enabled(True)
                        print("Attack engine enabled.")
                    elif option == 9:
                        self.get_sensor(
                            sensor_name).set_attack_engine_enabled(False)
                        print("Attack engine disabled")
                    elif option == 10:
                        break
                    else:
                        print("Wrong input! Aborting, going back to main menu...")
                        break

            elif option == 5:
                print("Thanks for trying Simutack, goodbye!")
                break
            elif option == -1:
                # SIGINT received -> shutdown quietly
                break
            else:
                print(
                    "Wrong input! Please enter an interger value in the range [1, 5].")
