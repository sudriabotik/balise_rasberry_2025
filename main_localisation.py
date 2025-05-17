#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ultralytics import YOLO
import cv2
import sys
import time
from setup_camera import setup_cameras
from localisation_tas_coter import create_aruco_detector, process_frame_qr_only
from detection_yolo import process_frames
from localisation_tas_cam_haut import traitement_cam_haut
from ecrans_lcd import setup_lcd

lcd = setup_lcd()

detector = create_aruco_detector()

cap_droite, cap_gauche, cap_haut = setup_cameras()

# Créer trois fenêtres redimensionnables pour l'affichage des détections
cv2.namedWindow("Detection Camera 0", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 2", cv2.WINDOW_NORMAL)

while True:
    # Capture d'une image depuis chaque caméra
    ret0, frame_droite = cap_droite.read()
    ret1, frame_gauche = cap_gauche.read()
    ret2, frame_haut = cap_haut.read()

    objects_detected = process_frames([frame_droite, frame_gauche, frame_haut])  # Traiter les frames et les annoter directement

# 1. Utiliser process_frame_qr_only AVANT l'annotation YOLO
    annotated_frame_droite, tas_cam_droite  = process_frame_qr_only(frame_droite.copy(), "Camera droite", detector, boxes=objects_detected[0])
    annotated_frame_gauche, tas_cam_gauche = process_frame_qr_only(frame_gauche.copy(), "Camera gauche", detector, boxes=objects_detected[1])
    annotated_redresser_frame_haut, tas_cam_haut = traitement_cam_haut(frame_haut, detector, objects_detected[2])
    print("[Camera droite] État des tas :", tas_cam_droite)
    print("[Camera gauche] État des tas :", tas_cam_gauche)
    print("[Camera haut] État des tas :", tas_cam_haut)

    # Afficher les images annotées dans leurs fenêtres respectives
    cv2.imshow("Detection Camera 0", annotated_frame_droite)
    cv2.imshow("Detection Camera 1", annotated_frame_gauche)
    cv2.imshow("Detection Camera 2", annotated_redresser_frame_haut)

    print("__________________________________")

    # Quitter la boucle en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les caméras et fermer les fenêtres
cap_droite.release()
cap_gauche.release()
cap_haut.release()
cv2.destroyAllWindows()

