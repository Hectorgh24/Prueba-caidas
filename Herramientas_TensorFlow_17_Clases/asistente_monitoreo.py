import tkinter as tk
from tkinter import ttk
# pyrefly: ignore [missing-import]
import pyttsx3
import threading
import time

class AsistenteMonitoreoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Asistente de Monitoreo de Caídas")
        self.root.geometry("600x400")
        self.root.configure(bg="#2b2b2b")
        self.root.resizable(False, False)

        self.tiempo_actual = 0
        self.en_ejecucion = False
        self.hilo_cronometro = None
        self.duracion_total = 120

        # Configurar motor de voz
        self.engine = pyttsx3.init()
        # Intentar configurar una voz en español
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "spanish" in voice.name.lower() or "español" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 150) # Velocidad del habla

        # Tabla de intervalos: (tiempo_inicio, etiqueta_hablada, descripcion_ui)
        self.intervalos = [
            (0, "standing_up", "Preparación y calibración (standing_up)"),
            (10, "walk", "Caminata de rutina (walk)"),
            (20, "running", "Actividad de impacto (running)"),
            (30, "sitting_down", "Transición postural (sitting_down)"),
            (45, "fall_sideward_left", "Primera simulación de caída (fall_sideward_left)"),
            (55, "walk", "Caminata de recuperación (walk)"),
            (65, "fall_backward", "Segunda simulación de caída (fall_backward)"),
            (75, "walk", "Caminata previa al evento crítico (walk)"),
            (85, "fall_forward", "Tercera simulación de caída (fall_forward)"),
            (90, "lying_down", "Periodo post-caída (lying_down)"),
        ]

        self._crear_interfaz()

    def _crear_interfaz(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Título
        lbl_titulo = tk.Label(main_frame, text="Protocolo de Pruebas: 120 Segundos", 
                              font=("Arial", 18, "bold"), bg="#2b2b2b", fg="#ffffff")
        lbl_titulo.pack(pady=(0, 20))

        # Contador de tiempo
        self.lbl_tiempo = tk.Label(main_frame, text="00:00", 
                                   font=("Courier", 48, "bold"), bg="#2b2b2b", fg="#4caf50")
        self.lbl_tiempo.pack(pady=10)

        # Etiqueta actual
        self.lbl_etiqueta_actual = tk.Label(main_frame, text="Esperando para iniciar...", 
                                            font=("Arial", 14), bg="#2b2b2b", fg="#ffeb3b", wraplength=500)
        self.lbl_etiqueta_actual.pack(pady=10)

        # Próxima etiqueta
        self.lbl_proxima_etiqueta = tk.Label(main_frame, text="", 
                                             font=("Arial", 12, "italic"), bg="#2b2b2b", fg="#aaaaaa")
        self.lbl_proxima_etiqueta.pack(pady=5)

        # Botón de inicio
        self.btn_iniciar = tk.Button(main_frame, text="INICIAR PROTOCOLO", 
                                     font=("Arial", 16, "bold"), bg="#4caf50", fg="white", 
                                     activebackground="#45a049", activeforeground="white",
                                     command=self.iniciar_detener, width=20, relief="flat")
        self.btn_iniciar.pack(pady=20)

        # Barra de progreso
        self.progreso = ttk.Progressbar(main_frame, orient="horizontal", length=500, mode="determinate")
        self.progreso.pack(pady=10)
        self.progreso["maximum"] = self.duracion_total

    def hablar(self, texto):
        def _hablar():
            self.engine.say(texto)
            self.engine.runAndWait()
        threading.Thread(target=_hablar, daemon=True).start()

    def actualizar_ui(self):
        mins, secs = divmod(self.tiempo_actual, 60)
        self.lbl_tiempo.config(text=f"{mins:02d}:{secs:02d}")
        self.progreso["value"] = self.tiempo_actual

        # Determinar el intervalo actual y el próximo
        intervalo_actual = None
        proximo_intervalo = None

        for i, (t, etiqueta, desc) in enumerate(self.intervalos):
            if self.tiempo_actual >= t:
                intervalo_actual = self.intervalos[i]
                if i + 1 < len(self.intervalos):
                    proximo_intervalo = self.intervalos[i + 1]
                else:
                    proximo_intervalo = None

        # Si justo acabamos de entrar en un nuevo segundo que coincide con un inicio de intervalo
        for t, etiqueta, desc in self.intervalos:
            if self.tiempo_actual == t:
                # Reemplazar los guiones bajos por espacios para que se pronuncie mejor
                texto_hablar = etiqueta.replace("_", " ")
                self.hablar(texto_hablar)
                break

        if intervalo_actual:
            self.lbl_etiqueta_actual.config(text=f"Actual: {intervalo_actual[2]}")
        
        if proximo_intervalo:
            faltan = proximo_intervalo[0] - self.tiempo_actual
            self.lbl_proxima_etiqueta.config(text=f"Próximo: {proximo_intervalo[2]} en {faltan}s")
        else:
            self.lbl_proxima_etiqueta.config(text="Última etapa en curso")

        if self.tiempo_actual >= self.duracion_total:
            self.detener()
            self.lbl_etiqueta_actual.config(text="Protocolo finalizado.")
            self.lbl_proxima_etiqueta.config(text="")
            self.hablar("Protocolo finalizado")

    def bucle_tiempo(self):
        while self.en_ejecucion and self.tiempo_actual <= self.duracion_total:
            # Actualizar interfaz en el hilo principal
            self.root.after(0, self.actualizar_ui)
            time.sleep(1)
            if self.en_ejecucion:
                self.tiempo_actual += 1

    def iniciar_detener(self):
        if not self.en_ejecucion:
            # Iniciar
            self.en_ejecucion = True
            self.tiempo_actual = 0
            self.btn_iniciar.config(text="DETENER", bg="#f44336", activebackground="#da190b")
            self.hilo_cronometro = threading.Thread(target=self.bucle_tiempo, daemon=True)
            self.hilo_cronometro.start()
        else:
            # Detener
            self.detener()

    def detener(self):
        self.en_ejecucion = False
        self.btn_iniciar.config(text="INICIAR PROTOCOLO", bg="#4caf50", activebackground="#45a049")

if __name__ == "__main__":
    root = tk.Tk()
    app = AsistenteMonitoreoApp(root)
    root.mainloop()
