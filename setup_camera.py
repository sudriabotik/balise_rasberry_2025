import cv2
import sys

def setup_cameras():
    device1 = "/dev/camera_droite"
    device2 = "/dev/camera_gauche"
    device3 = "/dev/camera_haut"

    cap0 = cv2.VideoCapture(device1)
    cap1 = cv2.VideoCapture(device2)
    cap2 = cv2.VideoCapture(device3)

    cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap0.set(cv2.CAP_PROP_FPS, 10)
    cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap1.set(cv2.CAP_PROP_FPS, 10)
    cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap2.set(cv2.CAP_PROP_FPS, 30)

    # Limiter le buffer pour chaque caméra
    cap0.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap2.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Vérifier l'ouverture de chaque caméra
    if not cap0.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra 0")
        sys.exit()
    if not cap1.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra 1")
        sys.exit()
    if not cap2.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra 2")
        sys.exit()

    return cap0, cap1, cap2