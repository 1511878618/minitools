#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from paddleocr import PaddleOCR
import os.path as osp
import pandas as pd 
import argparse
import textwrap

import warnings

warnings.filterwarnings("ignore")
# 读取图像
def extract_yellow(imagePath, outputPath):
    image = cv2.imread(imagePath)

    imageName=osp.splitext(osp.split(imagePath)[-1])[0]

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # 定义黄色的HSV颜色范围
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([40, 255, 255])
    # 创建一个掩码，其中黄色区域为白色，其他区域为黑色
    mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
    # 寻找黄色区域的轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 如果存在黄色区域的轮廓，则绘制边框并保存区域
    if len(contours) > 0:
        # 找到最大的黄色区域轮廓
        max_contour = max(contours, key=cv2.contourArea)
        # 计算最大轮廓的边界框坐标
        x, y, w, h = cv2.boundingRect(max_contour)
        # 绘制边框
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # 裁剪并保存黄色区域
        yellow_area = image[y:y + h, x:x + w]
        cv2.imwrite(osp.join(outputPath,f"{imageName}.jpg"), yellow_area)
        return yellow_area, max_contour
    else:
        return None


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog extract yellow and ocr
        @Author:xutingfeng@big.ac.cn

        Version: 1.0
        extract_yellow_ocr.py -i photo/DSC00012.JPG -o output 

        """
        ),
    )

    parser.add_argument(
        "-i", dest="imagePath", type=str, default=None, help="image path.")
    parser.add_argument("-o", dest="outputPath", type=str, default=None, help="output path.")
    return parser

if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()


    imagePath=args.imagePath
    outputPath=args.outputPath
    imageName=osp.splitext(osp.split(imagePath)[-1])[0]
    image,max_contour = extract_yellow(imagePath, outputPath)
    area = cv2.contourArea(max_contour)

    if image is not None:
        ocr = PaddleOCR(use_angle_cls=True, lang="ch",use_gpu=False)  # need to run only once to download and load model into memory
        result = ocr.ocr(image, cls=True)
        if len(result[0]) >0:  # result: [[]]
            pd.DataFrame([i[1] for i in result[0]], columns=["string", "score"]).to_csv(osp.join(outputPath,f"{imageName}.csv"), index=False)
        else:
            if area > 20000:
                pd.DataFrame().to_csv(osp.join(outputPath,f"{imageName}.csv"), index=False)    