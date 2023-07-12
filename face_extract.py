#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import pandas as pd 
import os.path as osp 
from deepface import DeepFace
import cv2 
import textwrap

def adjust_rect(bbox, img_shape, ratio=0.2):
    # img_shape should be [w, h]
    # bbox = [top, right, bottom, left]

    rect = bbox
    top, right, bottom, left = rect  
    h = bottom - top
    w = right - left
    ntop = max(0, top - 2 * ratio * h)
    nbottom = min(img_shape[1], bottom + 2 * ratio * h)
    nleft = max(0, left - 2 * ratio * w)
    nright = min(img_shape[0], right + 2 * ratio * w)
    return [int(ntop), int(nright), int(nbottom), int(nleft)]

def ensure_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def getParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
        %prog is ....
        @Author: xutingfeng@big.ac.cn and shaoqi wang 
        Version: 1.0
        Example:
        ...

        """
        ),
    )
    parser.add_argument('-i', "--imageFolder", dest="imageFolder",help="img folder to parse and extract",type=str,required=True)
    parser.add_argument('-o', "--outputDir", dest="outputDir",help="output root dir, input folder will be keep at this dir and extract face in it, default .",type=str, default='.', required=False)
    parser.add_argument('-m', "--model", dest="model",help="face detect model, currently only retinaface, ssd, mtcnn , opencv and dlib and mediapipe need to pip install, defualt retinaface ",type=str, default='retinaface', required=False)
    parser.add_argument('-c', "--min_confidence", dest="min_confidence",help="min confidence to extract face, default 0.7",type=float, default=0.7, required=False)
    parser.add_argument('-e', "--expand_ratio", dest="expand_ratio",help="expand ratio to extract face, default 0.2",type=float, default=0.2, required=False)
    return parser

def detect_face(img_path, model = 'retinaface', min_confidence = 0.7):
    backends = [
        'opencv', 
        'ssd', 
        'dlib', 
        'mtcnn', 
        'retinaface', 
        'mediapipe',
        # 'yolov8',
        ]
    if model in backends:
        face_objs = DeepFace.extract_faces(img_path = img_path, 
                target_size = (256, 256), 
                detector_backend = model,
                enforce_detection=False,
                )
        
        # return [{}, {}, {}], each dict contain face, region, confidence
        face_obj = max(face_objs, key=lambda x: x["confidence"])
        
        # get confidence
        confidence = face_obj["confidence"]
        if confidence < min_confidence:
            return None
        
        # get bbox
        facial_area = face_obj["facial_area"]
        x, y, w, h = facial_area["x"], facial_area["y"], facial_area["w"], facial_area["h"]
        top, right, bottom, left = [y, x+w, y+h, x]
        bbox = [int(top), int(right), int(bottom), int(left)]

    else:
        raise ValueError(f"model {model} not in {backends}")

    return bbox, confidence


if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()

    IMG_PATH = args.imageFolder
    SAVE_PATH = args.outputDir

    #optional
    model = args.model
    min_confidence = args.min_confidence
    expand_ratio = args.expand_ratio

    print(f"IMG_PATH is {IMG_PATH}")
    print(f"SAVE_PATH is {SAVE_PATH}")
    print(f"model is {model}")
    print(f"min_confidence is {min_confidence}")
    print(f"expand_ratio is {expand_ratio}")

    if not osp.isdir(IMG_PATH):
        raise ValueError("IMG_PATH should be a folder dir not a file")
    rawRootDir, folderName = osp.split(IMG_PATH)
    
    SAVE_DIR = osp.join(SAVE_PATH, folderName)
    ensure_dirs(SAVE_DIR)

    pics = [i for i in os.listdir(IMG_PATH) if osp.isfile(abspath:= osp.join(IMG_PATH, i))]
    print(f"total {len(pics)} pics")
    # extract face
    logList = []

    for pic in pics:
        pic_path = osp.join(IMG_PATH, pic)
        print(f"running on {pic}")
        res = detect_face(img_path = pic_path, model = model, min_confidence = min_confidence)
        if res is not None:
            bbox, confidence = res
            rawImg = cv2.imread(pic_path)
            #cv2 shape is [h, w, c] => [w, h]
            rawImg_shape = [rawImg.shape[1], rawImg.shape[0]]
            adj_bbox = adjust_rect(bbox, rawImg.shape, ratio=expand_ratio)
            top, right, bottom, left = adj_bbox
            face_img_crop = rawImg[top:bottom, left:right]
            # save face img
            face_img_path = osp.join(SAVE_DIR, pic)
            cv2.imwrite(face_img_path, face_img_crop)
            # save log 
            logList.append({"img":pic, "bbox":adj_bbox, "model":model,"confidence":confidence, "expand_ratio":expand_ratio, "status":"success", "raw_w":rawImg_shape[0], "raw_h":rawImg_shape[1], "bbox_top":bbox[0], "bbox_right":bbox[1], "bbox_bottom":bbox[2], "bbox_left":bbox[3]})
        else:
            logList.append({"img":pic, "bbox":adj_bbox, "model":model,"confidence":0, "expand_ratio":expand_ratio, "status":"fail", "raw_w":rawImg_shape[0], "raw_h":rawImg_shape[1], "bbox_top":bbox[0], "bbox_right":bbox[1], "bbox_bottom":bbox[2], "bbox_left":bbox[3]})
            print(f"no face detected in {pic_path}")
    # save log
    pd.DataFrame(logList).to_csv(osp.join(SAVE_DIR, "log.csv"), index=False)
