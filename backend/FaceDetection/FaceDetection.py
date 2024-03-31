#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2024-03-30 9:38 p.m.
# @Author  : FywOo02
# @FileName: FaceDetection.py
# @Software: PyCharm


import cv2
from google.cloud import vision
import io
import time
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'InterviewHelper.json'
client = vision.ImageAnnotatorClient()

def detect_negative_emotions(image_path):
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.face_detection(image=image)
    faces = response.face_annotations
    print('Faces detected:', len(faces))

    for i, face in enumerate(faces):
        print(f'Face #{i + 1}:')
        if face.anger_likelihood != vision.Likelihood.VERY_UNLIKELY:
            print(f'Anger: {face.anger_likelihood.name}')
        if face.sorrow_likelihood != vision.Likelihood.VERY_UNLIKELY:
            print(f'Sorrow: {face.sorrow_likelihood.name}')

    if response.error.message:
        raise Exception(f'{response.error.message}')

def capture_image(image_path):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cv2.imwrite(image_path, frame)
    cap.release()

while True:
    timestamp = int(time.time())
    image_path = f'image_{timestamp}.jpg'
    capture_image(image_path)
    detect_negative_emotions(image_path)
    os.remove(image_path)
    time.sleep(3)  # Wait for 5 seconds before capturing the next image
