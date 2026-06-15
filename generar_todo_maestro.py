import os
import sys

# Mapeo de proyectos y sus respectivos archivos JSON
proyectos = {
    "TensorFlow_17_Clases": r"C:\Develop\JSON-monitoreo\datos-monitoreo-tensorflow-keras-17-clases_20260614_151431.json",
    "TensorFlow_9_Clases": r"C:\Develop\JSON-monitoreo\datos-monitoreo-tensorflow-keras-9-clases_20260614_151705.json",
    "EdgeImpulse_17_Clases": r"C:\Develop\JSON-monitoreo\datos-monitoreo-edgeimpulse17-clases_20260614_191428.json",
    "EdgeImpulse_9_Clases": r"C:\Develop\JSON-monitoreo\datos-monitoreo-EdgeImpulse9-clases_20260614_191857.json"
}

base_dir = r"C:\Develop\Prueba de caidas"
output_dir = r"C:\Develop\Videos_Finales"
os.makedirs(output_dir, exist_ok=True)

for nombre_proyecto, json_path in proyectos.items():
    print(f"\n{'='*50}\nProcesando: {nombre_proyecto}\n{'='*50}")
    
    if not os.path.exists(json_path):
        print(f"ERROR: Archivo JSON no encontrado: {json_path}")
        continue
        
    herramientas_dir = os.path.join(base_dir, f"Herramientas_{nombre_proyecto}")
    sys.path.insert(0, herramientas_dir) # Para poder importar generar_videos de cada carpeta
    
    import generar_videos
    import importlib
    importlib.reload(generar_videos) # Recargar el modulo para asegurar que usa el de la carpeta actual
    
    data = generar_videos.cargar_datos(json_path)
    
    vid_clases = os.path.join(output_dir, f"{nombre_proyecto}_linea_tiempo.mp4")
    vid_accel = os.path.join(output_dir, f"{nombre_proyecto}_acelerometro.mp4")
    vid_ram = os.path.join(output_dir, f"{nombre_proyecto}_memoria_ram.mp4")
    
    print("1/3 Generando gráfico de clases...")
    generar_videos.generar_video_predicciones(data, vid_clases)
    
    print("2/3 Generando gráfico del acelerómetro...")
    generar_videos.generar_video_acelerometro(data, vid_accel)
    
    print("3/3 Generando gráfico de memoria RAM...")
    generar_videos.generar_video_memoria(data, vid_ram)
    
    sys.path.pop(0) # Quitar la ruta para el siguiente proyecto
    print(f"COMPLETADO: {nombre_proyecto}")

print(f"\n¡Todos los videos han sido generados exitosamente en: {output_dir}!")
