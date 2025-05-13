import cv2
import numpy as np
from setup_camera import setup_cameras
from localisation_V2 import create_aruco_detector, preprocess_for_aruco, detect_aruco
from redressement_cam_haut import traitement_cam_haut, position_aruco, redressement, coordonner_terrain, localisation_tas
from detection_yolo import process_frames

# === Initialisation caméra et ArUco ===
detector = create_aruco_detector()
cap_droite, cap_gauche, cap_haut = setup_cameras()
cv2.namedWindow("Camera haut", cv2.WINDOW_NORMAL)

while True:
    ret, frame_haut = cap_haut.read()
    if not ret:
        print("❌ Erreur de capture")
        continue
    
     #copie de l'image pour que les annotation ne derange as la detection des qrcode
    objects_detected = process_frames([frame_haut])
    
    warped, tas_cam_haut = traitement_cam_haut(frame_haut, detector, objects_detected[0])

    cv2.imshow("Camera haut", warped)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    print("__________________________________") 
    
cap_haut.release()
cap_droite.release()
cap_gauche.release()
cv2.destroyAllWindows()
