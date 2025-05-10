from setup_camera import setup_cameras
from detection_yolo import process_frames
from localisation import localisations_tas
import cv2
from communication_client import setup_connexion, send_data, couleur_equipe, wait_start_match
from ecrans_lcd import setup_lcd

 
# Initialiser les caméras
cap_droite, cap_gauche, cap_haut = setup_cameras()

# Establish connection to the server
socket_conn = setup_connexion()

# Créer trois fenêtres redimensionnables pour l'affichage des détections
cv2.namedWindow("Camera droite", cv2.WINDOW_NORMAL)
cv2.namedWindow("Camera gauche", cv2.WINDOW_NORMAL)
cv2.namedWindow("Camera haut", cv2.WINDOW_NORMAL)

lcd = setup_lcd()

# Boucle pour attendre la réception de la couleur de l'équipe
couleur_equipe_value = "bleu"
couleur_equipe_value = couleur_equipe(socket_conn, lcd)
print(f"Couleur de l'équipe reçue : {couleur_equipe_value}") 
elapsed_time = 0
