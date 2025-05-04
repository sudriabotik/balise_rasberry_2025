import cv2

#frame droite 
rectangle4 = (130, 250, 370, 420)  # vert
rectangle8 = (560, 130, 750, 255) 

tas_4 = 0
tas_8 = 0

#frame gauche
rectangle5 = (130, 250, 370, 420)  # vert
rectangle1 = (560, 130, 750, 255) 

tas_5 = 0
tas_1 = 0

#frame haut
rectangle2 = (130, 250, 370, 420)  # vert
rectangle3 = (560, 130, 750, 255)
rectangle6 = (130, 250, 370, 420)  # vert
rectangle7 = (560, 130, 750, 255)

tas_2 = 0
tas_3 = 0
tas_6 = 0
tas_7 = 0


def localisations_tas(objects_detected_by_frame, frames,equipe="bleu"):
    # Define rectangles for each frame
    rectangles_by_frame = [
        [(rectangle4, 'tas_4'), (rectangle8, 'tas_8')],  # Frame 0 (droite)
        [(rectangle5, 'tas_5'), (rectangle1, 'tas_1')],  # Frame 1 (gauche)
        [(rectangle2, 'tas_2'), (rectangle3, 'tas_3'), (rectangle6, 'tas_6'), (rectangle7, 'tas_7')]  # Frame 2 (haut)
    ]

    tas_counts = {
        'tas_4': 0, 'tas_8': 0, 'tas_5': 0, 'tas_1': 0,
        'tas_2': 0, 'tas_3': 0, 'tas_6': 0, 'tas_7': 0
    }

    for frame_index, objects_detected in enumerate(objects_detected_by_frame):
        if frame_index >= len(rectangles_by_frame):
            print(f"No rectangles defined for frame {frame_index}, skipping.")
            continue

        for obj in objects_detected:
            coordinates = obj.get('coordinates', [])
            if len(coordinates) < 4:
                print("Invalid detection coordinates, skipping.")
                continue

            center_x = (coordinates[0] + coordinates[2]) / 2  # Calculate center x
            center_y = (coordinates[1] + coordinates[3]) / 2  # Calculate center y

            for rectangle, tas_name in rectangles_by_frame[frame_index]:
                if is_inside_rectangle((center_x, center_y), rectangle):
                    tas_counts[tas_name] += 1

        # Draw rectangles on the corresponding frame
        for rectangle, _ in rectangles_by_frame[frame_index]:
            cv2.rectangle(
                frames[frame_index],
                (rectangle[0], rectangle[1]),
                (rectangle[2], rectangle[3]),
                (0, 255, 0), 2  # Green rectangle
            )

    # Validate piles based on the number of objects inside each rectangle
    pile_validations = {
        'tas_4': tas_counts['tas_4'] >= 3,
        'tas_8': tas_counts['tas_8'] >= 3,
        'tas_5': tas_counts['tas_5'] >= 3,
        'tas_1': tas_counts['tas_1'] >= 3,
        'tas_2': tas_counts['tas_2'] >= 3,
        'tas_3': tas_counts['tas_3'] >= 3,
        'tas_6': tas_counts['tas_6'] >= 3,
        'tas_7': tas_counts['tas_7'] >= 3
    }

    changement_equipe(pile_validations, equipe)  # Change team if needed

    return pile_validations

def is_inside_rectangle(coord, rectangle):
    x_min, y_min, x_max, y_max = rectangle
    x, y = coord
    return x_min <= x <= x_max and y_min <= y <= y_max

def changement_equipe(tas, equipe="bleue"):
    # Par défaut, on est équipe bleue. Si on est équipe jaune, on échange les valeurs des tas.
    if equipe == "jaune":
        tas['tas_8'], tas['tas_5'] = tas['tas_5'], tas['tas_8']
        tas['tas_4'], tas['tas_1'] = tas['tas_1'], tas['tas_4']
        tas['tas_2'], tas['tas_3'] = tas['tas_3'], tas['tas_2']
        tas['tas_6'], tas['tas_7'] = tas['tas_7'], tas['tas_6']
    return tas
