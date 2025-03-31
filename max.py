from ultralytics import YOLO
import cv2
import sys
import time

# Charger le modèle YOLO en mode détection
model = YOLO('/home/ubuntu/Documents/yolo/test/best_canette_ncnn_model', task='detect')


# Ouvrir la caméra 0 et la caméra 1
cap = cv2.VideoCapture(1)
cap0 = cv2.VideoCapture(5)
cap1 = cv2.VideoCapture(2)

if not cap0.isOpened():
    print("Erreur : Impossible d'ouvrir la camera 0")
    sys.exit()
if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la camera 1")
    sys.exit()
if not cap1.isOpened():
    print("Erreur : Impossible d'ouvrir la camera 2")
    sys.exit()

# Créer deux fenêtres redimensionnables pour l'affichage
cv2.namedWindow("Detection Camera 0", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 2", cv2.WINDOW_NORMAL)

while True:
    loop_start = time.time()  # Début de la boucle
    # Capture d'une image depuis chaque caméra
    ret0, frame0 = cap0.read()
    ret1, frame1 = cap.read()
    ret2, frame2 = cap1.read()
    capture_time = time.time() - loop_start

    if not ret0:
        print("Erreur lors de la capture de la camera 0")
        break
    if not ret1:
        print("Erreur lors de la capture de la camera 1")
        break
    if not ret2:
        print("Erreur lors de la capture de la camera 2")
        break

    # Effectuer la détection sur chaque frame
    detection_start = time.time()
    results0 = model(frame0)#, imgsz=1200)
    results1 = model(frame1)#, imgsz=1200)
    results2 = model(frame2)#, imgsz=1200)
    detection_time = time.time() - detection_start

    # Récupérer les images annotées
    annotation_start = time.time()
    annotated_frame1 = results1[0].plot()
    annotated_frame0 = results0[0].plot()
    annotated_frame3 = results2[0].plot()
    annotation_time = time.time() - annotation_start
    

    # Afficher les images annotées dans leurs fenêtres respectives
    display_start = time.time()
    cv2.imshow("Detection Camera 0", annotated_frame0)
    cv2.imshow("Detection Camera 1", annotated_frame1)
    cv2.imshow("Detection Camera 2", annotated_frame3)
    display_time = time.time() - display_start
    
    print(f"Temps de capture : {capture_time:.3f} s, "
          f"Temps de détection : {detection_time:.3f} s, "
          f"Temps d'annotation : {annotation_time:.3f} s, "
          f"Temps d'affichage : {display_time:.3f} s")

    # Quitter la boucle en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les caméras et fermer les fenêtres
cap0.release()
cap.release()
cap1.release()
cv2.destroyAllWindows()
