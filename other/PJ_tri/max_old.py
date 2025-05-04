#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO + ArUco (20–23) + diagonales par caméra + tas nommés selon mapping spécifique
"""

import cv2
import cv2.aruco as aruco
import numpy as np
from ultralytics import YOLO
from shapely.geometry import LineString, box as shapely_box
from datetime import datetime
import sys

# === Modèle YOLO ===
model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_canette_ncnn_model', task='detect')

# === Configuration des caméras ===
devices = ["/dev/camera_droite", "/dev/camera_gauche", "/dev/camera_haut"]
names = ["Camera droite", "Camera gauche", "Camera milieu"]
fps_list = [30, 10, 30]

caps = [cv2.VideoCapture(dev) for dev in devices]
for cap, fps in zip(caps, fps_list):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not all(cap.isOpened() for cap in caps):
    print("Erreur : Une caméra n'a pas pu être ouverte.")
    sys.exit()

# === Enregistrement vidéo ===
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
outs = [cv2.VideoWriter(f'camera{i}_{timestamp}.mp4', fourcc, fps, (640, 480)) for i, fps in enumerate(fps_list)]

# === Fenêtres OpenCV ===
for name in names:
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)

# === ArUco setup ===
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
detector = aruco.ArucoDetector(aruco_dict, aruco.DetectorParameters())
ids_autorises = {20, 21, 22, 23}
seuil_distance = 30

# === Mapping ArUco → Nom de tas ===
aruco_to_tas = {
    20: "tas_0",
    21: "tas_1",
    22: "tas_2",
    23: "tas_3"
}

# === Boucle principale ===
while True:
    for cam_index, (cap, out, name) in enumerate(zip(caps, outs, names)):
        ret, frame = cap.read()
        if not ret:
            print(f"Erreur de lecture sur {name}")
            continue

        image = frame.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.createCLAHE(3.0, (8, 8)).apply(gray)

        # === Détection ArUco ===
        corners, ids, _ = detector.detectMarkers(gray)
        diagonales = []
        diag_labels = []

        if ids is not None:
            for i, marker_corners in enumerate(corners):
                marker_id = int(ids[i][0])
                if marker_id not in aruco_to_tas:
                    continue

                pts = marker_corners[0]
                cx = int(np.mean(pts[:, 0]))
                cy = int(np.mean(pts[:, 1]))
                diag_len = int(np.hypot(*image.shape[:2])) + 100
                label = aruco_to_tas[marker_id]

                # Détermination des diagonales par caméra
                diag_data = []
                if name == "Camera gauche":
                    diag_data.append(((cx - diag_len, cy - diag_len), (cx + diag_len, cy + diag_len), (0, 255, 0)))
                elif name == "Camera droite":
                    diag_data.append(((cx - diag_len, cy + diag_len), (cx + diag_len, cy - diag_len), (255, 0, 255)))
                else:
                    diag_data.append(((cx - diag_len, cy - diag_len), (cx + diag_len, cy + diag_len), (0, 255, 0)))
                    diag_data.append(((cx - diag_len, cy + diag_len), (cx + diag_len, cy - diag_len), (255, 0, 255)))

                for (p1, p2, color) in diag_data:
                    diagonales.append(LineString([p1, p2]))
                    diag_labels.append(label)
                    cv2.line(image, p1, p2, color, 1)

            # Affichage des ArUco
            image = aruco.drawDetectedMarkers(image, corners, ids)
            for i, marker_id in enumerate(ids):
                center = tuple(np.mean(corners[i][0], axis=0).astype(int))
                cv2.putText(image, f"ID {marker_id[0]}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # === Détection YOLO et liaison aux diagonales ===
        results = model(image)
        annotated_image = results[0].plot()
        tas_deja_affiches = set()

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            bbox = shapely_box(x1, y1, x2, y2)

            for diag, label in zip(diagonales, diag_labels):
                if label in tas_deja_affiches:
                    continue
                if diag.distance(bbox) < seuil_distance:
                    cv2.putText(annotated_image, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    tas_deja_affiches.add(label)
                    break  # Un tas par boîte max

        # === Affichage & enregistrement ===
        cv2.imshow(name, annotated_image)
        out.write(annotated_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# === Nettoyage ===
for cap in caps: cap.release()
for out in outs: out.release()
cv2.destroyAllWindows()
