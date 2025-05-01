#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO + ArUco (20–23) + diagonales personnalisées par caméra + enregistrement vidéo
"""

import cv2
import cv2.aruco as aruco
import numpy as np
from ultralytics import YOLO
from shapely.geometry import box as shapely_box, LineString
from datetime import datetime
import sys

# === Charger le modèle YOLO ===
model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_canette_ncnn_model', task='detect')
q
# === Initialiser les caméras ===
device1 = "/dev/camera_droite"
device2 = "/dev/camera_gauche"
device3 = "/dev/camera_haut"
cap0 = cv2.VideoCapture(device1)
cap1 = cv2.VideoCapture(device2)
cap2 = cv2.VideoCapture(device3)

cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap0.set(cv2.CAP_PROP_FPS, 10)
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap1.set(cv2.CAP_PROP_FPS, 10)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap2.set(cv2.CAP_PROP_FPS, 30)

cap0.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap2.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# === Vérification caméras ===
if not (cap0.isOpened() and cap1.isOpened() and cap2.isOpened()):
    print("Erreur : Impossible d'ouvrir une des caméras")
    sys.exit()

# === Initialisation VideoWriter ===
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
out0 = cv2.VideoWriter(f'camera0_{timestamp}.mp4', fourcc, 30.0, (640, 480))
out1 = cv2.VideoWriter(f'camera1_{timestamp}.mp4', fourcc, 10.0, (640, 480))
out2 = cv2.VideoWriter(f'camera2_{timestamp}.mp4', fourcc, 30.0, (640, 480))

# === Initialisation ArUco ===
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

# === Seuil et IDs autorisés ===
seuil_distance = 30
ids_autorises = {20, 21, 22, 23}

# === Boucle principale ===
while True:
    for cap, out, name in zip([cap0, cap1, cap2], [out0, out1, out2], ["Camera 0", "Camera 1", "Camera 2"]):
        ret, frame = cap.read()
        if not ret:
            print(f"Erreur de lecture sur {name}")
            continue

        image = frame.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray_enhanced = clahe.apply(gray)

        # === Détection ArUco ===
        corners, ids, _ = detector.detectMarkers(gray_enhanced)
        associations = {}
        diagonales = []
        filtered_corners = []
        filtered_ids = []

        if ids is not None:
            for i, marker_corners in enumerate(corners):
                marker_id = int(ids[i][0])
                if marker_id not in ids_autorises:
                    continue

                c = marker_corners[0]
                cx = int(sum(p[0] for p in c) / 4)
                cy = int(sum(p[1] for p in c) / 4)
                associations[marker_id] = {"centre": (cx, cy)}
                filtered_corners.append(marker_corners)
                filtered_ids.append([marker_id])

                h, w = image.shape[:2]
                diag_len = int(np.hypot(w, h)) + 100
                diag_45 = ((cx - diag_len, cy - diag_len), (cx + diag_len, cy + diag_len))
                diag_135 = ((cx - diag_len, cy + diag_len), (cx + diag_len, cy - diag_len))

                if name == "Camera 1":  # Gauche — seulement diagonale verte
                    diagonales.append(LineString(diag_45))
                    cv2.line(image, diag_45[0], diag_45[1], (0, 255, 0), 1)

                elif name == "Camera 0":  # Droite — seulement diagonale rose
                    diagonales.append(LineString(diag_135))
                    cv2.line(image, diag_135[0], diag_135[1], (255, 0, 255), 1)

                else:  # Caméra du haut — afficher les deux
                    diagonales.append(LineString(diag_45))
                    diagonales.append(LineString(diag_135))
                    cv2.line(image, diag_45[0], diag_45[1], (0, 255, 0), 1)
                    cv2.line(image, diag_135[0], diag_135[1], (255, 0, 255), 1)

        # === Affichage des ArUco détectés ===
        if filtered_ids:
            filtered_ids = np.array(filtered_ids, dtype=np.int32)
            image = aruco.drawDetectedMarkers(image, filtered_corners, filtered_ids)
            for marker_id, data in associations.items():
                cv2.putText(image, f"ID {marker_id}", data["centre"], cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # === Détection YOLO ===
        results = model(image)[0]
        boxes = []
        for result in results.boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            cx_obj, cy_obj = (x1 + x2) // 2, (y1 + y2) // 2

            for data in associations.values():
                cx, cy = data["centre"]
                diag_len = int(np.hypot(*image.shape[:2])) + 100

                d_45 = abs((cy - diag_len - (cy + diag_len)) * cx_obj - (cx - diag_len - (cx + diag_len)) * cy_obj +
                           (cx + diag_len) * (cy - diag_len) - (cy + diag_len) * (cx - diag_len)) / np.hypot(2 * diag_len, 2 * diag_len)

                d_135 = abs((cy + diag_len - (cy - diag_len)) * cx_obj - (cx - diag_len - (cx + diag_len)) * cy_obj +
                            (cx + diag_len) * (cy + diag_len) - (cy - diag_len) * (cx - diag_len)) / np.hypot(2 * diag_len, 2 * diag_len)

                if (name == "Camera 1" and d_45 < seuil_distance) or \
                   (name == "Camera 0" and d_135 < seuil_distance) or \
                   (name == "Camera 2" and (d_45 < seuil_distance or d_135 < seuil_distance)):
                    boxes.append((x1, y1, x2, y2))
                    break

        # === Affichage des boîtes YOLO ===
        for (x1, y1, x2, y2) in boxes:
            geom = shapely_box(x1, y1, x2, y2)
            intersects = any(geom.intersects(diag) for diag in diagonales)
            if intersects:
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(image, "tas", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # === Affichage + Enregistrement ===
        cv2.imshow(name, image)
        out.write(image)

    # === Quitter avec 'q' ===
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# === Libération des ressources ===
for cap in [cap0, cap1, cap2]:
    cap.release()
for out in [out0, out1, out2]:
    out.release()
cv2.destroyAllWindows()
