# Creditos a Dan tran
# Conversor de Xml generado por el etiquetado a archivo tipo csv necesario para trabajar con el modelo


import os  # Importar el módulo 'os' para operaciones del sistema operativo
import glob  # Importar el módulo 'glob' para buscar archivos que coincidan con un patrón específico
import pandas as pd  # Importar el módulo 'pandas' para trabajar con estructuras de datos tabulares (DataFrames)
import xml.etree.ElementTree as ET  # Importar el módulo 'ElementTree' del paquete 'xml.etree' para analizar archivos XML

# Definir una función para convertir archivos XML a formato CSV
def xml_to_csv(path):
    xml_list = []  # Lista para almacenar los datos de los archivos XML convertidos a CSV
    for xml_file in glob.glob(path + '/*.xml'):  # Iterar sobre los archivos XML en el directorio especificado
        tree = ET.parse(xml_file)  # Analizar el archivo XML con ElementTree
        root = tree.getroot()  # Obtener el elemento raíz del árbol XML
        for member in root.findall('object'):  # Iterar sobre los elementos 'object' en el XML
            # Extraer los datos relevantes y almacenarlos en una tupla
            value = (root.find('filename').text,
                     int(root.find('size')[0].text),
                     int(root.find('size')[1].text),
                     member[0].text,
                     int(member[4][0].text),
                     int(member[4][1].text),
                     int(member[4][2].text),
                     int(member[4][3].text)
                     )
            xml_list.append(value)  # Agregar la tupla a la lista 'xml_list'
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']  # Nombres de las columnas
    xml_df = pd.DataFrame(xml_list, columns=column_name)  # Crear un DataFrame de pandas con los datos de 'xml_list'
    return xml_df  # Devolver el DataFrame convertido

def main():
    for folder in ['train', 'test']:  # Iterar sobre las carpetas 'train' y 'test'
        image_path = os.path.join(os.getcwd(), ('images/' + folder))  # Obtener la ruta de la carpeta de imágenes
        xml_df = xml_to_csv(image_path)  # Convertir los archivos XML en la carpeta de imágenes a formato CSV
        xml_df.to_csv(('images/'+folder+'_labels.csv'), index=None)  # Guardar el DataFrame como un archivo CSV
    print('Successfully converted xml to csv.')  # Imprimir mensaje de éxito

main()  # Llamar a la función principal para ejecutar el código
