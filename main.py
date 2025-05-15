from setup_camera import setup_cameras
from detection_yolo import process_frames
from localisation import localisations_tas
import cv2
from communication_client import setup_connexion, connexion_process, send_data, couleur_equipe, wait_start_match, exchange_infos
from ecrans_lcd import setup_lcd

import time

lcd = setup_lcd()
# Initialiser les caméras
#cap_droite, cap_gauche, cap_haut = setup_cameras()

# Establish connection to the server

#connexion_handle = setup_connexion(lcd)
#verify_connexion(connexion_handle)

connexion_handle = connexion_process()

"""
# Créer trois fenêtres redimensionnables pour l'affichage des détections
cv2.namedWindow("Camera droite", cv2.WINDOW_NORMAL)
cv2.namedWindow("Camera gauche", cv2.WINDOW_NORMAL)
cv2.namedWindow("Camera haut", cv2.WINDOW_NORMAL)
"""

# Boucle pour attendre la réception de la couleur de l'équipe
couleur_equipe_value = None
#couleur_equipe_value = couleur_equipe(connexion_handle, lcd)
print(f"Couleur de l'équipe reçue : {couleur_equipe_value}")
elapsed_time = 0
start_time = None

# Boucle principale pour traiter les images
while True:
    
    # verify connexion is still ok, else attempt to reconnect
    print(connexion_handle)
    if connexion_handle == None :
        print("connexion handle is None")
        connexion_handle = connexion_process()
    else :
        if not connexion_handle.valid :
            print("invalid connexion handle")
            try :
                connexion_handle.Close() # we do not really care of this cause an error, it's just to try to close it just in case
            finally :
                connexion_handle = connexion_process()
    
    
    if couleur_equipe_value == None : # it means the match has not yet started
        couleur_equipe_value = exchange_infos(connexion_handle)
        if couleur_equipe_value != None : # this mean the robot sent that the match have started
            start_time = time.time()
            print(f"match started, with color {couleur_equipe_value}")
        else :
            print("failed to obtain informations from the robot")
            time.sleep(1)
            continue
    
    print("lala")
    
    time.sleep(1)
    continue
    
    
    # Capture d'une image depuis chaque caméra
    ret0, frame_droite = cap_droite.read()
    ret1, frame_gauche = cap_gauche.read()
    ret2, frame_haut = cap_haut.read()

    # Utiliser la fonction process_frames pour traiter les frames
    frames = [frame_droite, frame_gauche, frame_haut]  # List of frames to process
    windows = ["Camera droite", "Camera gauche", "Camera haut"]  # Corresponding window names
    objects_detected = process_frames(frames)  # Process frames and annotate them directly

    # Pass the nested list structure directly to localisations_tas
    tas_detected = localisations_tas(objects_detected, frames, couleur_equipe_value, elapsed_time)  # Process frames without flattening

    # Display the updated frames at the end of the loop
    for i, frame in enumerate(frames):
        cv2.imshow(windows[i], frame)

    print("Validation des tas :", tas_detected)
    print("__________________________________")


    

    # Send tas_detected to the server

    

    try :
        
        #elapsed_time = wait_start_match(connexion_handle)
        elapsed_time = time.time() - start_time
        send_data(connexion_handle, tas_detected)
    except Exception as e :
        pass

    # Quitter la boucle en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les caméras et fermer les fenêtres
cap_droite.release()
cap_gauche.release()
cap_haut.release()
cv2.destroyAllWindows()

# Close the socket connection
connexion_handle.Close()