#!/usr/bin/python
#-*- coding: utf-8 -*-

class LidarData:
    def __init__(self, x: float, y: float, z: float, i: float) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.intensity = i

