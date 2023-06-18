#!/usr/bin/python
#-*- coding: utf-8 -*-

from simutack.sensor.PointCloudSensor import PointCloudSensor

class RadarSensor(PointCloudSensor):
    def __init__(self):
        self.radar_measurement = None

    def set_horizontal_fov(self, fov):
        pass

    def set_vertical_fov(self, fov):
        pass

    def set_points_per_second(self, pps):
        pass

    def set_range(self, range):
        pass

    def get_horizontal_fov(self, ):
        pass

    def get_vertical_fov(self, ):
        pass

    def get_points_per_second(self, ):
        pass

    def get_range(self, ):
        pass

    def get_points(self, target_unit):
        pass

    def save_configuration(self, ):
        pass

    def load_configuration(self, config):
        pass

    def sensor_callback(self, data):
        pass

