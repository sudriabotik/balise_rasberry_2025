#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import sys
import time

device = "/dev/camera_droite"
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print(f"Erreur : Impossible d'ouvrir la caméra {device}")
    sys.exit()

# 🔍 Lire le format FOURCC
fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
fourcc_str = "".join([chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)])
print(f"🎥 Format vidéo utilisé par {device} : {fourcc_str}")

# Créer une fenêtre redimensionnable
cv2.namedWindow("Test Camera", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la capture de l'image")
        break

    cv2.imshow("Test Camera", frame)

    key = cv2.waitKey(1) & 0xFF

    # Quitter avec 'q'
    if key == ord('q'):
        break

    # Sauvegarder avec 's'
    elif key == ord('s'):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Image sauvegardée : {filename}")

cap.release()
cv2.destroyAllWindows()