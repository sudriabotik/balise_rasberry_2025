#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import cv2

symlink = "/dev/camera_gauche"

# On suit le lien pour obtenir le vrai /dev/videoX
if os.path.islink(symlink):
    real_device = os.path.realpath(symlink)
else:
    real_device = symlink

print(f"🧭 Chemin réel de la caméra : {real_device}")

cap = cv2.VideoCapture(real_device)

if not cap.isOpened():
    print(f"❌ Impossible d’ouvrir la caméra : {real_device}")
else:
    print(f"✅ Caméra ouverte : {real_device}")
    ret, frame = cap.read()
    if ret:
        print("✅ Frame capturée avec succès")
    else:
        print("⚠️ Ouverture OK mais impossible de lire une frame")

    cap.release()
