from ultralytics import YOLO
import cv2

# Charger le modèle YOLO en mode détection
model = YOLO('/home/ubuntu/Documents/yolo/test/best_canette_ncnn_model', task='detect')

# Définir le pipeline GStreamer pour la Raspberry Pi Camera V2
pipeline = (
    "v4l2src device=/dev/video0 ! "
    "video/x-raw, width=640, height=480, framerate=30/1 ! "
    "videoconvert ! appsink"
)

# Ouvrir la caméra via le pipeline GStreamer
cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra via GStreamer")
    exit()

# Créer une fenêtre redimensionnable pour l'affichage
cv2.namedWindow("Détection en temps réel", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la capture de l'image")
        break

    # Effectuer la détection sur le frame capturé
    results = model(frame)
    annotated_frame = results[0].plot()

    # Afficher l'image annotée
    cv2.imshow("Détection en temps réel", annotated_frame)

    # Quitter en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la caméra et fermer la fenêtre
cap.release()
cv2.destroyAllWindows()
