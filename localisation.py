import cv2

def localisations_tas(objects_detected, frames):
    # Define the two predefined rectangles (x_min, y_min, x_max, y_max)
    rectangle1 = (50, 50, 200, 200)  
    rectangle2 = (300, 50, 450, 200) 

    pile1_count = 0
    pile2_count = 0

    for obj in objects_detected:
        coordinates = obj.get('coordinates', [])
        if len(coordinates) < 4:
            print("Invalid detection coordinates, skipping.")
            continue

        center_x = (coordinates[0] + coordinates[2]) / 2  # Calculate center x
        center_y = (coordinates[1] + coordinates[3]) / 2  # Calculate center y

        if is_inside_rectangle((center_x, center_y), rectangle1):
            pile1_count += 1
        elif is_inside_rectangle((center_x, center_y), rectangle2):
            pile2_count += 1

    for frame in frames:
        # Draw rectangles on each frame
        cv2.rectangle(frame, (rectangle1[0], rectangle1[1]), (rectangle1[2], rectangle1[3]), (0, 255, 0), 2)  # Green rectangle
        cv2.rectangle(frame, (rectangle2[0], rectangle2[1]), (rectangle2[2], rectangle2[3]), (255, 0, 0), 2)  # Blue rectangle

    # Validate piles based on the number of objects inside each rectangle
    pile1_validated = pile1_count >= 3
    pile2_validated = pile2_count >= 3

    return [pile1_validated, pile2_validated]

def is_inside_rectangle(coord, rectangle):
    x_min, y_min, x_max, y_max = rectangle
    x, y = coord
    return x_min <= x <= x_max and y_min <= y <= y_max
