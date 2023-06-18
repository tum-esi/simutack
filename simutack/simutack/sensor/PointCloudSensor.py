#!/usr/bin/python
#-*- coding: utf-8 -*-

from simutack.sensor.Sensor import Sensor

class PointCloudSensor(Sensor):
    def __init__(self):
        self.attack_engine = None

