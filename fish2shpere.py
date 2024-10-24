#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@file        :fish2shpere.py
@description :把circle fisheye图像转换为equirectgular图像
@date        :2024/10/24 08:51:58
@author      :cuixingxing
@email       :cuixingxing150@gmail.com
@version     :1.0
"""

import numpy as np
import cv2


def fish2sphere(fisheye_image, options):
    hFOV = options.get("hFOV", 180)
    vFOV = options.get("vFOV", 180)
    cx = options.get("cx", fisheye_image.shape[1] / 2)
    cy = options.get("cy", fisheye_image.shape[0] / 2)
    radius = options.get(
        "radius", min(fisheye_image.shape[0] / 2, fisheye_image.shape[1] / 2)
    )
    outW = options.get("width", 2000)
    outH = options.get("height", 1000)
    xDeg = options.get("x", 0)
    yDeg = options.get("y", 0)
    zDeg = options.get("z", 0)
    smoothedges = options.get("smoothedges", False)

    # Step 1: Create theta and phi meshgrid
    theta = np.linspace(270, -90, outW)  # y轴为图像正中间，即摄像机光轴指向
    phi = np.linspace(-90, 90, outH)
    THETA, PHI = np.meshgrid(theta, phi)

    # Step 2: Convert spherical coordinates to Cartesian
    x = np.cos(np.radians(PHI)) * np.cos(np.radians(THETA))
    y = np.cos(np.radians(PHI)) * np.sin(np.radians(THETA))
    z = np.sin(np.radians(PHI))

    # Apply rotation
    A = np.array([x.flatten(), y.flatten(), z.flatten()])
    R = rotz(zDeg) @ roty(yDeg) @ rotx(xDeg)
    A = R @ A

    # Step 3: Map Cartesian to fisheye coordinates
    x = np.reshape(A[0, :], THETA.shape)
    y = np.reshape(A[1, :], THETA.shape)
    z = np.reshape(A[2, :], THETA.shape)

    theta = np.degrees(np.arctan2(z, x))
    phi = np.degrees(np.arctan2(np.sqrt(x**2 + z**2), y))
    rx = 2 * radius * phi / hFOV
    ry = 2 * radius * phi / vFOV

    # Step 4: Interpolate to get the output image
    mapX = cx + rx * np.cos(np.radians(theta))
    mapY = cy + ry * np.sin(np.radians(theta))

    panoImage = cv2.remap(
        fisheye_image,
        mapX.astype(np.float32),
        mapY.astype(np.float32),
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(100, 100, 100),
    )

    return panoImage, mapX, mapY


def rotx(deg):
    R = np.array(
        [
            [1, 0, 0],
            [0, np.cos(np.radians(deg)), -np.sin(np.radians(deg))],
            [0, np.sin(np.radians(deg)), np.cos(np.radians(deg))],
        ]
    )
    return R


def roty(deg):
    R = np.array(
        [
            [np.cos(np.radians(deg)), 0, np.sin(np.radians(deg))],
            [0, 1, 0],
            [-np.sin(np.radians(deg)), 0, np.cos(np.radians(deg))],
        ]
    )
    return R


def rotz(deg):
    R = np.array(
        [
            [np.cos(np.radians(deg)), -np.sin(np.radians(deg)), 0],
            [np.sin(np.radians(deg)), np.cos(np.radians(deg)), 0],
            [0, 0, 1],
        ]
    )
    return R


if __name__ == "__main__":
    fisheye1 = cv2.imread("images/front00538.png")
    fisheye2 = cv2.imread("images/back00538.png")

    options1 = {"width": 5760, "height": 2880, "z": 0}
    panoImage1, _, _ = fish2sphere(fisheye1, options1)

    options2 = {"width": 5760, "height": 2880, "z": 180}
    panoImage2, _, _ = fish2sphere(fisheye2, options2)

    cv2.imwrite("images/front.jpg", panoImage1)
    cv2.imwrite("images/back.jpg", panoImage2)

    # cv2.imshow("", panoImage)
    # cv2.waitKey()
