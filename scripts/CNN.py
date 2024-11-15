import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
import tensorflow.keras.layers as LK
import tensorflow.keras.models as MK
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
import shutil  # Importar módulo para mover archivos
import numpy as np
import os

# Configuración del generador de datos para cargar imágenes
data_gen = ImageDataGenerator(rescale=1.0/255, validation_split=0.2)

# Cargar datos de entrenamiento desde las carpetas 'fish' y 'trash' dentro de 'train_set'
train_set = data_gen.flow_from_directory(
    'Dataset/train_set',  # Ruta donde están las carpetas 'fish' y 'trash'
    target_size=(28, 28),
    color_mode='rgb',  # Imágenes a color
    batch_size=32,
    class_mode='binary',  # Dos clases: Pez y Basura
    subset='training'  # Subconjunto de entrenamiento
)

# Cargar datos de validación desde las carpetas 'fish' y 'trash' dentro de 'train_set'
test_set = data_gen.flow_from_directory(
    'Dataset/train_set',  # Usando las mismas carpetas de entrenamiento
    target_size=(28, 28),
    color_mode='rgb',  # Imágenes a color
    batch_size=32,
    class_mode='binary',
    subset='validation'  # Subconjunto de validación
)

# Definir el modelo de la red neuronal
entrada = LK.Input(shape=(28, 28, 3))  # Imagen de 28x28x3 (a color)
conv1 = LK.Conv2D(6, (5, 5), padding="same", activation="relu")(entrada)
pool1 = LK.MaxPooling2D((2, 2), (2, 2))(conv1)
conv2 = LK.Conv2D(16, (5, 5), padding="valid", activation="relu")(pool1)
pool2 = LK.MaxPooling2D((2, 2), (2, 2))(conv2)
flat = LK.Flatten()(pool2)
FC1 = LK.Dense(120, activation="relu")(flat)
FC2 = LK.Dense(84, activation="relu")(FC1)
salida = LK.Dense(1, activation="sigmoid")(FC2)  # Salida binaria (Pez o Basura)

modelo = MK.Model(entrada, salida)
modelo.summary()  # Mostrar detalles del modelo

# Compilar el modelo
modelo.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

# Entrenar el modelo
history = modelo.fit(train_set, epochs=20, validation_data=test_set)

# Evaluar el modelo en el conjunto de validación
loss, accuracy = modelo.evaluate(test_set)
print(f"Accuracy en el conjunto de prueba: {accuracy:.2f}")

# Graficar el historial de entrenamiento para ver el rendimiento
plt.plot(history.history['accuracy'], label='Exactitud de Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Exactitud de Validación')
plt.xlabel('Épocas')
plt.ylabel('Exactitud')
plt.legend()
plt.show()

# Guardar el modelo entrenado en un archivo .h5
modelo.save("modelo_entrenado.h5")
print("Modelo guardado en 'modelo_entrenado.h5'")

# Función de predicción en nuevas imágenes (con imágenes individuales en test_set)
def predecir_imagenes_en_test_set():
    ruta_test_set = 'Dataset/Test_set'  # Ruta a la carpeta con las imágenes
    ruta_basura = 'static/processed/trash'  # Ruta para imágenes clasificadas como basura
    ruta_pez = 'static/processed/fish'  # Ruta para imágenes clasificadas como pez

    imagenes = [f for f in os.listdir(ruta_test_set) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]  # Filtrar imágenes

    if not imagenes:
        print("No se encontraron imágenes en la carpeta Test_set.")
        return

    for nombre_imagen in imagenes:
        ruta_imagen = os.path.join(ruta_test_set, nombre_imagen)  # Ruta completa de la imagen
        
        try:
            # Cargar y preprocesar la imagen
            img = image.load_img(ruta_imagen, target_size=(28, 28), color_mode='rgb')  # Ahora a color
            img_array = image.img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Predicción
            prediccion = modelo.predict(img_array, verbose=0)
            clase = "Basura" if prediccion[0][0] > 0.5 else "Pez"
            confianza = prediccion[0][0]

            # Mover la imagen a la carpeta correspondiente
            if clase == "Basura":
                shutil.move(ruta_imagen, os.path.join(ruta_basura, nombre_imagen))
            else:
                shutil.move(ruta_imagen, os.path.join(ruta_pez, nombre_imagen))

            print(f"Imagen: {nombre_imagen} -> Predicción: {clase} con confianza de {confianza:.2f}")

        except Exception as e:
            print(f"Error procesando {nombre_imagen}: {e}")

    print("Predicciones completadas y las imágenes han sido movidas a las carpetas correspondientes.")

# Llamar a la función
predecir_imagenes_en_test_set()
