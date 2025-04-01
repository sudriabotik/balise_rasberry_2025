import cv2
import sys

# Ouvrir la caméra (ici, l'indice 1, modifiez-le si nécessaire)
cap = cv2.VideoCapture("/dev/camera_gauche")
#cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra USB")
    sys.exit()  # Utilisez sys.exit() au lieu de exit()

# Créer une fenêtre redimensionnable pour l'affichage
cv2.namedWindow("Test Camera", cv2.WINDOW_NORMAL)

while True:
    # Capture d'une image depuis la caméra
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la capture de l'image")
        break

    # Afficher l'image capturée dans la fenêtre
    cv2.imshow("Test Camera", frame)

    # Quitter la boucle en appuyant sur la touche 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la caméra et fermer la fenêtre
cap.release()
cv2.destroyAllWindows()

