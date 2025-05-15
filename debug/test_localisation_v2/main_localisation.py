#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ultralytics import YOLO
import cv2
import sys
import time
from setup_camera import setup_cameras
from localisation_tas import create_aruco_detector, process_frame_qr_only
from detection_yolo import process_frames
from localisation_tas_cam_haut import traitement_cam_haut
# Charger le modèle YOLO en mode détection
#model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_V2_ncnn_model', task='detect')

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
    #results0 = model(frame_droite)
    #results1 = model(frame_gauche)
    #results2 = model(frame_haut)

    objects_detected = process_frames([frame_droite, frame_gauche, frame_haut])  # Traiter les frames et les annoter directement
    #print("objects_detected", objects_detected)
    #print("type(objects_detected))", type(objects_detected))
    print("objects_detected[0]", objects_detected[0])
    #print("type(objects_detected[0])", type(objects_detected[0]))
    #print("objects_detected[1]", objects_detected[1])
    #print("type(objects_detected[1])", type(objects_detected[1]))


# 1. Utiliser process_frame_qr_only AVANT l'annotation YOLO
    annotated_frame_droite, tas_cam_droite  = process_frame_qr_only(frame_droite.copy(), "Camera droite", detector, boxes=objects_detected[0])
    annotated_frame_gauche, tas_cam_gauche = process_frame_qr_only(frame_gauche.copy(), "Camera gauche", detector, boxes=objects_detected[1])
    annotated_redresser_frame_haut, tas_cam_haut = traitement_cam_haut(frame_haut, detector, objects_detected[2])
    print("[Camera droite] État des tas :", tas_cam_droite)
    print("[Camera gauche] État des tas :", tas_cam_gauche)
    print("[Camera haut] État des tas :", tas_cam_haut)

    # 2. Puis appliquer les annotations YOLO sur l'image de sortie si tu veux les voir aussi
    #annotated_frame_droite = results0[0].plot(img=annotated_frame_droite)
    #annotated_frame_gauche = results1[0].plot(img=annotated_frame_gauche)
    #annotated_frame2 = results2[0].plot()  # pas traité pour l'instant
    

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

