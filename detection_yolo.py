from ultralytics import YOLO
import cv2
from setup_camera import setup_cameras

model = YOLO('/home/ubuntu/Documents/yolo/detection_yolo/best_V2_ncnn_model', task='detect')

def process_frames(frames):
    """
    Process frames to detect objects and annotate them with detection rectangles.

    Args:
        frames: List of frames to process.

    Returns:
        A list of detected objects for each frame.
    """
    detections = []
    for i, frame in enumerate(frames):
        if frame is None:
            detections.append([])
            continue

        results = model(frame)
        detections.append(extract_detections_coordonates(results))

        # Annotate the frame directly with detection rectangles
        frames[i] = results[0].plot()

    return detections

def extract_detections_coordonates(results):
    """
    Extracts the coordinates and class of each detected object from the model results.

    Args:
        results: The results from the YOLO model.

    Returns:
        A list of dictionaries, each containing 'coordinates' and 'class' of a detected object.
    """
    detections = []
    for result in results:
        for box in result.boxes:
            if box.xyxy is not None and len(box.xyxy[0]) == 4:  # Ensure coordinates are valid
                detection = {
                    'coordinates': box.xyxy[0].tolist(),  # Convert coordinates to a list
                    'class': box.cls[0].item() if box.cls is not None else None  # Class of the detected object
                }
                detections.append(detection)
    return detections



