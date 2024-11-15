from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import os
import shutil
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image # type: ignore

app = Flask(__name__)
CORS(app)

# Directorios de entrada y salida
input_dir = "./static/imagenesDib"
output_fish_dir = "./static/processed/fish"
output_trash_dir = "./static/processed/trash"
js_file_path = "./templates/script.js"

# Función para limpiar directorios
def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Limpiar las carpetas antes de procesar
clear_directory(output_fish_dir)
clear_directory(output_trash_dir)
os.makedirs(output_fish_dir, exist_ok=True)
os.makedirs(output_trash_dir, exist_ok=True)

# Cargar modelo previamente entrenado
modelo = tf.keras.models.load_model('modelo_entrenado.h5')

# Función para eliminar el fondo de la imagen y guardar en PNG con transparencia
import cv2
import numpy as np

# Función para eliminar el fondo de la imagen y guardar en PNG con transparencia
def remove_background(img_path):
    # Leer la imagen
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    
    # Convertir la imagen a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Usar un filtro Gaussiano para suavizar la imagen y reducir ruido
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Umbral adaptativo para detectar el objeto en la imagen
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # Encontrar contornos de la imagen
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Crear una máscara para el objeto principal
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)
    
    # Crear una imagen con fondo transparente
    result = cv2.bitwise_and(img, img, mask=mask)
    
    # Crear la imagen con fondo transparente (canal alfa)
    rgba_img = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    
    # Establecer a 0 (transparente) el canal alfa donde no hay objeto
    rgba_img[:, :, 3] = mask
    
    # Guardar la imagen con fondo transparente
    return rgba_img

# Procesar y etiquetar imágenes
def predecir_imagen(img_path):
    img = image.load_img(img_path, target_size=(28, 28), color_mode='rgb')  # Cargar la imagen en RGB
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediccion = modelo.predict(img_array, verbose=0)
    return "fish" if prediccion[0][0] <= 0.5 else "trash"

def process_images():
    images = os.listdir(input_dir)
    for image_name in images:
        img_path = os.path.join(input_dir, image_name)
        
        # Predecir la etiqueta de la imagen original
        label = predecir_imagen(img_path)
        
        # Remover el fondo de la imagen y guardar en PNG con transparencia
        processed_img = remove_background(img_path)
        
        # Guardar la imagen sin fondo en formato PNG
        temp_path = os.path.join(input_dir, f"processed_{image_name.split('.')[0]}.png")
        cv2.imwrite(temp_path, processed_img)
        
        # Mover la imagen a la carpeta correspondiente según la predicción
        output_path = os.path.join(output_fish_dir if label == "fish" else output_trash_dir, f"{image_name.split('.')[0]}.png")
        shutil.move(temp_path, output_path)
        
        # Borrar la imagen original con fondo
        os.remove(img_path)

def get_image_paths(directory):
    return [f'"/static/{os.path.relpath(os.path.join(directory, filename), "./static").replace("\\", "/")}"' for filename in os.listdir(directory)]

@app.route('/upload', methods=['POST'])
def upload_images():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('file')  # Obtener todos los archivos subidos
    if not files:
        return jsonify({"error": "No selected files"}), 400

    for file in files:
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Guardar la imagen en la carpeta 'imagenesDib'
        file_path = os.path.join(input_dir, file.filename)
        file.save(file_path)

    return jsonify({"message": "Files uploaded successfully"}), 200

@app.route('/process_images', methods=['POST'])
def process_images_route():
    clear_directory(output_fish_dir)
    clear_directory(output_trash_dir)
    process_images()
    update_js_file()
    return jsonify({"message": "Images processed and JS file updated."})

def update_js_file():
    fish_images = get_image_paths(output_fish_dir)
    trash_images = get_image_paths(output_trash_dir)
    fish_images_js = f"const fishImages = [{', '.join(fish_images)}];\n"
    trash_images_js = f"const trashImages = [{', '.join(trash_images)}];\n"
    with open(js_file_path, "r") as file:
        js_content = file.readlines()
    with open(js_file_path, "w") as file:
        for line in js_content:
            if line.strip().startswith("const fishImages ="):
                file.write(fish_images_js)
            elif line.strip().startswith("const trashImages ="):
                file.write(trash_images_js)
            else:
                file.write(line)

@app.route('/')
def home():
    return "Flask app is running"

if __name__ == "__main__":
    app.run(debug=True)
