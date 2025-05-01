from ultralytics import YOLO
import cv2
from setup_camera import setup_cameras

model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_canette_ncnn_model', task='detect')

def process_and_display_frames(frames, windows):

    for frame, window in zip(frames, windows):
        if frame is None:
            print(f"Erreur : Frame non valide pour la fenêtre {window}")
            continue

        results = model(frame)
        annotated_frame = results[0].plot()

        cv2.imshow(window, annotated_frame)

