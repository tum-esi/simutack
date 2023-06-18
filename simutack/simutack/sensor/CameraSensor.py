#!/usr/bin/python
# -*- coding: utf-8 -*-

# Avoid cyclic imports while using type hints
from __future__ import annotations

# Imports
import numpy as np
import math

import simplejpeg
import base64
import copy
import cv2

import carla

from simutack.util.Logger import logger
from simutack.core.Unit import Unit
from simutack.core.AnnotationData import AnnotationData
from simutack.core.ImageData import ImageData
from simutack.sensor.Sensor import Sensor
from simutack.attack.ImageAttackEngine import ImageAttackEngine


class CameraSensor(Sensor):
    """
    """

    def __init__(self, controller: DataController, name: str, update_interval: float = 1.0) -> None:
        """Constructor"""
        # Call constructor of base class
        Sensor.__init__(self, controller, name, 'body', update_interval)

        # Init class attributes
        self.type = 'camera'
        self.attack_engine = ImageAttackEngine()

        # Create IMU sensor in carla world
        self.carla_blueprint = self.controller.get_blueprint_library().find('sensor.camera.rgb')
        self.carla_blueprint.set_attribute(
            'sensor_tick', f'{self.update_interval}')
        self.carla_transform = carla.Transform(carla.Location(
            x=1.5, y=0.0, z=2.4), carla.Rotation(0, 0, 0))
        self.respawn_sensor()
        self.set_enabled(True)

        self.image_list = []


        # Set up the set of bounding boxes from the level
        # We filter for traffic lights and traffic signs
        self.bounding_box_set = self.controller.get_world().get_level_bbs(carla.CityObjectLabel.TrafficLight)
        self.bounding_box_set.extend(self.controller.get_world().get_level_bbs(carla.CityObjectLabel.TrafficSigns))

        # Remember the edge pairs
        self.edges = [[0,1], [1,3], [3,2], [2,0], [0,4], [4,5], [5,1], [5,7], [7,6], [6,4], [6,2], [7,3]]


    def set_fov(self, fov: float) -> None:
        self.update_sensor_attribute('fov', f'{fov}')

    def set_image_width(self, width: int) -> None:
        self.update_sensor_attribute('image_size_x', f'{width}')

    def set_image_height(self, height: int) -> None:
        self.update_sensor_attribute('image_size_y', f'{height}')

    def set_position(self, position: list) -> None:
        # Update position
        self.carla_transform.location = carla.Location(
            x=position[0], y=position[1], z=position[2])
        # Avoid direct manipulation via set_transform() which may cause memory access violation
        self.pending_respawn = True
        # self.respawn_sensor()

    def set_rotation(self, rotation: list) -> None:
        """
        [roll, pitch, yaw]
        """
        # Update rotation
        self.carla_transform.rotation = carla.Rotation(
            roll=rotation[0], pitch=rotation[1], yaw=rotation[2])
        # Avoid direct manipulation via set_transform() which may cause memory access violation
        self.pending_respawn = True

    def get_fov(self) -> float:
        return self.carla_blueprint.get_attribute('fov').as_float()

    def get_image_width(self) -> int:
        return self.carla_blueprint.get_attribute('image_size_x').as_int()

    def get_image_height(self) -> int:
        return self.carla_blueprint.get_attribute('image_size_y').as_int()

    def get_position(self) -> carla.Location:
        return self.carla_transform.location

    def get_rotation(self) -> carla.Rotation:
        return self.carla_transform.rotation




    def get_image_point(self, loc, K, w2c):
        # Calculate 2D projection of 3D coordinate

        # Format the input coordinate (loc is a carla.Position object)
        point = np.array([loc.x, loc.y, loc.z, 1])
        # transform to camera coordinates
        point_camera = np.dot(w2c, point)

        # New we must change from UE4's coordinate system to an "standard"
        # (x, y ,z) -> (y, -z, x)
        # and we remove the fourth componebonent also
        point_camera = [point_camera[1], -point_camera[2], point_camera[0]]

        # now project 3D->2D using the camera matrix
        point_img = np.dot(K, point_camera)
        # normalize
        point_img[0] /= point_img[2]
        point_img[1] /= point_img[2]

        return point_img[0:2]

    def build_projection_matrix(self, w, h, fov):
        focal = w / (2.0 * np.tan(fov * np.pi / 360.0))
        K = np.identity(3)
        K[0, 0] = K[1, 1] = focal
        K[0, 2] = w / 2.0
        K[1, 2] = h / 2.0
        return K

    def sensor_callback(self, data: carla.SensorData) -> None:
        # Check if we want to process this update (only relevant if server rate is higher than user selected update rate)
        if (data.frame >= self.next_frame) and self.is_enabled():
            # Compute next frame when sensor data should be received
            self.next_frame = data.frame + \
                int(math.ceil(self.update_interval /
                              self.controller.get_world_step()))

            # Get data
            image = ImageData(Unit.IMAGE_RGB, data.frame, data.timestamp,
                              np.frombuffer(data.raw_data, dtype=np.uint8).reshape(
                                  self.get_image_height(), self.get_image_width(), 4))  # 32-bit BRGA -> [height, width, 4] array

            # self.image_list.append({'frame': data.frame, 'data': copy.copy(bytes(data.raw_data))})
            # if len(self.image_list) > 20:
            #     for im in self.image_list:
            #         with open('_out/{}/{:06d}.jpg'.format(self.name, im['frame']), "wb") as f:
            #             f.write(simplejpeg.encode_jpeg(
            #                 image=np.frombuffer(im['data'], dtype=np.uint8).reshape(
            #                       self.get_image_height(), self.get_image_width(), 4),
            #                 colorspace='BGRA',
            #             ))
            #     self.image_list.clear()

            # Attack data
            # image = self.attack_engine.attack_data(image, vehicle_transform)


            try:
                vehicle_transform = self.controller.get_vehicle().get_transform()
                camera_transform = self.carla_actor.get_transform() # vehicle + local sensor offset
            except:
                vehicle_transform = None
                camera_transform = None
            image = self.attack_engine.attack_data(image, vehicle_transform, camera_transform, data.fov)




            # img = image.get_image()

            # # Get the camera matrix 
            # world_2_camera = np.array(camera_transform.get_inverse_matrix())

            # # Get the attributes from the camera
            # image_w = self.carla_blueprint.get_attribute("image_size_x").as_int()
            # image_h = self.carla_blueprint.get_attribute("image_size_y").as_int()
            # fov = self.carla_blueprint.get_attribute("fov").as_float()

            # # Calculate the camera projection matrix to project from 3D -> 2D
            # K = self.build_projection_matrix(image_w, image_h, fov)

            # print(f"working: \n{K}")

            # for bb in self.bounding_box_set:
            #     # Filter for distance from ego vehicle
            #     if bb.location.distance(vehicle_transform.location) < 3:

            #         # Calculate the dot product between the forward vector
            #         # of the vehicle and the vector between the vehicle
            #         # and the bounding box. We threshold this dot product
            #         # to limit to drawing bounding boxes IN FRONT OF THE CAMERA
            #         forward_vec = vehicle_transform.get_forward_vector()
            #         ray = bb.location - vehicle_transform.location

            #         print(f"Loc: {bb.location}, Loc_world: {bb.get_world_vertices(carla.Transform())[0]}")

            #         v1 = np.array([forward_vec.x, forward_vec.y, forward_vec.z])
            #         v2 = np.array([ray.x, ray.y, ray.z])
            #         if np.dot(v1, v2) > 1:
            #             # Cycle through the vertices
            #             verts = [v for v in bb.get_world_vertices(carla.Transform())]
            #             for edge in self.edges:
            #                 # Join the vertices into edges
            #                 p1 = self.get_image_point(verts[edge[0]], K, world_2_camera)
            #                 p2 = self.get_image_point(verts[edge[1]], K, world_2_camera)
            #                 print(f"Edge: {verts[edge[0]]}, {verts[edge[1]]}")
            #                 # Draw the edges into the camera output
            #                 cv2.line(img, (int(p1[0]),int(p1[1])), (int(p2[0]),int(p2[1])), (0,0,255, 255), 1)




            # Annotate data
            annotations = AnnotationData(self.attack_engine.is_enabled(
            ), self.attack_engine.get_active_attacks_list())

            # Put data in queue for further processing
            if image:
                # image_jpg = simplejpeg.encode_jpeg(
                #     image=image.get_image(),
                #     colorspace='BGRA',
                # )
                # image_base64 = base64.b64encode(image_jpg).decode('utf-8')
                # self.data_queue.put(image_base64)

                self.data_queue.put((image, annotations))

    def save_configuration(self):
        pass

    def load_configuration(self, config):
        pass
