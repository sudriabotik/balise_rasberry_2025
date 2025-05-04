import cv2
import cv2.aruco as aruco
import numpy as np
from ultralytics import YOLO
from shapely.geometry import box as shapely_box
from datetime import datetime
import sys

# === Modèle YOLO ===
model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_canette_ncnn_model', task='detect')

# === Configuration des caméras ===
devices = ["/dev/camera_droite","/dev/camera_haut","/dev/camera_gauche"]
names = ["Camera droite", "Camera milieu","Camera gauche"]
fps_list = [30, 10, 30]

caps = [cv2.VideoCapture(dev) for dev in devices]
for cap, fps in zip(caps, fps_list):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not all(cap.isOpened() for cap in caps):
    print("Erreur : Une caméra n'a pas pu être ouverte.")
    sys.exit()

# === Enregistrement vidéo ===
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
outs = [cv2.VideoWriter(f'camera{i}_{timestamp}.mp4', fourcc, fps, (640, 480)) for i, fps in enumerate(fps_list)]

# === Fenêtres OpenCV ===
for name in names:
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)

# === ArUco setup ===
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
parameters.adaptiveThreshWinSizeMin = 3
parameters.adaptiveThreshWinSizeMax = 23
parameters.adaptiveThreshWinSizeStep = 10
parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
detector = aruco.ArucoDetector(aruco_dict, parameters)

ids_autorises = {20, 21, 22, 23}
seuil_distance = 30

# === Suivi des positions des tas ===
last_positions = {}
seuil_deplacement = 30  # pixels

# === Boucle principale ===
while True:
    for cam_index, (cap, out, name) in enumerate(zip(caps, outs, names)):
        ret, frame = cap.read()
        if not ret:
            print(f"Erreur de lecture sur {name}")
            continue

        image = frame.copy()

        # Prétraitement uniquement pour ArUco si caméra du milieu
        if name == "Camera milieu":
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None:
            valid_corners = []
            valid_ids = []
            for i, marker_id in enumerate(ids):
                id_val = int(marker_id[0])
                if id_val in ids_autorises:
                    valid_corners.append(corners[i])
                    valid_ids.append([id_val])

            if valid_ids:
                image = aruco.drawDetectedMarkers(image, valid_corners, np.array(valid_ids))
                for i, marker_id in enumerate(valid_ids):
                    center = tuple(np.mean(valid_corners[i][0], axis=0).astype(int))
                    cv2.putText(image, f"ID {marker_id[0]}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # === Détection YOLO ===
        results = model(image)
        annotated_image = results[0].plot()

        current_positions = {}

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = results[0].names[int(box.cls[0])]
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            current_positions[label] = (center_x, center_y)

            # Affichage nom
            cv2.putText(annotated_image, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            # Détection de déplacement
            if label in last_positions:
                last_x, last_y = last_positions[label]
                dist = np.linalg.norm([center_x - last_x, center_y - last_y])
                if dist > seuil_deplacement:
                    cv2.putText(annotated_image, "DÉPLACÉ", (x1, y2 + 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Mise à jour des positions
        last_positions = current_positions.copy()

        cv2.imshow(name, annotated_image)
        out.write(annotated_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

for cap in caps:
    cap.release()
for out in outs:
    out.release()
cv2.destroyAllWindows()
