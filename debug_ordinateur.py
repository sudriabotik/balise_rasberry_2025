: 640x640 4 canettes, 107.9ms
Speed: 6.8ms preprocess, 107.9ms inference, 1.2ms postprocess per image at shape (1, 3, 640, 640)
Traceback (most recent call last):

  File /usr/lib/python3/dist-packages/spyder_kernels/py3compat.py:356 in compat_exec
    exec(code, globals, locals)

  File /home/ubuntu/Documents/yolo/detection_yolo/main.py:34
    tas_detected = localisations_tas(objects_detected, frames)  # Add rectangles to frames

  File /home/ubuntu/Documents/yolo/detection_yolo/localisation.py:12 in localisations_tas
    coordinates = obj.get('coordinates', [])

AttributeError: 'list' object has no attribute 'get'