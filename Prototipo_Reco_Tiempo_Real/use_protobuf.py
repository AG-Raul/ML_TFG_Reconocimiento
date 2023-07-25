
# Uso Ptorobuf

import os
import sys

args = sys.argv  # Obtener los argumentos de línea de comandos proporcionados al script
directory = args[1]
protoc_path = args[2]

for file in os.listdir(directory):
    if file.endswith(".proto"):
        # Ejecutar el comando para invocar el compilador Protobuf y generar archivos de salida
        os.system(protoc_path + " " + directory + "/" + file + " --python_out=.")
