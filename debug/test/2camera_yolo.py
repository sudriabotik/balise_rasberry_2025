#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ultralytics import YOLO
import cv2
import sys

# Charger le modèle YOLO en mode détection
model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_canette_ncnn_model', task='detect')

# Chemins des deux caméras
device1 = "/dev/camera_droite"
device2 = "/dev/camera_gauche"

# Initialisation des captures
cap0 = cv2.VideoCapture(device1)
cap1 = cv2.VideoCapture(device2)

# Configurer la résolution et le framerate
cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap0.set(cv2.CAP_PROP_FPS, 10)

cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap1.set(cv2.CAP_PROP_FPS, 10)

# Limiter le buffer pour chaque caméra\ ncap0.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap1.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Vérifier l'ouverture de chaque caméra
if not cap0.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra droite")
    sys.exit()
if not cap1.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra gauche")
    sys.exit()

# Créer deux fenêtres redimensionnables pour l'affichage des détections
cv2.namedWindow("Detection Caméra Droite", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Caméra Gauche", cv2.WINDOW_NORMAL)

while True:
    # Capture d'une image depuis chaque caméra
    ret0, frame0 = cap0.read()
    ret1, frame1 = cap1.read()

    if not ret0:
        print("Erreur lors de la capture de la caméra droite")
        break
    if not ret1:
        print("Erreur lors de la capture de la caméra gauche")
        break

    # Effectuer la détection sur chaque frame
    results0 = model(frame0)
    results1 = model(frame1)

    # Récupérer les images annotées avec les détections
    annotated_frame0 = results0[0].plot()
    annotated_frame1 = results1[0].plot()

    # Afficher les images annotées dans leurs fenêtres respectives
    cv2.imshow("Detection Caméra Droite", annotated_frame0)
    cv2.imshow("Detection Caméra Gauche", annotated_frame1)

    # Quitter la boucle en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les caméras et fermer les fenêtres
cap0.release()
cap1.release()
cv2.destroyAllWindows()