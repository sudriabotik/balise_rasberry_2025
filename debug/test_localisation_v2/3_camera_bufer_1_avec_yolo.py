#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ultralytics import YOLO
import cv2
import sys
import time
from setup_camera import setup_cameras
from localisation_V2 import create_aruco_detector, process_frame_qr_only


# Charger le modèle YOLO en mode détection
model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_V2_ncnn_model', task='detect')

detector = create_aruco_detector()

cap_droite, cap_gauche, cap_haut = setup_cameras()

# Créer trois fenêtres redimensionnables pour l'affichage des détections
cv2.namedWindow("Detection Camera 0", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 2", cv2.WINDOW_NORMAL)

while True:
    # Capture d'une image depuis chaque caméra
    ret0, frame0 = cap_droite.read()
    ret1, frame1 = cap_gauche.read()
    ret2, frame2 = cap_haut.read()

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

# 1. Utiliser process_frame_qr_only AVANT l'annotation YOLO
    annotated_frame0, valid0  = process_frame_qr_only(frame0.copy(), "Camera droite", detector, boxes=results0[0].boxes)
    annotated_frame1, valid1 = process_frame_qr_only(frame1.copy(), "Camera gauche", detector, boxes=results1[0].boxes)

    print("[Camera droite] État des tas :", valid0)
    print("[Camera gauche] État des tas :", valid1)

    # 2. Puis appliquer les annotations YOLO sur l'image de sortie si tu veux les voir aussi
    annotated_frame0 = results0[0].plot(img=annotated_frame0)
    annotated_frame1 = results1[0].plot(img=annotated_frame1)
    annotated_frame2 = results2[0].plot()  # pas traité pour l'instant
    

    # Afficher les images annotées dans leurs fenêtres respectives
    cv2.imshow("Detection Camera 0", annotated_frame0)
    cv2.imshow("Detection Camera 1", annotated_frame1)
    cv2.imshow("Detection Camera 2", annotated_frame2)

    print("__________________________________")

    # Quitter la boucle en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les caméras et fermer les fenêtres
cap_droite.release()
cap_gauche.release()
cap_haut.release()
cv2.destroyAllWindows()

