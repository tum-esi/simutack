#!/usr/bin/python
# -*- coding: utf-8 -*-

import pickle
import cv2
import numpy as np
import carla
import math


from simutack.attack.AttackEngine import AttackEngine
from simutack.core.ImageData import ImageData


class ImageAttackEngine(AttackEngine):
    def __init__(self) -> None:
        # Call constructor of base class
        AttackEngine.__init__(self)

        # Loading the masks
        self.mask = None

        with open("simutack/attack/mask.bin", "rb") as fp:
            self.mask = pickle.load(fp)

    def no_update_attack(self, data):
        # Use previous data but with current timestamp/frame
        data.image = self.previous_data.image
        return data

    def camera_blinding_attack(self, data, vehicle_transform, camera_transform, fov):
        # https://carla.readthedocs.io/en/latest/tuto_G_bounding_boxes/
        img_shape = data.image.shape    # (y,x) Different order!
        mask_shape = self.mask.shape
        #center = (img_shape[0] // 2, img_shape[1] // 2)
        mask = np.copy(self.mask)
        img = np.copy(data.image)

        # Image params
        w = img_shape[1]    # (y,x) order
        h = img_shape[0]    # (y,x) order

        # Get the world to camera matrix
        world_2_camera = np.array(camera_transform.get_inverse_matrix())

        # Calculate the camera projection matrix to project from 3D -> 2D
        focal = w / (2.0 * np.tan(fov * np.pi / 360.0))
        K = np.identity(3)
        K[0, 0] = K[1, 1] = focal
        K[0, 2] = w / 2.0
        K[1, 2] = h / 2.0

        # Position of the light source
        attack_location = carla.Location(
            x=161.389999, y=309.049988, z=2.230000)
        # attack_location = carla.Location(
        #     x=159.389999, y=309.049988, z=2.230000)

        # Calculate 2D projection of 3D coordinate
        # Format the input coordinate (loc is a carla.Position object)
        point = np.array(
            [attack_location.x, attack_location.y, attack_location.z, 1])
        # transform to camera coordinates
        point_camera = np.dot(world_2_camera, point)

        # Now we must change from UE4's coordinate system to a "standard"
        # (x, y ,z) -> (y, -z, x)
        # and we remove the fourth component also
        point_camera = [point_camera[1], -point_camera[2], point_camera[0]]

        # Now project 3D->2D using the camera matrix
        point_img = np.dot(K, point_camera)

        # Normalize coordinates
        point_img[0] /= point_img[2]
        point_img[1] /= point_img[2]

        # Convert to int
        x_2d = int(point_img[0])
        y_2d = int(point_img[1])

        # Debug output
        print(f"x: {x_2d:6d}, y: {y_2d:6d}")

        # Get distance from attack location to ego vehicle
        distance = vehicle_transform.location.distance(attack_location)

        # Scale mask
        scale_factor = min(15.0 / distance, 1.0)    # original: 50.0
        size = (int(mask_shape[1]*scale_factor),
                int(mask_shape[0]*scale_factor))
        mask_scaled = cv2.resize(mask, size, interpolation=cv2.INTER_AREA)
        mask_scaled_shape = mask_scaled.shape

        # Convert from gray to color image
        mask_scaled = cv2.merge(
            (mask_scaled, mask_scaled, mask_scaled, mask_scaled))
        mask_scaled_shape = mask_scaled.shape

        # Determine regions of interest
        roi_img = [np.arange(y_2d-mask_scaled_shape[0]//2, y_2d-mask_scaled_shape[0]//2+mask_scaled_shape[0]),
                   np.arange(x_2d-mask_scaled_shape[1]//2, x_2d-mask_scaled_shape[1]//2+mask_scaled_shape[1])]    # (y,x)
        roi_msk = [np.arange(mask_scaled_shape[0]), np.arange(
            mask_scaled_shape[1])]                              # (y,x)

        # print(f"ROI vor img: {roi_img}, msk{roi_msk}")

        # Top part clipped
        if (roi_img[0][0] < 0):
            if (abs(roi_img[0][0]) < mask_scaled_shape[0]):
                roi_msk[0] = roi_msk[0][abs(roi_img[0][0]):]
                roi_img[0] = roi_img[0][abs(roi_img[0][0]):]    # Limit region
            else:   # Out of range
                return data
        # Bottom part clipped
        if (roi_img[0][-1] > img_shape[0]):
            if ((roi_img[0][-1] - mask_scaled_shape[0]) < img_shape[0]):    # Limit region
                roi_msk[0] = roi_msk[0][:-(roi_img[0][-1] - img_shape[0] + 1)]
                roi_img[0] = roi_img[0][:-(roi_img[0][-1] - img_shape[0] + 1)]
            else:   # Out of range
                return data
        # Left part clipped
        if (roi_img[1][0] < 0):
            if (abs(roi_img[1][0]) < mask_scaled_shape[1]):     # Limit region
                roi_msk[1] = roi_msk[1][abs(roi_img[1][0]):]
                roi_img[1] = roi_img[1][abs(roi_img[1][0]):]
            else:   # Out of range
                return data
        # Right part clipped
        if (roi_img[1][-1] > img_shape[1]):
            print(f"x_right: {roi_img[1][-1]}, mask_width: {mask_scaled_shape[1]}, img_width: {img_shape[1]}")
            if ((roi_img[1][-1] - mask_scaled_shape[1]) < img_shape[1]):    # Limit region
                roi_msk[1] = roi_msk[1][:-(roi_img[1][-1] - img_shape[1] + 1)]
                roi_img[1] = roi_img[1][:-(roi_img[1][-1] - img_shape[1] + 1)]
            else:   # Out of range
                return data

        # Draw the mask at the computed location

        # size = 25
        # if (y_2d-size >= 0) and (y_2d+size < img_shape[0]) and (x_2d-size >= 0) and (x_2d+size < img_shape[1]):
        #     mask[y_2d-size:y_2d+size, x_2d-size:x_2d+size, :] = 255
        # cv2.line(img, (int(p1[0]),int(p1[1])), (int(p2[0]),int(p2[1])), (0,0,255, 255), 1)
        # image = cv2.rectangle(data.image, (x_2d-(size+5), y_2d-(size+5)), (x_2d+(size+5), y_2d+(size+5)), (0,255,0, 255), 4)
        # if (y_2d-mask_scaled_shape[0]//2 >= 0) and (y_2d+mask_scaled_shape[0]//2 < img_shape[0]) and (x_2d-mask_scaled_shape[1]//2 >= 0) and (x_2d+mask_scaled_shape[1]//2 < img_shape[1]):
        #     data.image = cv2.add(data.image[y_2d-mask_scaled_shape[0]//2:y_2d+mask_scaled_shape[0]//2, x_2d-mask_scaled_shape[1]//2:x_2d+mask_scaled_shape[1]//2, :], mask)

        try:
            # print(f"ROI img: {roi_img}, msk{roi_msk}")
            # print(f"Shape img: {data.image.shape}, msk: {mask_scaled.shape}")
            #rows = data.image[roi_img[0]][:,roi_img[1],:]
            #columns = data.image[roi_img[1]][:,roi_img[0],:]

            # print(f"Shap2 img: {data.image[roi_img[0]][:, roi_img[1], :].shape}, msk: {mask_scaled[roi_msk[0]][:, roi_msk[1], :].shape}")
            # print("---")
            # tmp = cv2.add(
            #     img[roi_img[0]][:, roi_img[1], :], mask_scaled[roi_msk[0]][:, roi_msk[1], :])
            # img[roi_img[0]][:, roi_img[1], :] = tmp
            # img[roi_img[0]][:400] = 255 # --> no
            # img[roi_img[0],:400] = 255 # --> yes
            # img[roi_img[0],roi_img[1]] = 255 # --> no
            # img[roi_img[0], roi_img[1][0]:roi_img[1][-1]] = 255  # --> yes

            img[roi_img[0], roi_img[1][0]:(roi_img[1][-1]+1), :] = cv2.add(
                img[roi_img[0]][:, roi_img[1], :], mask_scaled[roi_msk[0]][:, roi_msk[1], :])

            # print(img[roi_img[0]][:, roi_img[1], :].shape)
            data.image = img
            # data.image[roi_img[0]][:, roi_img[1], :] = cv2.add(
            #     data.image[roi_img[0]][:, roi_img[1], :], mask_scaled[roi_msk[0]][:, roi_msk[1], :])
        except Exception as e:
            print(e)

        return data
