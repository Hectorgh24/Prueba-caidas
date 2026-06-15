import os

src_dir = r"c:\Users\HECTO\AndroidStudioProjects\AplicacionTensorFlowAndKeras17\python_tools"
dst_dir = r"c:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app\python_tools"

with open(os.path.join(src_dir, "interfaz_grafica.py"), "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("17 Clases", "9 Clases")
content = content.replace("TensorFlowKeras17", "TensorFlowKeras9")

with open(os.path.join(dst_dir, "interfaz_grafica.py"), "w", encoding="utf-8") as f:
    f.write(content)

with open(os.path.join(src_dir, "generar_videos.py"), "r", encoding="utf-8") as f:
    content_gen = f.read()

class_list_17 = """CLASS_LIST = [
    "Caminando", "Subiendo escaleras", "Bajando escaleras", "Sentado", 
    "De pie", "Levantandose", "Acostado", "Sientandose", "Agachandose", 
    "Caida frontal", "Caida a la derecha", "Caida hacia atras",
    "Caida contra obstaculo", "Caida (intentando protegerse)", 
    "Caida al sentarse", "Desmayo / Sincope", "Caida a la izquierda"
]"""

class_list_9 = """CLASS_LIST = [
    "Caminando",
    "Caída frontal",
    "Caída a la derecha",
    "Caída hacia atrás",
    "Caída contra obstáculo",
    "Caída (intentando protegerse)",
    "Caída al sentarse",
    "Desmayo / Síncope",
    "Caída a la izquierda"
]"""

content_gen = content_gen.replace(class_list_17, class_list_9)
content_gen = content_gen.replace("17 Clases", "9 Clases")
content_gen = content_gen.replace("y_idx >= 9", "y_idx >= 1")
content_gen = content_gen.replace("índices >= 9", "índices >= 1")

with open(os.path.join(dst_dir, "generar_videos.py"), "w", encoding="utf-8") as f:
    f.write(content_gen)

print("Archivos copiados y adaptados exitosamente.")
