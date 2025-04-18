#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import os

device = "/dev/camera_haut"
print("os path",os.path.exists(device)) 


cap = cv2.VideoCapture(device)

if not cap.isOpened():
    print(f"❌ Impossible d’ouvrir la caméra : {device}")
else:
    print(f"✅ Caméra ouverte : {device}")
    ret, frame = cap.read()
    if ret:
        print("✅ Frame capturée avec succès")
    else:
        print("⚠️ Ouverture OK mais impossible de lire une frame")

    cap.release()
