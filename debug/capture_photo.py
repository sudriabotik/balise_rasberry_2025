import cv2
import sys
import time

# 1) Ouvrir la caméra avec le backend V4L2 pour forcer les contrôles v4l2
device = "/dev/camera_haut"
cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
if not cap.isOpened():
    print(f"Erreur : Impossible d'ouvrir la caméra {device}")
    sys.exit()

# 2) Passer en mode manuel (valeur 1 sous Linux/V4L2)
if not cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1):
    print("⚠️ Impossible d'activer le mode manuel d'exposition")
else:
    print("AUTO_EXPOSURE =", cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))

# 3) Appliquer la valeur CLI que vous avez testée (200)
exposure_value = 60 # 100 x 0,0001s = 0.01s = 10 ms
if not cap.set(cv2.CAP_PROP_EXPOSURE, float(exposure_value)):
    print("⚠️ Impossible de régler l'exposition")
else:
    print("EXPOSURE      =", cap.get(cv2.CAP_PROP_EXPOSURE))

# 4) Laisser un petit temps de stabilisation  
time.sleep(0.5)
# (optionnel : lire quelques images pour vider le buffer)
for _ in range(5):
    cap.read()

# 5) Capturer une seule image
ret, frame = cap.read()
if not ret:
    print("Erreur lors de la capture de l'image")
else:
    output_file = "capture.jpg"
    cv2.imwrite(output_file, frame)
    print(f"Image capturée et enregistrée sous {output_file}")

cap.release()
