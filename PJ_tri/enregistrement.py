#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 12:50:36 2025

@author: root
"""

from ultralytics import YOLO
import cv2
import sys
from datetime import datetime

# Charger le modèle YOLO
model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_canette_ncnn_model', task='detect')

device1 = "/dev/camera_droite"
device2 = "/dev/camera_gauche"
device3 = "/dev/camera_haut"

cap0 = cv2.VideoCapture(device1)
cap1 = cv2.VideoCapture(device2)
cap2 = cv2.VideoCapture(device3)

cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap0.set(cv2.CAP_PROP_FPS, 10)
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap1.set(cv2.CAP_PROP_FPS, 10)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap2.set(cv2.CAP_PROP_FPS, 30)

cap0.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap2.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap0.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 0")
    sys.exit()
if not cap1.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 1")
    sys.exit()
if not cap2.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 2")
    sys.exit()

# Création des fenêtres d'affichage
cv2.namedWindow("Detection Camera 0", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 2", cv2.WINDOW_NORMAL)

# Préparer les VideoWriter pour enregistrer les vidéos
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

out0 = cv2.VideoWriter(f'camera0_{timestamp}.mp4', fourcc, 10.0, (960, 720))
out1 = cv2.VideoWriter(f'camera1_{timestamp}.mp4', fourcc, 10.0, (960, 720))
out2 = cv2.VideoWriter(f'camera2_{timestamp}.mp4', fourcc, 30.0, (640, 480))

while True:
    ret0, frame0 = cap0.read()
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret0 or not ret1 or not ret2:
        print("Erreur lors de la capture d'une des caméras")
        break

    results0 = model(frame0)
    results1 = model(frame1)
    results2 = model(frame2)

    annotated_frame0 = results0[0].plot()
    annotated_frame1 = results1[0].plot()
    annotated_frame2 = results2[0].plot()

    # Affichage
    cv2.imshow("Detection Camera 0", annotated_frame0)
    cv2.imshow("Detection Camera 1", annotated_frame1)
    cv2.imshow("Detection Camera 2", annotated_frame2)

    # Écriture dans les fichiers vidéo
    out0.write(annotated_frame0)
    out1.write(annotated_frame1)
    out2.write(annotated_frame2)

    print("__________________________________")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libération
cap0.release()
cap1.release()
cap2.release()
out0.release()
out1.release()
out2.release()
cv2.destroyAllWindows()
