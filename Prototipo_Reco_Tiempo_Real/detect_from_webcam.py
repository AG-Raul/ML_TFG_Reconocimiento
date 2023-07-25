import numpy as np
import argparse
import tensorflow as tf
import cv2

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# Parche para TF1 en `utils.ops`
utils_ops.tf = tf.compat.v1

# Parche para la ubicación de gfile
tf.gfile = tf.io.gfile


def cargar_modelo(ruta_modelo):
    modelo = tf.saved_model.load(ruta_modelo)
    return modelo


def ejecutar_inferencia_para_imagen_individual(modelo, imagen):
    imagen = np.asarray(imagen)
    # La entrada debe ser un tensor, conviértelo usando `tf.convert_to_tensor`.
    tensor_entrada = tf.convert_to_tensor(imagen)
    # El modelo espera un batch de imágenes, así que agrega un eje con `tf.newaxis`.
    tensor_entrada = tensor_entrada[tf.newaxis, ...]
    
    # Ejecutar la inferencia
    output_dict = modelo(tensor_entrada)

    # Todos los resultados son tensores con batches.
    # Conviértelos a arrays numpy y toma el índice [0] para eliminar la dimensión de batch.
    # Solo nos interesan las primeras detecciones (num_detections).
    num_detecciones = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detecciones].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detecciones'] = num_detecciones

    # Las clases de detección deben ser enteros.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)
   
    # Manejar modelos con máscaras:
    if 'detection_masks' in output_dict:
        # Reformatear la máscara bbox al tamaño de la imagen.
        deteccion_mascaras_reframed = utils_ops.reframe_box_masks_to_image_masks(
                                    output_dict['detection_masks'], output_dict['detection_boxes'],
                                    imagen.shape[0], imagen.shape[1])      
        deteccion_mascaras_reframed = tf.cast(deteccion_mascaras_reframed > 0.5, tf.uint8)
        output_dict['detection_masks_reframed'] = deteccion_mascaras_reframed.numpy()
    
    return output_dict


def ejecutar_inferencia(modelo, indice_categorias, captura_video):
    while True:
        ret, imagen_np = captura_video.read()
        # Detección real.
        output_dict = ejecutar_inferencia_para_imagen_individual(modelo, imagen_np)
        # Visualización de los resultados de la detección.
        vis_util.visualize_boxes_and_labels_on_image_array(
            imagen_np,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            indice_categorias,
            instance_masks=output_dict.get('detection_masks_reframed', None),
            use_normalized_coordinates=True,
            line_thickness=8)
        cv2.imshow('object_detection', cv2.resize(imagen_np, (800, 600)))
        if cv2.waitKey(25) & 0xFF == ord('q'):
            captura_video.release()
            cv2.destroyAllWindows()
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detectar objetos en un flujo de video de la webcam')
    parser.add_argument('-m', '--modelo', type=str, required=True, help='Ruta del modelo')
    parser.add_argument('-l', '--etiquetas', type=str, required=True, help='Ruta del archivo de etiquetas')
    args = parser.parse_args()

    modelo_deteccion = cargar_modelo(args.modelo)
    indice_categorias = label_map_util.create_category_index_from_labelmap(args.etiquetas, use_display_name=True)

    captura_video = cv2.VideoCapture(0)
    ejecutar_inferencia(modelo_deteccion, indice_categorias, captura_video)

# Comando : python .\detect_from_webcam.py -m inference_graph\saved_model -l .\labelmap.pbtxt
