import os
import glob

base_path = r"C:\Develop\Prueba de caidas"

def fix_class_matching():
    for folder in glob.glob(os.path.join(base_path, "Herramientas_*")):
        gen_vid_path = os.path.join(folder, "generar_videos.py")
        if not os.path.exists(gen_vid_path): continue
            
        with open(gen_vid_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Reemplazar la logica estricta por logica tolerante a encoding/acentos
        old_logic = """
            if class_name in CLASS_LIST:
                y_idx = CLASS_LIST.index(class_name)
"""
        new_logic = """
            import unicodedata
            def norm(s): return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower().strip()
            
            n_class_name = norm(class_name)
            norm_class_list = [norm(c) for c in CLASS_LIST]
            
            y_idx = -1
            if n_class_name in norm_class_list:
                y_idx = norm_class_list.index(n_class_name)
            else:
                for i, c in enumerate(norm_class_list):
                    if c in n_class_name or n_class_name in c:
                        y_idx = i
                        break
                        
            if y_idx != -1:
"""
        if "if class_name in CLASS_LIST:" in content:
            content = content.replace(old_logic, new_logic)
            with open(gen_vid_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Lógica de emparejamiento corregida en: {gen_vid_path}")

if __name__ == "__main__":
    fix_class_matching()
    print("Correcciones aplicadas.")
