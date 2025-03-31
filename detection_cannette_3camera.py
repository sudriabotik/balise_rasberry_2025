from ultralytics import YOLO
import cv2
import sys
import time

def capture_fresh_image(cap, flush_count=5):
    """
    Vide le tampon de la caméra en appelant cap.grab() plusieurs fois,
    puis capture et retourne la dernière image.
    """
    for _ in range(flush_count):
        cap.grab()
    return cap.read()

# Charger le modèle YOLO en mode détection
model = YOLO('/home/ubuntu/Documents/yolo/test/best_canette_ncnn_model', task='detect')

# Ouvrir les caméras (ajustez les indices selon votre configuration)
cap0 = cv2.VideoCapture(5)
cap1 = cv2.VideoCapture(1)
cap2 = cv2.VideoCapture(2)

if not cap0.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 0")
    sys.exit()
if not cap1.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 1")
    sys.exit()
if not cap2.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra 2")
    sys.exit()

# Créer des fenêtres redimensionnables pour l'affichage
cv2.namedWindow("Detection Camera 0", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 1", cv2.WINDOW_NORMAL)
cv2.namedWindow("Detection Camera 2", cv2.WINDOW_NORMAL)

while True:
    cycle_start = time.time()  # Début du cycle

    # Capture "fraîche" des images en vidant le tampon
    start_cap = time.time()
    ret0, frame0 = capture_fresh_image(cap0)
    ret1, frame1 = capture_fresh_image(cap1)
    ret2, frame2 = capture_fresh_image(cap2)
    cap_duration = (time.time() - start_cap) * 1000  # en ms

    if not ret0:
        print("Erreur lors de la capture de la caméra 0")
        break
    if not ret1:
        print("Erreur lors de la capture de la caméra 1")
        break
    if not ret2:
        print("Erreur lors de la capture de la caméra 2")
        break

    # Traitement avec YOLO
    start_det = time.time()
    results0 = model(frame0)
    results1 = model(frame1)
    results2 = model(frame2)
    det_duration = (time.time() - start_det) * 1000  # en ms

    # Annotation des résultats
    start_ann = time.time()
    annotated_frame0 = results0[0].plot()
    annotated_frame1 = results1[0].plot()
    annotated_frame2 = results2[0].plot()
    ann_duration = (time.time() - start_ann) * 1000  # en ms

    # Affichage des images
    start_disp = time.time()
    cv2.imshow("Detection Camera 0", annotated_frame0)
    cv2.imshow("Detection Camera 1", annotated_frame1)
    cv2.imshow("Detection Camera 2", annotated_frame2)
    disp_duration = (time.time() - start_disp) * 1000  # en ms

    cycle_duration = (time.time() - cycle_start) * 1000  # temps total du cycle

    print(f"Cycle total: {cycle_duration:.2f} ms | Capture: {cap_duration:.2f} ms, "
          f"Détection: {det_duration:.2f} ms, Annotation: {ann_duration:.2f} ms, "
          f"Affichage: {disp_duration:.2f} ms ___________________________________________________________________________________")

    # Quitter la boucle en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les caméras et fermer les fenêtres
cap0.release()
cap1.release()
cap2.release()
cv2.destroyAllWindows()
