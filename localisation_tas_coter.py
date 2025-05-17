import cv2
import cv2.aruco as aruco
import numpy as np
from shapely.geometry import LineString, Point, box as shapely_box

# === Dictionnaire des IDs ArUco autorisés ===
aruco_to_tas = {
    20: "tas_8",
    21: "tas_5",
    22: "tas_4",
    23: "tas_1"
}

# === Caméras et leurs tas autorisés ===
tas_par_camera = {
    "Camera droite": {"tas_4", "tas_8"},
    "Camera gauche": {"tas_1", "tas_5"}
}

# === Offset d'angle personnalisé par tas (en degrés) ===
# sens positif sens horaire
angle_offsets_par_tas = {
    "tas_5": 100,
    "tas_8": -100,
    "tas_4": -110,
    "tas_1": 110
}

# === Paramètres de détection personnalisés par tas ===

rectangle_params_par_tas = {
    "tas_5": {"zone_distance": 285, "rect_w": 240, "rect_h": 110},
    "tas_8": {"zone_distance": 255, "rect_w": 220, "rect_h": 115},
    "tas_4": {"zone_distance": 200, "rect_w": 140, "rect_h": 90},
    "tas_1": {"zone_distance": 223, "rect_w": 160, "rect_h": 82}
}

init_distance_rectangle = True
'''
#valeur equipe jaune
rectangle_params_par_tas = {
    "tas_8": {"zone_distance": 285, "rect_w": 240, "rect_h": 115},
    "tas_5": {"zone_distance": 255, "rect_w": 220, "rect_h": 115},
    "tas_1": {"zone_distance": 200, "rect_w": 140, "rect_h": 90},
    "tas_4": {"zone_distance": 223, "rect_w": 160, "rect_h": 82}
}
'''

# === Sauvegarde des rectangles persistants ===
rectangles_persistants = {}

# === Création du détecteur ArUco ===
def create_aruco_detector():
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()
    parameters.adaptiveThreshWinSizeMin = 3
    parameters.adaptiveThreshWinSizeMax = 23
    parameters.adaptiveThreshWinSizeStep = 10
    parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    return detector

