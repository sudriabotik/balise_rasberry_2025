#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2

device = "/dev/camera_gauche"
cap = cv2.VideoCapture(device)

# 👉 Forcer la résolution 960x720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# 👉 Forcer la fréquence à 10 FPS
cap.set(cv2.CAP_PROP_FPS, 10)

# (Optionnel) Forcer MJPG si supporté
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

# Vérification des valeurs réellement appliquées
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"📷 Résolution réelle : {int(width)}x{int(height)} @ {fps:.2f} FPS")

if not cap.isOpened():
    print("❌ Échec ouverture caméra")
else:
    print("✅ Caméra ouverte")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Erreur de lecture")
            break

        cv2.imshow("Camera Droite", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


