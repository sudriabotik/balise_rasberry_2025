#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ultralytics import YOLO
import cv2
import sys
import time

# Charger le modèle YOLO en mode détection
model = YOLO('/home/ubuntu/Documents/yolo/test/best_canette_ncnn_model', task='detect')

# Ouvrir la caméra (utilisez l'index approprié, par exemple 0)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra")
    sys.exit()

# Créer une fenêtre redimensionnable pour l'affichage
cv2.namedWindow("Detection Camera", cv2.WINDOW_NORMAL)

while True:
    loop_start = time.time()  # Début de la boucle

    # 1. Capture d'une image depuis la caméra
    ret, frame = cap.read()
    capture_time = time.time() - loop_start

    if not ret:
        print("Erreur lors de la capture de l'image")
        break

    # 2. Détection avec YOLO
    detection_start = time.time()
    results = model(frame)  # Vous pouvez ajouter imgsz=1200 si nécessaire, par ex. model(frame, imgsz=1200)
    detection_time = time.time() - detection_start

    # 3. Annotation des résultats sur l'image
    annotation_start = time.time()
    annotated_frame = results[0].plot()
    annotation_time = time.time() - annotation_start

    # 4. Affichage de l'image annotée
    display_start = time.time()
    cv2.imshow("Detection Camera", annotated_frame)
    display_time = time.time() - display_start

    # Afficher les temps écoulés pour chaque étape dans la console
    print(f"Temps de capture : {capture_time:.3f} s, "
          f"Temps de détection : {detection_time:.3f} s, "
          f"Temps d'annotation : {annotation_time:.3f} s, "
          f"Temps d'affichage : {display_time:.3f} s")

    # Quitter la boucle en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la caméra et fermer la fenêtre
cap.release()
cv2.destroyAllWindows()
