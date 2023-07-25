# Descargarmos el modelo de interes


import wget
import tarfile

model_link = "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8.tar.gz"  # Enlace del modelo a descargar

wget.download(model_link)  # Descargar el modelo utilizando la función 'download' de wget

tar = tarfile.open('ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8.tar.gz')
tar.extractall('.')
tar.close()
