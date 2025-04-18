import cv2
import cv2.aruco as aruco
import numpy as np
from ultralytics import YOLO
from shapely.geometry import box as shapely_box, LineString
from shapely.ops import unary_union

# === Charger YOLO ===
modele_yolo = YOLO("C:/Users/Mickael/PJML/runs/detect/train/weights/best.pt")

# === Charger l'image ===
image = cv2.imread("tgt.jpg")
if image is None:
    raise FileNotFoundError("L'image n'a pas été trouvée.")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
gray_enhanced = clahe.apply(gray)

# === Détection ArUco ===
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

corners, ids, _ = detector.detectMarkers(gray_enhanced)

associations = {}
image_out = image.copy()
filtered_corners = []
filtered_ids = []

diagonales = []  # Pour stocker les diagonales

if ids is not None:
    for i, marker_corners in enumerate(corners):
        marker_id = int(ids[i][0])
        if marker_id == 47:
            continue  # Ignorer le marqueur avec l'ID 47

        c = marker_corners[0]
        cx = int(sum(p[0] for p in c) / 4)
        cy = int(sum(p[1] for p in c) / 4)

        associations[marker_id] = {"centre": (cx, cy)}
        filtered_corners.append(marker_corners)
        filtered_ids.append([marker_id])

        h, w = image.shape[:2]
        diag_len = int(np.hypot(w, h)) + 100

        # Diagonales
        diag_45 = ((cx - diag_len, cy - diag_len), (cx + diag_len, cy + diag_len))
        diag_135 = ((cx - diag_len, cy + diag_len), (cx + diag_len, cy - diag_len))
        diagonales.append(LineString(diag_45))
        diagonales.append(LineString(diag_135))

        # Tracer les diagonales
        cv2.line(image_out, diag_45[0], diag_45[1], (0, 255, 0), 1, cv2.LINE_AA)
        cv2.line(image_out, diag_135[0], diag_135[1], (255, 0, 255), 1, cv2.LINE_AA)

# === Dessiner les ArUco détectés ===
if filtered_ids:
    filtered_ids = np.array(filtered_ids, dtype=np.int32)
    image_out = aruco.drawDetectedMarkers(image_out, filtered_corners, filtered_ids)
    for marker_id, data in associations.items():
        cv2.putText(image_out, f"ID {marker_id}", data["centre"], cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# === Détection avec YOLO ===
seuil_distance = 30
results = modele_yolo(image)[0]

boxes = []
for result in results.boxes:
    x1, y1, x2, y2 = map(int, result.xyxy[0])
    cx_obj, cy_obj = (x1 + x2) // 2, (y1 + y2) // 2

    for data in associations.values():
        cx, cy = data["centre"]
        diag_len = int(np.hypot(*image.shape[:2])) + 100

        x1_45, y1_45 = cx - diag_len, cy - diag_len
        x2_45, y2_45 = cx + diag_len, cy + diag_len
        x1_135, y1_135 = cx - diag_len, cy + diag_len
        x2_135, y2_135 = cx + diag_len, cy - diag_len
        # Diagonales loin de tout, par exemple dans un coin vide


        d_45 = abs((y2_45 - y1_45) * cx_obj - (x2_45 - x1_45) * cy_obj + x2_45 * y1_45 - y2_45 * x1_45) / np.hypot(x2_45 - x1_45, y2_45 - y1_45)
        d_135 = abs((y2_135 - y1_135) * cx_obj - (x2_135 - x1_135) * cy_obj + x2_135 * y1_135 - y2_135 * x1_135) / np.hypot(x2_135 - x1_135, y2_135 - y1_135)

        if d_45 < seuil_distance or d_135 < seuil_distance:
            boxes.append((x1, y1, x2, y2))
            break

# === Fusion et intersection avec diagonales ===
if boxes:
    shapes = [shapely_box(x1, y1, x2, y2) for (x1, y1, x2, y2) in boxes]
    merged = unary_union(shapes)

    geometries = [merged] if merged.geom_type == "Polygon" else list(merged.geoms)

    for geom in geometries:
        intersects = any(geom.intersects(diag) for diag in diagonales)
        color = (0, 0, 255) if intersects else (255, 0, 0)  # Rouge si touche une diagonale, sinon bleu
        x_min, y_min, x_max, y_max = map(int, geom.bounds)
        cv2.rectangle(image_out, (x_min, y_min), (x_max, y_max), color, 3)
        cv2.putText(image_out, "tas", (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

# === Affichage ===
cv2.imshow("YOLO + ArUco + Tas coloré", image_out)
cv2.waitKey(0)
cv2.destroyAllWindows()
