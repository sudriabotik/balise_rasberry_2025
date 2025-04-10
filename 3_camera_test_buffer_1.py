#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import sys

device1 = "/dev/camera_droite"
device2 = "/dev/camera_gauche"
device3 = "/dev/camera_milieu"
cap0 = cv2.VideoCapture(device1)
cap1 = cv2.VideoCapture(device2)
cap2 = cv2.VideoCapture(device3)

# Limiter la taille du buffer pour chaque caméra
cap0.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap2.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Vérification de l'ouverture de chaque caméra
if not cap0.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 0")
    sys.exit()
if not cap1.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 1")
    sys.exit()
if not cap2.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 2")
    sys.exit()

# Création des fenêtres pour l'affichage
cv2.namedWindow("Camera 0", cv2.WINDOW_NORMAL)
cv2.namedWindow("Camera 1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Camera 2", cv2.WINDOW_NORMAL)

while True:
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

    cv2.imshow("Camera 0", frame0)
    cv2.imshow("Camera 1", frame1)
    cv2.imshow("Camera 2", frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap0.release()
cap1.release()
cap2.release()
cv2.destroyAllWindows()
