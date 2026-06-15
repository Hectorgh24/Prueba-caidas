import os
import glob

base_path = r"C:\Develop\Prueba de caidas"

def inject_generar_video_memoria():
    ram_func = """
def generar_video_memoria(data, output_path):
    memory_data = data.get("memoryHistory", [])
    if not memory_data:
        print("Aviso: El historial de memoria RAM está vacío, omitiendo video.")
        return

    duration = data.get("durationSeconds", 30)
    fps = 30
    
    times_s = np.array([d["timeSeconds"] for d in memory_data], dtype=float)
    ram_vals = np.array([d["ramMB"] for d in memory_data], dtype=float)

    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#1E1E1E')
    ax.set_facecolor('#121212')

    ax.set_title("Consumo de Memoria RAM (MB)", color='#FFFFFF', fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Tiempo (segundos)", color='#E0E0E0', fontsize=10, labelpad=10)
    ax.set_ylabel("Memoria RAM (MB)", color='#E0E0E0', fontsize=10, labelpad=10)
    
    min_ram = max(0, np.min(ram_vals) - 5)
    max_ram = np.max(ram_vals) + 5
    ax.set_ylim(min_ram, max_ram)
    
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.tick_params(axis='y', colors='#E0E0E0')
    ax.tick_params(axis='x', rotation=90, labelsize=8, colors='#E0E0E0')
    ax.grid(True, which='major', color='#2C2C2C', linestyle='--', linewidth=0.5)

    for spine in ax.spines.values():
        spine.set_color('#2C2C2C')

    line_ram, = ax.plot([], [], color='#FFCA28', linewidth=2.5, label='Consumo PSS (MB)')
    ax.legend(loc='upper right', facecolor='#1E1E1E', edgecolor='#2C2C2C', labelcolor='#E0E0E0')

    visible_window = 120.0

    def init():
        line_ram.set_data([], [])
        ax.set_xlim(0, visible_window)
        return line_ram,

    def update(frame):
        current_time = frame / fps
        mask = times_s <= current_time
        t_vis = times_s[mask]
        r_vis = ram_vals[mask]

        if current_time > visible_window:
            window_mask = t_vis >= (current_time - visible_window)
            t_vis = t_vis[window_mask]
            r_vis = r_vis[window_mask]
            ax.set_xlim(current_time - visible_window, current_time)
        else:
            ax.set_xlim(0, visible_window)

        line_ram.set_data(t_vis, r_vis)
        return line_ram,

    frames_total = int(duration * fps) + (2 * fps)
    ani = animation.FuncAnimation(fig, update, frames=frames_total, init_func=init, blit=False, interval=1000 // fps)

    _guardar_animacion(ani, output_path, fps)
    plt.close(fig)
"""

    for folder in glob.glob(os.path.join(base_path, "Herramientas_*")):
        gen_vid_path = os.path.join(folder, "generar_videos.py")
        if os.path.exists(gen_vid_path):
            with open(gen_vid_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "def generar_video_memoria" not in content:
                content += "\n" + ram_func
                with open(gen_vid_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Modificado {gen_vid_path}")

def update_interfaz_grafica():
    replacement = """
            prefijo = os.path.basename(os.path.dirname(os.path.abspath(__file__))).replace("Herramientas_", "")
            video_pred = os.path.join(OUTPUT_DIR, f"{prefijo}_linea_tiempo.mp4")
            video_accel = os.path.join(OUTPUT_DIR, f"{prefijo}_acelerometro.mp4")
            video_ram = os.path.join(OUTPUT_DIR, f"{prefijo}_memoria_ram.mp4")
            
            # Eliminar versiones viejas
            for v in [video_pred, video_accel, video_ram]:
                if os.path.exists(v): os.remove(v)
                if os.path.exists(v.replace(".mp4", ".gif")): os.remove(v.replace(".mp4", ".gif"))
            
            root.after(0, lambda: lbl_status.config(text="Generando video 1/3 (Grafico de clases)...", fg="blue"))
            generar_videos.generar_video_predicciones(data, video_pred)
            
            root.after(0, lambda: lbl_status.config(text="Generando video 2/3 (Acelerometro)...", fg="blue"))
            generar_videos.generar_video_acelerometro(data, video_accel)
            
            root.after(0, lambda: lbl_status.config(text="Generando video 3/3 (Memoria RAM)...", fg="blue"))
            generar_videos.generar_video_memoria(data, video_ram)
            
            root.after(0, lambda: lbl_status.config(text="Exito: Videos generados correctamente.", fg="green"))
            root.after(0, lambda: messagebox.showinfo("Proceso Completado", f"Los videos se han guardado exitosamente en la carpeta:\\n\\n{OUTPUT_DIR}\\n\\n(Los 3 videos han sido generados)"))
"""
    for folder in glob.glob(os.path.join(base_path, "Herramientas_*")):
        ui_path = os.path.join(folder, "interfaz_grafica.py")
        if os.path.exists(ui_path):
            with open(ui_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "video_ram" not in content:
                # Find the start of the block to replace
                start_idx = content.find("video_pred = os.path.join(OUTPUT_DIR")
                # Find the end of the block to replace
                end_idx = content.find("except Exception as e:", start_idx)
                
                if start_idx != -1 and end_idx != -1:
                    new_content = content[:start_idx] + replacement.strip() + "\n            \n        " + content[end_idx:]
                    with open(ui_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Modificado {ui_path}")

if __name__ == "__main__":
    inject_generar_video_memoria()
    update_interfaz_grafica()
    print("Todo listo.")
