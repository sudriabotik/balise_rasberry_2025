import cv2
import sys

#setup_camera haut exposure
exposure_value = 60

def setup_cameras():
    cam_droite = "/dev/camera_droite"
    cam_gauche = "/dev/camera_gauche"
    cam_haut = "/dev/camera_haut"

    cap_droite = cv2.VideoCapture(cam_droite)
    cap_gauche = cv2.VideoCapture(cam_gauche)
    #cap_haut = cv2.VideoCapture(cam_haut)
    cap_haut = cv2.VideoCapture(cam_haut, cv2.CAP_V4L2)

    cap_droite.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap_droite.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap_droite.set(cv2.CAP_PROP_FPS, 10)
    cap_gauche.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap_gauche.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap_gauche.set(cv2.CAP_PROP_FPS, 10)
    cap_haut.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
    cap_haut.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
    cap_haut.set(cv2.CAP_PROP_FPS, 10)

    # Limiter le buffer pour chaque caméra
    cap_droite.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap_gauche.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap_haut.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Vérifier l'ouverture de chaque caméra
    if not cap_droite.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra droite")
        sys.exit()
    if not cap_gauche.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra gauche")
        sys.exit()
    if not cap_haut.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra haut")
        sys.exit()

    setup_camera_haut_exposure(cap_haut)

    return cap_droite, cap_gauche, cap_haut

def setup_camera_haut_exposure (cap):
    if not cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1):
        print("⚠️ Impossible d'activer le mode manuel d'exposition")
    else:
        print("AUTO_EXPOSURE =", cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))

    # 3) Appliquer la valeur CLI que vous avez testée (200)
    #exposure_value = 60
    if not cap.set(cv2.CAP_PROP_EXPOSURE, float(exposure_value)):
        print("⚠️ Impossible de régler l'exposition")
    else:
        print("EXPOSURE      =", cap.get(cv2.CAP_PROP_EXPOSURE))
    return None


