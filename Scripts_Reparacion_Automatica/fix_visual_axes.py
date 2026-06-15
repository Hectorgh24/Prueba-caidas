import os
import glob

base_path = r"C:\Develop\Prueba de caidas"

def fix_visuals():
    for folder in glob.glob(os.path.join(base_path, "Herramientas_*")):
        gen_vid_path = os.path.join(folder, "generar_videos.py")
        if os.path.exists(gen_vid_path):
            with open(gen_vid_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 1. Unificar ventanas a 15 segundos para evitar superposicion y mantener consistencia
            content = content.replace("max_window = 15", "max_window = 15.0")
            content = content.replace("visible_window = 10.0", "visible_window = 15.0")
            content = content.replace("visible_window = 120.0", "visible_window = 15.0")
            content = content.replace("visible_window = 20.0", "visible_window = 15.0")

            # 2. Mejorar la legibilidad de los numeros en el eje X (1 segundo de intervalo)
            # Cambiamos rotacion de 90 a 45 o 0 y subimos tamano de fuente
            content = content.replace("rotation=90, labelsize=8", "rotation=45, labelsize=10")
            content = content.replace("rotation=90", "rotation=45")
            
            with open(gen_vid_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Mejorado aspecto visual en {gen_vid_path}")

if __name__ == "__main__":
    fix_visuals()
    print("Correcciones visuales aplicadas.")
