#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@file        :myexperiment.py
@description :用于验证nona命令产生的map0000.tif,map0001.tif文件产生的是映射矩阵
@date        :2024/06/07 09:20:52
@author      :cuixingxing
@email       :cuixingxing150@gmail.com
@version     :1.0
"""


import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# 读取原始双鱼眼图像
srcFrontImage = cv2.imread("images/front00538.png")
srcBackImage = cv2.imread("images/back00538.png")

# 已经通过hugin控制点对齐，然后生成pto文件，创建mapX,mapY矩阵
os.system(
    "nona -c -o map -m TIFF_m back00538_front00538.pto images/front00538.png images/back00538.png"
)
map1X = cv2.imread("map0001_x.tif", cv2.IMREAD_UNCHANGED).astype("float32")
map1Y = cv2.imread("map0001_y.tif", cv2.IMREAD_UNCHANGED).astype("float32")
map2X = cv2.imread("map0000_x.tif", cv2.IMREAD_UNCHANGED).astype("float32")
map2Y = cv2.imread("map0000_y.tif", cv2.IMREAD_UNCHANGED).astype("float32")

dstImageFront = cv2.remap(srcFrontImage, map1X, map1Y, cv2.INTER_LINEAR)
dstImageBack = cv2.remap(srcBackImage, map2X, map2Y, cv2.INTER_LINEAR)

# 创建mask通道，用于给enblend程序做融合
maskFront = np.ones(srcFrontImage.shape[0:2], dtype="uint8") * 255
maskBack = np.ones(srcBackImage.shape[0:2], dtype="uint8") * 255
maskFront = cv2.remap(maskFront, map1X, map1Y, cv2.INTER_LINEAR)
maskBack = cv2.remap(maskBack, map2X, map2Y, cv2.INTER_LINEAR)

dstImageFront = np.concatenate((dstImageFront, maskFront[..., np.newaxis]), axis=-1)
dstImageBack = np.concatenate((dstImageBack, maskBack[..., np.newaxis]), axis=-1)

cv2.imwrite("images/frontMap.png", dstImageFront)  # 含有alpha通道的png图像
cv2.imwrite("images/backMap.png", dstImageBack)  # 含有alpha通道的png图像

# 调用enblend拼接
os.system("enblend -o images/out.png images/frontMap.png images/backMap.png")

cv2.imshow("mapxy", dstImageBack)

# img1 = cv2.imread("out0000.tif", cv2.IMREAD_UNCHANGED)
# img2 = cv2.imread("out0001.tif", cv2.IMREAD_UNCHANGED)
# cv2.imshow("", img1)
# cv2.imshow("merge", img1 + img2)
cv2.waitKey()
