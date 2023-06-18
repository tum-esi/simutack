#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
from simutack.core.SensorData import SensorData
from simutack.core.Unit import Unit


class PointCloudData(SensorData):
    """
    """

    def __init__(self, base_unit: Unit, point_cloud=[]) -> None:
        """
        """
        # Call constuctor of base class
        SensorData.__init__(self, base_unit)

        # Init class attributes
        self.point_cloud = point_cloud

    def get_points(self, target_unit: Unit = Unit.BASE_UNIT):
        return self.point_cloud

    def set_points(self, points, target_unit: Unit = Unit.BASE_UNIT):
        self.point_cloud = points

    def add_points(self, points, target_unit: Unit = Unit.BASE_UNIT):
        pass

    def clear_points(self):
        pass
