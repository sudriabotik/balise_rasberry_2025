import cv2
import sys

device = "/dev/camera_haut"
cap = cv2.VideoCapture(4)

if not cap.isOpened():
    print(f"Erreur : Impossible d'ouvrir la caméra {device}")
    sys.exit()

# 🔍 Lire le format FOURCC
fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
fourcc_str = "".join([chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)])
print(f"🎥 Format vidéo utilisé par {device} : {fourcc_str}")

# Créer une fenêtre redimensionnable pour l'affichage
cv2.namedWindow("Test Camera", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la capture de l'image")
        break

    cv2.imshow("Test Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
