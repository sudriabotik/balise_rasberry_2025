import cv2
import time
import os

# Caméras logiques
logical_cameras = ["/dev/camera_gauche", "/dev/camera_droite", "/dev/camera_haut"]
cameras = [os.path.realpath(cam) for cam in logical_cameras]

# Vidéo
width, height, fps = 640, 480, 30
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_dir = "recordings"
os.makedirs(output_dir, exist_ok=True)
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

caps = []
outs = []

# Initialisation
for i, cam_path in enumerate(cameras):
    cap = cv2.VideoCapture(cam_path, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)

    if not cap.isOpened():
        print(f"❌ Impossible d’ouvrir {cam_path}")
        continue

    filename = os.path.join(output_dir, f"camera_{i}_{timestamp}.avi")
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    print(f"✅ Enregistrement de {logical_cameras[i]} ({cam_path}) → {filename}")

    caps.append(cap)
    outs.append(out)

if not caps:
    print("⚠️ Aucune caméra ouverte.")
    exit()

# Enregistrement pendant 5 minutes
print("🎥 Enregistrement sans affichage pendant 5 min.")
start_time = time.time()
duration = 8 * 60  # secondes

try:
    while time.time() - start_time < duration:
        for i, cap in enumerate(caps):
            ret, frame = cap.read()
            if ret:
                outs[i].write(frame)
        time.sleep(1 / fps)

finally:
    for cap in caps:
        cap.release()
    for out in outs:
        out.release()
    print("✅ Terminé.")