# === Prétraitement image ===
def preprocess_for_aruco(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# === Détection brute ArUco ===
def detect_aruco(gray_image, detector):
    corners, ids, _ = detector.detectMarkers(gray_image)
    return corners, ids

# === Extraction centres et labels valides ===
def get_valid_qr_centers(corners, ids, aruco_to_tas):
    centers = []
    labels = []
    qr_vectors = []
    for i, marker_corners in enumerate(corners):
        marker_id = int(ids[i][0])
        if marker_id in aruco_to_tas:
            pts = marker_corners[0]
            cx = int(np.mean(pts[:, 0]))
            cy = int(np.mean(pts[:, 1]))
            v = np.array(pts[1]) - np.array(pts[0])  # horizontal vector
            centers.append((cx, cy))
            labels.append(aruco_to_tas[marker_id])
            qr_vectors.append(v)
    return centers, labels, qr_vectors

# === Calcul des demi-diagonales avec offset adapté par tas ===
def compute_outward_diagonal(cx, cy, direction_vector, angle_offset_deg=0, length=1000):
    dx, dy = direction_vector
    base_angle = np.arctan2(dy, dx) - np.pi / 2  # -90°
    angle_rad = base_angle + np.deg2rad(angle_offset_deg)
    dx_scaled = int(np.cos(angle_rad) * length)
    dy_scaled = int(np.sin(angle_rad) * length)
    return (cx, cy), (cx + dx_scaled, cy + dy_scaled)

def compute_qr_diagonals(centers, labels, vectors):
    diagonales = []
    diag_labels = []
    for (cx, cy), label, v in zip(centers, labels, vectors):
        offset = angle_offsets_par_tas.get(label, 0)
        p1, p2 = compute_outward_diagonal(cx, cy, v, angle_offset_deg=offset)
        diagonales.append(LineString([p1, p2]))
        diag_labels.append(label)
    return diagonales, diag_labels

# === Validation d'un rectangle de tas selon les objets ===

def valider_contenu_tas(rect, centres):
    """
    Vérifie combien d'objets de chaque classe ont leur centre dans un rectangle.

    Args:
        rect: shapely Polygon ou Rectangle
        centres: liste de tuples (x, y, classe)

    Returns:
        count_class_0, count_class_1
    """
    count_class_0 = 0
    count_class_1 = 0
    #print("parametre centre ", centres)
    for i, (x, y, classe) in enumerate(centres):
        try:
            point = Point(x, y)
            if rect.contains(point):
                if classe == 0.0:
                    count_class_0 += 1
                elif classe == 1.0:
                    count_class_1 += 1
        except Exception as e:
            print(f"[ERREUR] Objet #{i} invalide : {e}")

    return count_class_0, count_class_1

# === Création d'un rectangle de tas à partir de sa diagonale ===
def create_rectangle(label, diag):
    params = rectangle_params_par_tas[label]
    zone_distance = params["zone_distance"]
    rect_w = params["rect_w"]
    rect_h = params["rect_h"]

    p1, p2 = diag.coords[0], diag.coords[1]
    vecteur = np.array(p2) - np.array(p1)
    longueur = np.linalg.norm(vecteur)
    if longueur == 0:
        return None
    direction = vecteur / longueur
    cible = np.array(p1) + direction * zone_distance
    cx, cy = int(cible[0]), int(cible[1])

    return shapely_box(cx - rect_w//2, cy - rect_h//2, cx + rect_w//2, cy + rect_h//2)

# === Association objets ↔ diagonales avec zone restreinte ===
def associer_objets_diagonales(boxes, diagonales, diag_labels, nom_camera, image,
                                tas_deja_affiches=None):
    if tas_deja_affiches is None:
        tas_deja_affiches = set()

    validation_par_tas = {}
    diag_dict = {label: diag for diag, label in zip(diagonales, diag_labels)}
    labels_uniques = list(aruco_to_tas.values())
    tas_autorises = tas_par_camera.get(nom_camera, set())
    #print(f"[INFO] Tas autorisés pour {nom_camera}: {tas_autorises}")
    #print(f"[INFO] Tas déjà affichés: {tas_deja_affiches}")

    for label in labels_uniques:
        if label in tas_deja_affiches or label not in tas_autorises:
            #print(f"[INFO] Tas {label} déjà affiché ou non autorisé pour {nom_camera}")
            continue

        diag = diag_dict.get(label)

        if diag is not None:
            rect = create_rectangle(label, diag)
            rectangles_persistants[label] = rect
            #print(f"[INFO] Rectangle mis à jour pour {label}")
        else:
            rect = rectangles_persistants.get(label)
            if rect is None:
                print(f"[INFO] Aucun rectangle disponible pour {label}, QR non visible")
                continue
            else:
                print(f"[INFO] Rectangle réutilisé pour {label}, QR non visible")

        minx, miny, maxx, maxy = map(int, rect.bounds)
        count_class_0, count_class_1 = valider_contenu_tas(rect, boxes)

        color = (0, 0, 255) if count_class_0 >= 3 and count_class_1 >= 1 else (255, 0, 0)
        cv2.rectangle(image, (minx, miny), (maxx, maxy), color, 2)
        cv2.putText(image, label, (minx, miny - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        if count_class_0 >= 3 and count_class_1 >= 1:
            cx = (minx + maxx) // 2
            cy = (miny + maxy) // 2
            cv2.putText(image, label, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            tas_deja_affiches.add(label)
            validation_par_tas[label] = True
        else:
            validation_par_tas[label] = False

    return image, validation_par_tas

def distance_rectangle(couleur_equipe):
    global init_distance_rectangle, rectangle_params_par_tas

    if couleur_equipe == "jaune" and init_distance_rectangle:
        print("Changement de couleur équipe, on inverse les distances des rectangles")
        init_distance_rectangle = False

        d = rectangle_params_par_tas          # alias plus court

        # tas_1  ↔  tas_4
        d["tas_1"]["zone_distance"], d["tas_4"]["zone_distance"] = \
            d["tas_4"]["zone_distance"], d["tas_1"]["zone_distance"]

        # tas_5  ↔  tas_8
        d["tas_5"]["zone_distance"], d["tas_8"]["zone_distance"] = \
            d["tas_8"]["zone_distance"], d["tas_5"]["zone_distance"]

        print("rectangle_params_par_tas", rectangle_params_par_tas)


# === Pipeline ArUco complet pour caméra gauche/droite ===
def process_frame_qr_only(frame, nom_camera, detector, boxes=None, couleur_equipe=None):
    if nom_camera not in ["Camera droite", "Camera gauche"]:
        return frame, {}

    distance_rectangle(couleur_equipe)

    coords_centre = visualisation_objects_detected(frame, boxes)

    gray = preprocess_for_aruco(frame)
    corners, ids = detect_aruco(gray, detector)
    validation_par_tas = {}

    if ids is not None:
        centers, labels, vectors = get_valid_qr_centers(corners, ids, aruco_to_tas)
        diagonales, diag_labels = compute_qr_diagonals(centers, labels, vectors)

        for diag in diagonales:
            p1, p2 = diag.coords
            cv2.line(frame, tuple(map(int, p1)), tuple(map(int, p2)), (0, 255, 255), 2)

        if boxes is not None:
            frame, validation_par_tas = associer_objets_diagonales(coords_centre, diagonales, diag_labels, nom_camera, frame)

    else:
        print(f"[INFO] Aucun ArUco détecté sur {nom_camera}")
        if boxes is not None:
            # Appel avec listes vides : aucune diagonale visible
            frame, validation_par_tas = associer_objets_diagonales(coords_centre, [], [], nom_camera, frame)

    return frame, validation_par_tas
def visualisation_objects_detected(image, box_list):
    """
    Dessine les centres des objets détectés et retourne leurs coordonnées avec la classe.

    Args:
        image: image sur laquelle dessiner
        box_list: liste de dictionnaires {'coordinates': [...], 'class': ...}

    Returns:
        Liste de tuples (x_center, y_center, classe)
    """
    centres = []

    if not box_list:
        print("Erreur, Aucun objet détecté")
        return centres

    for i, obj in enumerate(box_list):
        if not isinstance(obj, dict):
            print(f"[AVERTISSEMENT] Objet #{i} ignoré car non dictionnaire : {obj}")
            continue

        coords = obj.get("coordinates")
        classe = obj.get("class")

        if not coords or len(coords) != 4:
            print(f"[ERREUR] Coordonnées invalides pour l'objet #{i}: {coords}")
            continue

        x1, y1, x2, y2 = coords
        x_center = (x1 + x2) / 2
        y_center = (y1 + y2) / 2

        centres.append((x_center, y_center, classe))
        
        # Rose (255, 0, 255) si classe == 1, sinon jaune (0, 255, 255)
        color = (255, 0, 255) if classe == 1 else (0, 255, 255)
        cv2.circle(image, (int(x_center), int(y_center)), 10, color, -1)

    return centres

def numero_tas_en_jaune(tas: dict) -> None:
    """
    paires à échanger :
      tas_5 ↔ tas_8
      tas_1 ↔ tas_4
      tas_2 ↔ tas_3
      tas_6 ↔ tas_7
    """

    swaps = [
        ("tas_5", "tas_8"),
        ("tas_1", "tas_4"),
        ("tas_2", "tas_3"),
        ("tas_6", "tas_7"),
    ]

    for k1, k2 in swaps:
        if k1 in tas and k2 in tas:        # les deux clés existent
            tas[k1], tas[k2] = tas[k2], tas[k1]
        else:
            # facultatif : message de debug ; commente si tu ne veux rien afficher
            manquantes = [k for k in (k1, k2) if k not in tas]
            print(f"  ⚠️  clé(s) manquante(s) ignorée(s) : {', '.join(manquantes)}")

    # la fonction modifie le dict en place, rien à retourner


def safe_merge(*items, verbose=False):
    """
    Fusionne les dictionnaires passés en argument.
    Ignore silencieusement tout élément qui n’est pas un dict.

    >>> a = {'x': 1}
    >>> b = None
    >>> c = {'y': 2}
    >>> safe_merge(a, b, c)
    {'x': 1, 'y': 2}
    """
    result = {}
    for idx, item in enumerate(items, 1):
        if isinstance(item, dict):
            result |= item                 # opérateur de fusion (Py 3.9+)
        elif verbose:
            print(f"[safe_merge] argument #{idx} ignoré (type {type(item).__name__})")
    return result
