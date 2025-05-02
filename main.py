from setup_camera import setup_cameras
from detection_yolo import process_frames
from localisation import localisations_tas
import cv2
from communication import setup_connexion, send_data

# Initialiser les caméras
cap_droite, cap_gauche, cap_haut = setup_cameras()

# Establish connection to the server
socket_conn = setup_connexion()

# Créer trois fenêtres redimensionnables pour l'affichage des détections
cv2.namedWindow("Camera droite", cv2.WINDOW_NORMAL)
cv2.namedWindow("Camera gauche", cv2.WINDOW_NORMAL)
cv2.namedWindow("Camera haut", cv2.WINDOW_NORMAL)

while True:
    # Capture d'une image depuis chaque caméra
    ret0, frame_droite = cap_droite.read()
    ret1, frame_gauche = cap_gauche.read()
    ret2, frame_haut = cap_haut.read()

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
    frames = [frame_droite, frame_gauche, frame_haut]  # List of frames to process
    windows = ["Camera droite", "Camera gauche", "Camera haut"]  # Corresponding window names
    objects_detected = process_frames(frames)  # Process frames and annotate them directly

    # Pass the nested list structure directly to localisations_tas
    tas_detected = localisations_tas(objects_detected, frames)  # Process frames without flattening

    # Display the updated frames at the end of the loop
    for i, frame in enumerate(frames):
        cv2.imshow(windows[i], frame)

    print("Validation des tas :", tas_detected)
    print("__________________________________")

    # Send tas_detected to the server
    send_data(socket_conn, tas_detected)

    # Quitter la boucle en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les caméras et fermer les fenêtres
cap_droite.release()
cap_gauche.release()
cap_haut.release()
cv2.destroyAllWindows()

# Close the socket connection
socket_conn.close()