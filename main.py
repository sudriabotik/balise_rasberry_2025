from setup_camera import setup_cameras
from detection_yolo import process_frames
from localisation import localisations_tas
import cv2

# Initialiser les caméras
cap0, cap1, cap2 = setup_cameras()

# Créer trois fenêtres redimensionnables pour l'affichage des détections
cv2.namedWindow("Detection Camera 0", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 2", cv2.WINDOW_NORMAL)

while True:
    # Capture d'une image depuis chaque caméra
    ret0, frame0 = cap0.read()
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret0:
        print("Erreur lors de la capture de la caméra 0")
        break
    if not ret1:
        print("Erreur lors de la capture de la caméra 1")
        break
    if not ret2:
        print("Erreur lors de la capture de la caméra 2")
        break

    # Utiliser la fonction process_frames pour traiter les frames
    frames = [frame0, frame1, frame2]  # List of frames to process
    windows = ["Detection Camera 0", "Detection Camera 1", "Detection Camera 2"]  # Corresponding window names
    objects_detected = process_frames(frames)  # Process frames and annotate them directly

    # Flatten the objects_detected list before passing it to localisations_tas
    flattened_objects_detected = [obj for frame_detections in objects_detected for obj in frame_detections]
    tas_detected = localisations_tas(flattened_objects_detected, frames)  # Add rectangles to frames

    # Display the updated frames at the end of the loop
    for i, frame in enumerate(frames):
        cv2.imshow(windows[i], frame)

    print("Pile 1 :", tas_detected[0],"Pile 2 validée:", tas_detected[1])
    print("__________________________________")

    # Quitter la boucle en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les caméras et fermer les fenêtres
cap0.release()
cap1.release()
cap2.release()
cv2.destroyAllWindows()