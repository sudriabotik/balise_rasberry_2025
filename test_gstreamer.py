import cv2
import sys



# Ouvrir la caméra avec l'index approprié et en forçant le backend FFMPEG
cap = cv2.VideoCapture(1, cv2.CAP_FFMPEG)


if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra")
    sys.exit()

# Configurer la résolution et le framerate
# Note : Ces réglages dépendent du support de la caméra et peuvent ne pas être appliqués si la caméra ne les supporte pas.
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
cap.set(cv2.CAP_PROP_FPS, 5)

cv2.namedWindow("Test Camera (FFMPEG)", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la capture d'image")
        break

    cv2.imshow("Test Camera (FFMPEG)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
