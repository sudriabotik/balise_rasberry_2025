#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO + ArUco (20–23) + diagonales par caméra + indication "tas" + enregistrement
"""

import cv2
import cv2.aruco as aruco
import numpy as np
from ultralytics import YOLO
from shapely.geometry import LineString
from datetime import datetime
import sys

# === Charger le modèle YOLO ===
model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_canette_ncnn_model', task='detect')

# === Initialiser les caméras ===
devices = ["/dev/camera_droite", "/dev/camera_gauche", "/dev/camera_haut"]
caps = [cv2.VideoCapture(dev) for dev in devices]
for cap, fps in zip(caps, [30, 10, 30]):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not all(cap.isOpened() for cap in caps):
    print("Erreur : Impossible d'ouvrir une des caméras")
    sys.exit()

# === Initialisation enregistrement vidéo ===
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
outs = [
    cv2.VideoWriter(f'camera0_{timestamp}.mp4', fourcc, 30.0, (640, 480)),
    cv2.VideoWriter(f'camera1_{timestamp}.mp4', fourcc, 10.0, (640, 480)),
    cv2.VideoWriter(f'camera2_{timestamp}.mp4', fourcc, 30.0, (640, 480))
]

# === Fenêtres d'affichage ===
names = ["Camera 0", "Camera 1", "Camera 2"]
for name in names:
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)

# === Détection ArUco (ID 20 à 23 uniquement) ===
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)
ids_autorises = {20, 21, 22, 23}
seuil_distance = 30

# === Boucle principale ===
while True:
    for cap, out, name in zip(caps, outs, names):
        ret, frame = cap.read()
        if not ret:
            print(f"Erreur lecture {name}")
            continue

        image = frame.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray_enhanced = clahe.apply(gray)

        corners, ids, _ = detector.detectMarkers(gray_enhanced)
        diagonales = []
        associations = []
        filtered_corners = []
        filtered_ids = []

        # === Traitement des ArUco ===
        if ids is not None:
            for i, marker_corners in enumerate(corners):
                marker_id = int(ids[i][0])
                if marker_id not in ids_autorises:
                    continue

                c = marker_corners[0]
                cx = int(sum(p[0] for p in c) / 4)
                cy = int(sum(p[1] for p in c) / 4)
                associations.append((cx, cy))
                filtered_corners.append(marker_corners)
                filtered_ids.append([marker_id])

                h, w = image.shape[:2]
                diag_len = int(np.hypot(w, h)) + 100
                diag_45 = ((cx - diag_len, cy - diag_len), (cx + diag_len, cy + diag_len))
                diag_135 = ((cx - diag_len, cy + diag_len), (cx + diag_len, cy - diag_len))

                if name == "Camera 1":  # gauche : diagonale verte uniquement
                    diagonales.append(LineString(diag_45))
                    cv2.line(image, diag_45[0], diag_45[1], (0, 255, 0), 1)
                elif name == "Camera 0":  # droite : diagonale rose uniquement
                    diagonales.append(LineString(diag_135))
                    cv2.line(image, diag_135[0], diag_135[1], (255, 0, 255), 1)
                else:  # haut : les deux
                    diagonales.append(LineString(diag_45))
                    diagonales.append(LineString(diag_135))
                    cv2.line(image, diag_45[0], diag_45[1], (0, 255, 0), 1)
                    cv2.line(image, diag_135[0], diag_135[1], (255, 0, 255), 1)

        if filtered_ids:
            filtered_ids = np.array(filtered_ids, dtype=np.int32)
            image = aruco.drawDetectedMarkers(image, filtered_corners, filtered_ids)
            for i, marker_id in enumerate(filtered_ids):
                center = tuple(map(int, np.mean(filtered_corners[i][0], axis=0)))
                cv2.putText(image, f"ID {marker_id[0]}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # === Détection YOLO ===
        results = model(image)
        annotated_image = results[0].plot()

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            box_line = LineString([(x1, y1), (x2, y2)])

            for diag in diagonales:
                if diag.distance(box_line) < seuil_distance:
                    cv2.putText(annotated_image, "tas", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    break

        # === Affichage et enregistrement ===
        cv2.imshow(name, annotated_image)
        out.write(annotated_image)

    # === Quitter avec la touche "q" ===
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# === Libération des ressources ===
for cap in caps:
    cap.release()
for out in outs:
    out.release()
cv2.destroyAllWindows()
