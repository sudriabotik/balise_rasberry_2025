from ultralytics import YOLO
import cv2

# Charger le modèle YOLO avec le chemin fourni
model = YOLO('/home/ubuntu/Documents/yolo/test/best_canette_ncnn_model', task='detect')


# Ouvrir la caméra USB (index 0 par défaut)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra USB")
    exit()
    

# Créer une fenêtre redimensionnable une seule fois
cv2.namedWindow("Détection en temps réel", cv2.WINDOW_NORMAL)

while True:
    # Capture d'une image depuis la caméra
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la capture de l'image")
        break

    # Effectuer la détection sur l'image capturée
    results = model(frame)


    # Récupérer l'image annotée directement sur le flux vidéo
    annotated_frame = results[0].plot()


    # Afficher l'image annotée dans la même fenêtre
    cv2.imshow("Détection en temps réel", annotated_frame)


    # Quitter la boucle en appuyant sur la touche 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la caméra et fermer la fenêtre
cap.release()

cv2.destroyAllWindows()
