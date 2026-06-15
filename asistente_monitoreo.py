import tkinter as tk
from tkinter import ttk
# pyrefly: ignore [missing-import]
from gtts import gTTS
import pygame
import threading
import time
import queue
import tempfile
import os
import socket
import urllib.request

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

        # Configurar socket UDP para envío de broadcast por red local Wi-Fi
        self.puerto_udp = 50000
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Configurar hilo dedicado para motor de voz
        self.cola_voz = queue.Queue()
        self.hilo_voz = threading.Thread(target=self._bucle_voz, daemon=True)
        self.hilo_voz.start()

        # Tabla de intervalos: (tiempo_inicio, etiqueta_hablada, descripcion_ui)
        self.intervalos = [
            (0, "De pie", "Preparación y calibración (standing_up)"),
            (10, "Caminando", "Caminata de rutina (walk)"),
            (20, "Corriendo", "Actividad de impacto (running)"),
            (30, "Sentado", "Transición postural (sitting_down)"),
            (45, "Caída lateral izquierda", "Primera simulación de caída (fall_sideward_left)"),
            (55, "Caminando", "Caminata de recuperación (walk)"),
            (65, "Caída hacia atrás", "Segunda simulación de caída (fall_backward)"),
            (75, "Caminando", "Caminata previa al evento crítico (walk)"),
            (85, "Caída hacia adelante", "Tercera simulación de caída (fall_forward)"),
            (90, "Acostado", "Periodo post-caída (lying_down)"),
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

        # Configuración de IPs
        frame_ips = tk.Frame(main_frame, bg="#2b2b2b")
        frame_ips.pack(pady=5)
        
        lbl_ip_redmi = tk.Label(frame_ips, text="IP Redmi 13C (Cámara):", font=("Arial", 10), bg="#2b2b2b", fg="#ffffff")
        lbl_ip_redmi.grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.entry_ip = tk.Entry(frame_ips, width=18, font=("Arial", 10))
        self.entry_ip.insert(0, "192.168.1.100:8080")
        self.entry_ip.grid(row=0, column=1, padx=5, pady=2)



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

    def _bucle_voz(self):
        pygame.mixer.init()
        
        # Crear directorio caché para modo offline
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voz_cache")
        if not os.path.exists(cache_dir):
            try:
                os.makedirs(cache_dir)
            except:
                pass
                
        while True:
            texto = self.cola_voz.get()
            if texto is None:
                break
            try:
                # Limpiar texto para nombre de archivo
                safe_texto = "".join(c for c in texto if c.isalnum() or c == " ").strip().replace(" ", "_").lower()
                cache_path = os.path.join(cache_dir, f"{safe_texto}.mp3")
                
                # Generar solo si no existe o si está vacío por un error previo
                if not os.path.exists(cache_path) or os.path.getsize(cache_path) == 0:
                    from gtts import gTTS
                    tts = gTTS(text=texto, lang='es', tld='com.mx')
                    tts.save(cache_path)
                
                pygame.mixer.music.load(cache_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    import time
                    time.sleep(0.1)
                
                pygame.mixer.music.unload()

            except Exception as e:
                print(f"Error TTS (Quizás sin internet y sin caché): {e}")
            
            self.cola_voz.task_done()



    def hablar(self, texto):
        self.cola_voz.put(texto)

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
                self.hablar(etiqueta)
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
            if getattr(self, 'en_cuenta_regresiva', False):
                return # Ignorar clics mientras cuenta atrás
            
            self.en_cuenta_regresiva = True
            self.btn_iniciar.config(text="Preparando...", state=tk.DISABLED, bg="#aaaaaa")
            
            def _countdown():
                for i in range(5, 0, -1):
                    if not self.en_cuenta_regresiva: return # Cancelado
                    self.lbl_tiempo.config(text=f"- 00:0{i}")
                    self.lbl_etiqueta_actual.config(text=f"Prepárate, iniciando en {i}...")
                    self.hablar(str(i))
                    time.sleep(1)
                
                # Termina cuenta regresiva, arrancar todo sincronizado
                self.en_cuenta_regresiva = False
                self.en_ejecucion = True
                self.tiempo_actual = 0
                
                def _start_everything():
                    self.btn_iniciar.config(text="DETENER", state=tk.NORMAL, bg="#f44336", activebackground="#da190b")
                    
                    # UDP BROADCASTS REMOVED - Android apps now handle start manually.
                        
                    # Iniciar cámara
                    ip = self.entry_ip.get().strip()
                    if ip:
                        def start_cam():
                            try:
                                url = f"http://{ip}/startvideo?force=1"
                                req = urllib.request.Request(url, data=b"") # POST request
                                urllib.request.urlopen(req, timeout=3)
                                print(f"Cámara IP iniciada: {url}")
                            except Exception as e:
                                print(f"Error al iniciar cámara IP: {e}")
                        threading.Thread(target=start_cam, daemon=True).start()

                    # Iniciar reloj interno
                    self.hilo_cronometro = threading.Thread(target=self.bucle_tiempo, daemon=True)
                    self.hilo_cronometro.start()
                
                # Ejecutar en hilo principal para evitar bugs de tkinter
                self.root.after(0, _start_everything)

            threading.Thread(target=_countdown, daemon=True).start()
        else:
            # Detener
            self.en_cuenta_regresiva = False
            self.detener()

    def detener(self):
        self.en_ejecucion = False
        self.btn_iniciar.config(text="INICIAR PROTOCOLO", bg="#4caf50", activebackground="#45a049")
        
        # UDP BROADCASTS REMOVED - Android apps now handle stop automatically after 120s.

        # Detener cámara IP Webcam
        ip = self.entry_ip.get().strip()
        if ip:
            def stop_cam():
                try:
                    url = f"http://{ip}/stopvideo?force=1"
                    req = urllib.request.Request(url, data=b"") # POST request
                    urllib.request.urlopen(req, timeout=3)
                    print(f"Cámara IP detenida: {url}")
                except Exception as e:
                    print(f"Error al detener cámara IP: {e}")
            threading.Thread(target=stop_cam, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AsistenteMonitoreoApp(root)
    root.mainloop()
