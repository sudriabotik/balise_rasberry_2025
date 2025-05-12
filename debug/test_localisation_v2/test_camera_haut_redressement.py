import cv2
import numpy as np
from setup_camera import setup_cameras
from localisation_V2 import create_aruco_detector, preprocess_for_aruco, detect_aruco
from redressement_cam_haut import position_aruco, redressement, coordonner_terrain, localisation_tas
from detection_yolo import process_frames

# === Initialisation caméra et ArUco ===
detector = create_aruco_detector()
cap_droite, cap_gauche, cap_haut = setup_cameras()
cv2.namedWindow("Camera haut", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap_haut.read()
    if not ret:
        print("❌ Erreur de capture")
        continue
    
    frame_original = frame.copy() #copie de l'image pour que les annotation ne derange as la detection des qrcode
    objects_detected = process_frames([frame])
    
    pts_image = position_aruco(frame_original, detector) 

    #objects_detected = process_frames([frame_original])
    
    if pts_image is None:
        continue

    #objects_detected = process_frames(frame)

    warped, matrix = redressement(frame, pts_image)

    print("objects_detected[0]", objects_detected[0])
    print("type(objects_detected[0])", type(objects_detected[0]))

    position_elements_jeux = coordonner_terrain(objects_detected, matrix, warped)
    print("Position des éléments de jeu :", position_elements_jeux) 
    
    tas_detected = localisation_tas(position_elements_jeux,warped)
    print(tas_detected)

    cv2.imshow("Camera haut", warped)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    print("__________________________________") 
    
cap_haut.release()
cap_droite.release()
cap_gauche.release()
cv2.destroyAllWindows()
