import os

files = [
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulseDeteccionCaidas9clases\app\src\main\java\com\empresa\aplicacionedgeimpulse\MainActivity.kt",
    r"C:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app\app\src\main\java\com\empresa\aplicaciontensorflowliteandkeras\MainActivity.kt"
]

import_code = """
import android.util.Log
import java.net.DatagramPacket
import java.net.DatagramSocket
import kotlin.concurrent.thread
"""

listener_code = """
    private fun startUdpListener() {
        thread(isDaemon = true) {
            try {
                val socket = DatagramSocket(50000)
                socket.broadcast = true
                val buffer = ByteArray(256)
                while (true) {
                    val packet = DatagramPacket(buffer, buffer.size)
                    socket.receive(packet)
                    val message = String(packet.data, 0, packet.length).trim()
                    Log.d("UDP_LISTENER", "Recibido: $message")
                    
                    if (message == "START_MONITORING") {
                        if (!MonitoringState.isMonitoring.value) {
                            val serviceIntent = Intent(this, FallDetectionService::class.java)
                            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                                startForegroundService(serviceIntent)
                            } else {
                                startService(serviceIntent)
                            }
                        }
                    } else if (message == "STOP_MONITORING") {
                        if (MonitoringState.isMonitoring.value) {
                            val serviceIntent = Intent(this, FallDetectionService::class.java)
                            stopService(serviceIntent)
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e("UDP_LISTENER", "Error: ${e.message}")
            }
        }
    }
"""

for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if "DatagramSocket" not in content:
            content = content.replace("\nimport ", import_code + "\nimport ", 1)
            content = content.replace("super.onCreate(savedInstanceState)", "super.onCreate(savedInstanceState)\n        startUdpListener()")
            last_brace_index = content.rfind("}")
            content = content[:last_brace_index] + listener_code + content[last_brace_index:]
            
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Modificado {f}")
        else:
            print(f"Ya modificado {f}")
            
        # Manifest
        manifest_path = f.replace(r"java\com\empresa", "AndroidManifest.xml").split(r"\AndroidManifest.xml")[0] + r"\AndroidManifest.xml"
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as mfile:
                mcontent = mfile.read()
            if "android.permission.INTERNET" not in mcontent:
                mcontent = mcontent.replace("<application", '<uses-permission android:name="android.permission.INTERNET" />\n    <application')
                with open(manifest_path, 'w', encoding='utf-8') as mfile:
                    mfile.write(mcontent)
                print(f"Permiso INTERNET agregado en {manifest_path}")
    except Exception as e:
        print(f"Error procesando {f}: {e}")
