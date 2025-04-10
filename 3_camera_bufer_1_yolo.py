#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ultralytics import YOLO
import cv2
import sys
import time

# Charger le modèle YOLO en mode détection
model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_canette_ncnn_model', task='detect')

device1 = "/dev/camera_droite"
device2 = "/dev/camera_gauche"
device3 = "/dev/camera_milieu_rex"
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

# Limiter le buffer pour chaque caméra
cap0.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap2.set(cv2.CAP_PROP_BUFFERSIZE, 1)
# Vérifier l'ouverture de chaque caméra
if not cap0.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 0")
    sys.exit()
if not cap1.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 1")
    sys.exit()
if not cap2.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 2")
    sys.exit()

# Créer trois fenêtres redimensionnables pour l'affichage des détections
cv2.namedWindow("Detection Camera 0", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 2", cv2.WINDOW_NORMAL)

while True:
    # Capture d'une image depuis chaque caméra
    ret0, frame0 = cap0.read()
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret0:
        print("Erreur lors de la capture de la caméra 0")
        break
    if not ret1:
        print("Erreur lors de la capture de la caméra 1")
        break
    if not ret2:
        print("Erreur lors de la capture de la caméra 2")
        break

    # Effectuer la détection sur chaque frame
    results0 = model(frame0)
    results1 = model(frame1)
    results2 = model(frame2)

    # Récupérer les images annotées avec les détections
    annotated_frame0 = results0[0].plot()
    annotated_frame1 = results1[0].plot()
    annotated_frame2 = results2[0].plot()

    # Afficher les images annotées dans leurs fenêtres respectives
    cv2.imshow("Detection Camera 0", annotated_frame0)
    cv2.imshow("Detection Camera 1", annotated_frame1)
    cv2.imshow("Detection Camera 2", annotated_frame2)

    print("__________________________________")

    # Quitter la boucle en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les caméras et fermer les fenêtres
cap0.release()
cap1.release()
cap2.release()
cv2.destroyAllWindows()

