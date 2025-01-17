# -*- coding: utf-8 -*-

# Crear carpetas para subir los ZIP con las imagenes de cada categoría
!mkdir Perros
!mkdir Coches
!mkdir Aviones

# Commented out IPython magic to ensure Python compatibility.
# Entrar en carpeta y descomprimir el archivo zip

# %cd /content/Perros
!unzip /content/Perros/Perros.zip
# %cd ..
# %cd /content/Coches
!unzip /content/Coches/Coches.zip
# %cd /content/Aviones
!unzip /content/Aviones/Aviones.zip
# %cd ..

# Borrar los archivo ZIP
!rm -rf /content/Coches/Coches.zip
!rm -rf /content/Perros/Perros.zip
!rm -rf /content/Aviones/Aviones.zip

# algunas imagenes de ejemplo para el tfg
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

plt.figure(figsize=(15,15))

carpeta = '/content/Aviones/Aviones'
imagenes = os.listdir(carpeta)

for i, nombreimg in enumerate(imagenes[:25]):
  plt.subplot(5,5,i+1)
  imagen = mpimg.imread(carpeta + '/' + nombreimg)
  plt.imshow(imagen)

# Preparamos carpetas para el set de datos

!mkdir dataset
!mkdir dataset/avion
!mkdir dataset/coche
!mkdir dataset/perro

#  Sacamos por pantalla el número de imágenes de cada categoria
!ls /content/Coches/Coches | wc -l ## 549
!ls /content/Aviones/Aviones| wc -l ## 614
!ls /content/Perros/Perros | wc -l ## 775

# Copiar imágenes y limitar el número de imágenes al menor de los tres


import shutil ## Nos servira para poder copiar o eliminar archivos o colecciones de archivos
carpeta_I = '/content/Aviones/Aviones'
carpeta_D = '/content/dataset/avion'

imagenes = os.listdir(carpeta_I)

for e, catimagenes in enumerate(imagenes):
  if e < 549:
    shutil.copy(carpeta_I + '/' + catimagenes, carpeta_D + '/' + catimagenes)

carpeta_I = '/content/Coches/Coches'
carpeta_D = '/content/dataset/coche'

imagenes = os.listdir(carpeta_I)

for e, catimagenes in enumerate(imagenes):
  if e < 549:
    shutil.copy(carpeta_I + '/' + catimagenes, carpeta_D + '/' + catimagenes)

carpeta_I = '/content/Perros/Perros'
carpeta_D = '/content/dataset/perro'

imagenes = os.listdir(carpeta_I)

for e, catimagenes in enumerate(imagenes):
  if e < 549:
    shutil.copy(carpeta_I + '/' + catimagenes, carpeta_D + '/' + catimagenes)

# Mostramos el número de nuevo y comprobamos que coinciden
!ls /content/dataset/avion| wc -l
!ls /content/dataset/coche | wc -l
!ls /content/dataset/perro | wc -l

# Aumentamos el numero de imágenes mediante el uso de IDG
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np

datagen = ImageDataGenerator(
    rescale=1. / 255,
    rotation_range = 30,
    width_shift_range = 0.25,
    height_shift_range = 0.25,
    shear_range = 15,
    zoom_range = [0.5, 1.5],
    validation_split=0.2 ## Reservamos un 20% para pruebas de validación
)

# Creamos los dos sets que se van a usar
data_gen_entrenamiento = datagen.flow_from_directory('/content/dataset', target_size=(224,224),
                                                     batch_size=32, shuffle=True, subset='training')
data_gen_pruebas = datagen.flow_from_directory('/content/dataset', target_size=(224,224),
                                                     batch_size=32, shuffle=True, subset='validation')

# Imprimimos algunas imágenes para comprobar
for imagen, etiqueta in data_gen_entrenamiento:
  for e in range(10):
    plt.subplot(2,5,e+1)
    plt.xticks([])
    plt.yticks([])
    plt.imshow(imagen[e])
  break
plt.show()

# Importamos google/mobilenet_v2

import tensorflow as tf
import tensorflow_hub as hub

url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/4"
mobilenetv2 = hub.KerasLayer(url, input_shape=(224,224,3))

# Congelamos los datos del modelo cargado
mobilenetv2.trainable = False

model = tf.keras.Sequential(mobilenetv2)

model.summary()

# Añadimos la modificación de la última capa densa para obtener las tres salidas de interés
modelo = tf.keras.Sequential([
    mobilenetv2,
    tf.keras.layers.Dense(3, activation='softmax')
])

modelo.summary()

# Compilamos el modelo
modelo.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Entrenamos el modelo

historial = modelo.fit(
    data_gen_entrenamiento, epochs=25, batch_size=32,
    validation_data=data_gen_pruebas
)

# Creamos algunas graficas para analizar la precisión que ha obtenido nuestro modelo
acc = historial.history['accuracy']
valor_acc = historial.history['valor_accuracy']

loss = historial.history['loss']
valor_loss = historial.history['valor_loss']

rango_epocas = range(25)

plt.figure(figsize=(8,8))
plt.subplot(1,2,1)
plt.plot(rango_epocas, acc, label='Precisión Entrenamiento')
plt.plot(rango_epocas, valor_acc, label='Precisión Pruebas')
plt.legend(loc='lower right')
plt.title('Precisión de entrenamiento y pruebas')

plt.subplot(1,2,2)
plt.plot(rango_epocas, loss, label='Pérdida de entrenamiento')
plt.plot(rango_epocas, valor_loss, label='Pérdida de pruebas')
plt.legend(loc='upper right')
plt.title('Pérdida de entrenamiento y pruebas')
plt.show()

# Analizamos las imágenes de internet mediante su URL
from PIL import Image
import requests
from io import BytesIO
import cv2

def categorizar(url):
  respuesta = requests.get(url)
  img = Image.open(BytesIO(respuesta.content))
  img = np.array(img).astype(float)/255

  img = cv2.resize(img, (224,224))
  prediccion = modelo.predict(img.reshape(-1, 224, 224, 3))
  return np.argmax(prediccion[0], axis=-1)

# 0 = avion, 1 = coche, 2 = perro
url = 'https://cms-gauib.s3.eu-central-1.amazonaws.com/noticias/imagenes/EuroTaller%2C_luces%2C_coche%2C_iluminaci%C3%B3n%2C_noche%2C_nocturno_1557476993.jpg?v=153'
prediccion = categorizar (url)

if prediccion == 0:
  print("Es un avión")
elif prediccion == 1:
  print("Es un coche")
else:
  print("Es un perro")

# Creamos la carpeta para exportarla
!mkdir -p carpeta_final/TFG_Reconocimiento

# Guardar el modelo en formato SavedModel
modelo.save('carpeta_final/TFG_Reconocimiento')

!zip -r modelo_TFG.zip /content/carpeta_final/TFG_Reconocimiento
