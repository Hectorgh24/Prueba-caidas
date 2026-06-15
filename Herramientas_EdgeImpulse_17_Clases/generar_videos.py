import json
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
from matplotlib.animation import FFMpegWriter
import numpy as np

try:
    import imageio_ffmpeg
    plt.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    pass

# Lista de las 17 clases del modelo Edge Impulse (orden alfabético del entrenamiento)
# Las 8 primeras son caídas (fall_*), las 9 restantes son actividades normales
CLASS_LIST = [
    "fall_backward", "fall_bending", "fall_forward",
    "fall_hand", "fall_sideward_left", "fall_sideward_right",
    "fall_sitting", "fall_syncope", "going_down_stairs",
    "going_up_stairs", "jump", "lying_down_fs",
    "run", "sitting_down", "standing_up_fl",
    "standing_up_fs", "walk"
]

# Traducciones al español para las etiquetas visuales del gráfico
CLASS_TRANSLATIONS = {
    "fall_backward": "Caída hacia atrás",
    "fall_bending": "Caída doblándose",
    "fall_forward": "Caída hacia adelante",
    "fall_hand": "Caída sobre manos",
    "fall_sideward_left": "Caída lateral izq.",
    "fall_sideward_right": "Caída lateral der.",
    "fall_sitting": "Caída sentado",
    "fall_syncope": "Caída desmayo",
    "going_down_stairs": "Bajando escaleras",
    "going_up_stairs": "Subiendo escaleras",
    "jump": "Saltando",
    "lying_down_fs": "Acostándose (Silla)",
    "run": "Corriendo",
    "sitting_down": "Sentándose",
    "standing_up_fl": "Levantándose (Suelo)",
    "standing_up_fs": "Levantándose (Silla)",
    "walk": "Caminando"
}

# Índices 0 a 7 son caídas (fall_*), 8 a 16 son actividades normales
FALL_THRESHOLD_INDEX = 8  # className con índice < 8 es caída


