import cv2
import cv2.aruco as aruco
import numpy as np
import sys

exposure_value = 60

def setup_camera_haut_exposure(cap):
    if not cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1):
        print("\u26a0\ufe0f Impossible d'activer le mode manuel d'exposition")
    else:
        print("AUTO_EXPOSURE =", cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))

    if not cap.set(cv2.CAP_PROP_EXPOSURE, float(exposure_value)):
        print("\u26a0\ufe0f Impossible de r\u00e9gler l'exposition")
    else:
        print("EXPOSURE      =", cap.get(cv2.CAP_PROP_EXPOSURE))


def setup_cameras():
    cam_droite = "/dev/camera_droite"
    cam_gauche = "/dev/camera_gauche"
    cam_haut = "/dev/camera_haut"

    cap_droite = cv2.VideoCapture(cam_droite)
    cap_gauche = cv2.VideoCapture(cam_gauche)
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

    cap_droite.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap_gauche.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap_haut.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap_droite.isOpened():
        print("Erreur : Impossible d'ouvrir la cam\u00e9ra droite")
        sys.exit()
    if not cap_gauche.isOpened():
        print("Erreur : Impossible d'ouvrir la cam\u00e9ra gauche")
        sys.exit()
    if not cap_haut.isOpened():
        print("Erreur : Impossible d'ouvrir la cam\u00e9ra haut")
        sys.exit()

    setup_camera_haut_exposure(cap_haut)

    return cap_droite, cap_gauche, cap_haut

# === Initialisation ===
caps = setup_cameras()
names = ["Camera droite", "Camera gauche", "Camera haut"]

# === D\u00e9tecteur ArUco ===
dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(dictionary, parameters)

for name in names:
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)

while True:
    for cap, name in zip(caps, names):
        ret, frame = cap.read()
        if not ret:
            print(f"Erreur de lecture sur {name}")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None:
            frame = aruco.drawDetectedMarkers(frame, corners, ids)
            for i, marker_id in enumerate(ids):
                center = tuple(np.mean(corners[i][0], axis=0).astype(int))
                cv2.putText(frame, f"ID {marker_id[0]}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow(name, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

for cap in caps:
    cap.release()
cv2.destroyAllWindows()
