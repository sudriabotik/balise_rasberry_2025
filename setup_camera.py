import cv2
import sys

def setup_cameras():
    cam_droite = "/dev/camera_droite"
    cam_gauche = "/dev/camera_gauche"
    cam_haut = "/dev/camera_haut"

    cap_droite = cv2.VideoCapture(cam_droite)
    cap_gauche = cv2.VideoCapture(cam_gauche)
    cap_haut = cv2.VideoCapture(cam_haut)

    cap_droite.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap_droite.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap_droite.set(cv2.CAP_PROP_FPS, 10)
    cap_gauche.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap_gauche.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap_gauche.set(cv2.CAP_PROP_FPS, 10)
    cap_haut.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap_haut.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap_haut.set(cv2.CAP_PROP_FPS, 30)

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

    return cap_droite, cap_gauche, cap_haut