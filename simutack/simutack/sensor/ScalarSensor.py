#!/usr/bin/python
#-*- coding: utf-8 -*-

from simutack.sensor.Sensor import Sensor
from simutack.attack.ScalarAttackEngine import ScalarAttackEngine

class ScalarSensor(Sensor, ScalarAttackEngine):
    def __init__(self):
        self.attack_engine = None

