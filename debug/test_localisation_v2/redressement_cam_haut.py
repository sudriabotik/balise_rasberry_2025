import cv2
import numpy as np
from localisation_V2 import create_aruco_detector, preprocess_for_aruco, detect_aruco
import sys

coordonnée_qrcode = np.array([
    [600, 600],   # ID 23 → HG # c'est pas les vrai coordonnée mais c'est comme ça que ça marche sinon le y est inversé
    [2400, 600],  # ID 22 → HD
    [2400, 1400],   # ID 20 → BD
    [600, 1400]     # ID 21 → BG
], dtype=np.float32)



# Dictionnaire global de sauvegarde des derniers centres de qrcode connus
dernier_centres_aruco = {
    23: None,  # HG
    22: None,  # HD
    20: None,  # BD
    21: None   # BG
}

def calculer_centre_aruco(corners, ids):
    global dernier_centres_aruco
    id_to_center = {}

    # Mise à jour des centres détectés dans cette frame
    for i, marker_id in enumerate(ids.flatten()):
        pts = corners[i][0]
        cx = int(np.mean(pts[:, 0]))
        cy = int(np.mean(pts[:, 1]))
        id_to_center[marker_id] = (cx, cy)
        dernier_centres_aruco[marker_id] = (cx, cy)  # On sauvegarde la dernière position connue

    # Ordre voulu : HG, HD, BD, BG → 23, 22, 20, 21
    ids_utiles = [23, 22, 20, 21]
    centers = []

    for id_tag in ids_utiles:
        if dernier_centres_aruco[id_tag] is None:
            print(f"❌ ArUco {id_tag} jamais détecté, impossible de redresser")
            return None
        centers.append(dernier_centres_aruco[id_tag])

    return np.array(centers, dtype=np.float32)

def position_aruco(frame, detector):
    gray = preprocess_for_aruco(frame)
    corners, ids = detect_aruco(gray, detector)

    pts_image = calculer_centre_aruco(corners, ids)
    if pts_image is None:
        print("❌ Erreur de calcul des centres ArUco")
        return None
    return pts_image


def redressement(frame, pts_image):
    matrix = cv2.getPerspectiveTransform(pts_image, coordonnée_qrcode) 
    warped = cv2.warpPerspective(frame, matrix, (3000, 2000))  # Dimensions arbitraires

    #=== Format Python copiable ===
    #pythonMat = "[" + ",\n".join("[" + ",".join(f"{v:.6f}" for v in row) + "]" for row in matrix) + "]"

    # Affichage des centres sur l'image originale
    for pt in pts_image:
        frame = cv2.circle(frame, (int(pt[0]), int(pt[1])), 20, (0, 255, 0), -1)
    # Affichage des centres sur l'image redressée
    for pt in coordonnée_qrcode:
        warped = cv2.circle(warped, (int(pt[0]), int(pt[1])), 20, (255, 0, 0), -1)

    return warped, matrix
def coordonner_terrain(detections, mat, image):
    """
    Transforme les coordonnées image des objets détectés vers les coordonnées du terrain (x, y).
    
    Args:
        detections: liste de détections [{coordinates: [...], class: ...}, ...]
        mat: matrice de perspective OpenCV 3x3
        image: image redressée pour afficher les points détectés

    Returns:
        liste de tuples (x, y) des positions projetées sur le terrain
    """
    positions = []

    if not detections or not isinstance(detections, list):
        print("[ERREUR] Format inattendu pour detections")
        print(f"Type de detections : {type(detections)}")
        print(f"Valeur de detections : {detections}")
        return positions

    for i, obj in enumerate(detections):
        try:
            if not isinstance(obj, dict):
                raise TypeError("L'objet n'est pas un dictionnaire")

            if obj.get("class") != 1.0:
                continue  # Ignore les objets qui ne sont pas de classe 1

            coords = obj["coordinates"]
            x1, y1, x2, y2 = coords

            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2

            pt = np.array([[[x_center, y_center]]], dtype=np.float32)
            transformed = cv2.perspectiveTransform(pt, np.array(mat, dtype=np.float32))

            x_terrain = float(transformed[0][0][0])
            y_terrain = float(transformed[0][0][1])
            positions.append((x_terrain, y_terrain))

            # Dessiner sur l'image redressée
            cv2.circle(image, (int(x_terrain), int(y_terrain)), 10, (0, 255, 255), -1)

        except Exception as e:
            print(f"[ERREUR] Impossible de transformer le point #{i} : {e}")

    return positions


zones_tas = {
    "tas_2": {"x_min": 600, "x_max": 900, "y_min": 20, "y_max": 200},
    "tas_3": {"x_min": 2000, "x_max": 2400, "y_min": 20, "y_max": 200},
    "tas_6": {"x_min": 900, "x_max": 1300, "y_min": 700, "y_max": 1100},
    "tas_7": {"x_min": 1700, "x_max": 2100, "y_min": 700, "y_max": 1100}
}

def localisation_tas(position_elements_jeux, image):
    """
    Vérifie si un objet détecté est dans un tas, et dessine les rectangles sur l'image.

    Args:
        position_elements_jeux: liste de tuples (x, y)
        image: image redressée sur laquelle dessiner

    Returns:
        tas_detected: dictionnaire booléen pour chaque tas
    """
    tas_detected = {key: False for key in zones_tas}

    # Dessiner tous les rectangles de zone
    for key, zone in zones_tas.items():
        cv2.rectangle(
            image,
            (zone["x_min"], zone["y_min"]),
            (zone["x_max"], zone["y_max"]),
            (0, 255, 0), 2  # Vert
        )
        cv2.putText(image, key, (zone["x_min"], zone["y_min"] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Vérifier si chaque objet est dans une zone
    for x, y in position_elements_jeux:
        for key, zone in zones_tas.items():
            if zone["x_min"] <= x <= zone["x_max"] and zone["y_min"] <= y <= zone["y_max"]:
                tas_detected[key] = True
                break

    return tas_detected


def traitement_cam_haut(frame_haut, detector, objects_detected):
    
    pts_image = position_aruco(frame_haut.copy(), detector) #copie de l'image pour que les annotation ne derange as la detection des qrcode
    
    if pts_image is None:
        print("❌ Erreur de positionnement des ArUco")
        return None

    warped, matrix = redressement(frame_haut, pts_image)

    print("objects_detected[0]", objects_detected)

    position_elements_jeux = coordonner_terrain(objects_detected, matrix, warped)
    print("Position des éléments de jeu :", position_elements_jeux) 
    
    tas_detected = localisation_tas(position_elements_jeux, warped)

    return  warped, tas_detected 