def cargar_datos(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generar_video_predicciones(data, output_path):
    history = data.get("predictionHistory", [])
    if not history:
        raise ValueError("El historial de predicciones está vacío.")

    duration = data.get("durationSeconds", 30)
    fps = 30
    # 16:9 Aspect Ratio at 120 DPI = 1920x1080 (1080p Exacto)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    translated_labels = [CLASS_TRANSLATIONS.get(c, c) for c in CLASS_LIST]
    y_positions = list(range(len(CLASS_LIST)))
    max_window = 15.0  # Reducir la ventana a 15 segundos para dar mayor espacio visual entre los números de 1 segundo

    fig.patch.set_facecolor('#1E1E1E')
    ax.set_facecolor('#121212')

    ax.set_yticks(y_positions)
    ax.set_yticklabels(translated_labels, color='#E0E0E0', fontsize=7)
    ax.tick_params(axis='y', colors='#E0E0E0')
    ax.tick_params(axis='x', rotation=45, labelsize=10, colors='#E0E0E0')

    ax.set_title("Línea de Tiempo - Edge Impulse (17 Clases)", color='#FFFFFF', fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Tiempo (segundos)", color='#E0E0E0', fontsize=10, labelpad=10)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.tick_params(axis='x', rotation=45, labelsize=10, colors='#E0E0E0')
    ax.grid(True, which='both', color='#2C2C2C', linestyle='--', linewidth=0.5)

    scatter_normal = ax.scatter([], [], color='#00E5FF', s=50, label='Actividades normales', edgecolors='none')
    scatter_fall = ax.scatter([], [], color='#FF1744', s=60, label='Caídas detectadas', edgecolors='none')
    ax.legend(loc='upper right', facecolor='#1E1E1E', edgecolor='#2C2C2C', labelcolor='#E0E0E0')

    time_line = ax.axvline(x=0, color='#FFC107', linestyle='-', alpha=0.8, linewidth=1.5)

    for spine in ax.spines.values():
        spine.set_color('#2C2C2C')

    def init():
        scatter_normal.set_offsets(np.empty((0, 2)))
        scatter_fall.set_offsets(np.empty((0, 2)))
        time_line.set_xdata([0, 0])
        ax.set_xlim(0, max_window)
        return scatter_normal, scatter_fall, time_line

    def update(frame):
        current_time = frame / fps
        current_predictions = [p for p in history if p['timeSeconds'] <= current_time]
        norm_points = []
        fall_points = []

        for p in current_predictions:
            t = p['timeSeconds']
            class_name = p['className']
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
                # En Edge Impulse 17 clases, los índices 0-7 son caídas (fall_*)
                if y_idx < FALL_THRESHOLD_INDEX:
                    fall_points.append((t, y_idx))
                else:
                    norm_points.append((t, y_idx))

        if norm_points:
            scatter_normal.set_offsets(norm_points)
        else:
            scatter_normal.set_offsets(np.empty((0, 2)))

        if fall_points:
            scatter_fall.set_offsets(fall_points)
        else:
            scatter_fall.set_offsets(np.empty((0, 2)))

        time_line.set_xdata([current_time, current_time])

        if current_time > max_window:
            ax.set_xlim(current_time - max_window, current_time)
        else:
            ax.set_xlim(0, max_window)

        return scatter_normal, scatter_fall, time_line

    frames_total = int(duration * fps) + (2 * fps)
    ani = animation.FuncAnimation(fig, update, frames=frames_total, init_func=init, blit=False, interval=1000 // fps)

    _guardar_animacion(ani, output_path, fps)
    plt.close(fig)


def generar_video_acelerometro(data, output_path):
    sensor_data = data.get("sensorHistory", [])
    if not sensor_data:
        raise ValueError("El historial del sensor está vacío.")

    duration = data.get("durationSeconds", 30)
    fps = 30
    times_ms = np.array([d["timeOffsetMillis"] for d in sensor_data], dtype=float)
    times_s = times_ms / 1000.0
    x_vals = np.array([d["x"] for d in sensor_data], dtype=float)
    y_vals = np.array([d["y"] for d in sensor_data], dtype=float)
    z_vals = np.array([d["z"] for d in sensor_data], dtype=float)

    # 16:9 Aspect Ratio at 120 DPI = 1920x1080 (1080p Exacto)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#1E1E1E')
    ax.set_facecolor('#121212')

    ax.set_title("Datos del Acelerómetro — Edge Impulse 17", color='#FFFFFF', fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Tiempo (segundos)", color='#E0E0E0', fontsize=10, labelpad=10)
    ax.set_ylabel("Aceleración (m/s²)", color='#E0E0E0', fontsize=10, labelpad=10)
    ax.set_ylim(-25, 25)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.tick_params(axis='y', colors='#E0E0E0')
    ax.tick_params(axis='x', rotation=45, labelsize=10, colors='#E0E0E0')
    ax.grid(True, color='#2C2C2C', linestyle='--', linewidth=0.5)

    for spine in ax.spines.values():
        spine.set_color('#2C2C2C')

    line_x, = ax.plot([], [], color='#EF5350', linewidth=1.5, label='Eje X')
    line_y, = ax.plot([], [], color='#66BB6A', linewidth=1.5, label='Eje Y')
    line_z, = ax.plot([], [], color='#42A5F5', linewidth=1.5, label='Eje Z')
    ax.legend(loc='upper right', facecolor='#1E1E1E', edgecolor='#2C2C2C', labelcolor='#E0E0E0')

    visible_window = 15.0

    def init():
        line_x.set_data([], [])
        line_y.set_data([], [])
        line_z.set_data([], [])
        ax.set_xlim(0, visible_window)
        return line_x, line_y, line_z

    def update(frame):
        current_time = frame / fps
        mask = times_s <= current_time
        t_vis = times_s[mask]
        x_vis = x_vals[mask]
        y_vis = y_vals[mask]
        z_vis = z_vals[mask]

        if current_time > visible_window:
            window_mask = t_vis >= (current_time - visible_window)
            t_vis = t_vis[window_mask]
            x_vis = x_vis[window_mask]
            y_vis = y_vis[window_mask]
            z_vis = z_vis[window_mask]
            ax.set_xlim(current_time - visible_window, current_time)
        else:
            ax.set_xlim(0, visible_window)

        line_x.set_data(t_vis, x_vis)
        line_y.set_data(t_vis, y_vis)
        line_z.set_data(t_vis, z_vis)
        return line_x, line_y, line_z

    frames_total = int(duration * fps) + (2 * fps)
    ani = animation.FuncAnimation(fig, update, frames=frames_total, init_func=init, blit=False, interval=1000 // fps)

    _guardar_animacion(ani, output_path, fps)
    plt.close(fig)


def _guardar_animacion(ani, output_path, fps_val):
    # 1. Intentar con aceleración por hardware AMD (AMF)
    try:
        writer_amf = FFMpegWriter(
            fps=fps_val,
            bitrate=8000,
            extra_args=['-vcodec', 'h264_amf', '-pix_fmt', 'yuv420p']
        )
        ani.save(output_path, writer=writer_amf)
        print("Video guardado usando aceleración de hardware AMD (AMF).")
        return
    except Exception as e_amf:
        print(f"No se pudo usar AMD AMF: {e_amf}. Intentando NVIDIA...")
        pass

    # 2. Intentar con aceleración por hardware NVIDIA (NVENC)
    try:
        writer_nvenc = FFMpegWriter(
            fps=fps_val,
            bitrate=8000,
            extra_args=['-vcodec', 'h264_nvenc', '-pix_fmt', 'yuv420p', '-preset', 'fast']
        )
        ani.save(output_path, writer=writer_nvenc)
        print("Video guardado usando aceleración de hardware NVIDIA (NVENC).")
        return
    except Exception as e_nvenc:
        print(f"No se pudo usar NVIDIA NVENC: {e_nvenc}. Usando CPU...")
        pass 

    # 3. Fallback a CPU (libx264 ultrafast)
    try:
        writer_cpu = FFMpegWriter(
            fps=fps_val,
            bitrate=8000,
            extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'ultrafast', '-profile:v', 'high', '-level', '4.0']
        )
        ani.save(output_path, writer=writer_cpu)
        print("Video guardado usando CPU (libx264 ultrafast).")
    except Exception as e1:
        # Fallback a GIF si FFmpeg falla por completo
        output_gif = output_path.replace(".mp4", ".gif")
        try:
            ani.save(output_gif, writer='pillow', fps=fps_val)
        except Exception as e2:
            raise Exception(f"Fallo hardware/CPU: {str(e1)}\n\nFallo GIF: {str(e2)}")

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
    ax.tick_params(axis='x', rotation=45, labelsize=10, colors='#E0E0E0')
    ax.grid(True, which='major', color='#2C2C2C', linestyle='--', linewidth=0.5)

    for spine in ax.spines.values():
        spine.set_color('#2C2C2C')

    line_ram, = ax.plot([], [], color='#FFCA28', linewidth=2.5, label='Consumo PSS (MB)')
    ax.legend(loc='upper right', facecolor='#1E1E1E', edgecolor='#2C2C2C', labelcolor='#E0E0E0')

    visible_window = 15.0

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
