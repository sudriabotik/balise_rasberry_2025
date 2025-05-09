#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import sys
import time

# Configuration de l'exposition pour la caméra du haut
exposure_value = 60

def setup_camera_haut_exposure(cap):
    if not cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1):
        print("⚠️ Impossible d'activer le mode manuel d'exposition")
    else:
        print("AUTO_EXPOSURE =", cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))

    if not cap.set(cv2.CAP_PROP_EXPOSURE, float(exposure_value)):
        print("⚠️ Impossible de régler l'exposition")
    else:
        print("EXPOSURE =", cap.get(cv2.CAP_PROP_EXPOSURE))

def setup_cameras():
    cam_haut = "/dev/camera_haut"
    cap_haut = cv2.VideoCapture(cam_haut, cv2.CAP_V4L2)

    cap_haut.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap_haut.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap_haut.set(cv2.CAP_PROP_FPS, 30)
    cap_haut.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap_haut.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra haut")
        sys.exit()

    setup_camera_haut_exposure(cap_haut)
    return cap_haut

# Initialisation de la caméra du haut
cap = setup_cameras()

cv2.namedWindow("Caméra Haut", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la capture de l'image")
        break

    cv2.imshow("Caméra Haut", frame)
    key = cv2.waitKey(1)

    # Quitter avec 'q'
    if key == ord('q'):
        break

    # Ctrl + S pour sauvegarder
    elif key == 19:  # ASCII de Ctrl+S
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"photo_haut_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Image sauvegardée : {filename}")

cap.release()
cv2.destroyAllWindows()
