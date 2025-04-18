from ultralytics import YOLO
import cv2
import os
import glob

# Charger le modèle YOLO avec le chemin fourni
model = YOLO('/home/ubuntu/Documents/yolo/test/best_canette_ncnn_model')

# Dossier contenant les images à traiter
image_folder = '/home/ubuntu/Documents/yolo/test/'

# Dossier où sauvegarder les images annotées
save_folder = '/home/ubuntu/Documents/yolo/test/result_image/'
os.makedirs(save_folder, exist_ok=True)

# Obtenir la liste des images JPG dans le dossier
image_files = glob.glob(os.path.join(image_folder, "*.jpg"))

# Traitement de chaque image
for image_path in image_files:
    # Effectuer la détection sur l'image
    results = model(image_path)
    
    # Récupérer l'image annotée à partir du résultat
    annotated_image = results[0].plot()
    
    # Afficher la dimension pour vérification
    print("Dimensions de l'image annotée :", annotated_image.shape)

    # Optionnel : redimensionner l'image si elle est trop petite
    scale_factor = 2  # Modifier ce facteur selon vos besoins
    annotated_image = cv2.resize(annotated_image, (annotated_image.shape[1]*scale_factor,
                                                    annotated_image.shape[0]*scale_factor))

    # Sauvegarder l'image annotée dans le dossier de résultats
    filename = os.path.basename(image_path)
    save_path = os.path.join(save_folder, filename)
    cv2.imwrite(save_path, annotated_image)

    # Créer une fenêtre redimensionnable et afficher l'image
    cv2.namedWindow("Résultat de YOLO", cv2.WINDOW_NORMAL)
    cv2.imshow("Résultat de YOLO", annotated_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

print("Visualisation terminée !")
