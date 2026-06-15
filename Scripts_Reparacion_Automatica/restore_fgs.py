import os
import re

APPS = [
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulseDeteccionCaidas9clases",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionTensorFlowAndKeras17",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulse17",
    r"C:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app"
]

def get_package_name(app_path):
    manifest_path = os.path.join(app_path, "app", "src", "main", "AndroidManifest.xml")
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            match = re.search(r'package="([^"]+)"', f.read())
            if match: return match.group(1)
    
    for gradle_file in ["build.gradle.kts", "build.gradle"]:
        gpath = os.path.join(app_path, "app", gradle_file)
        if os.path.exists(gpath):
            with open(gpath, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'namespace\s*=\s*"([^"]+)"', content)
                if match: return match.group(1)
                match = re.search(r"namespace\s*=\s*'([^']+)'", content)
                if match: return match.group(1)
    return None

for app in APPS:
    pkg = get_package_name(app)
    if not pkg: continue
    
    code = f"""package {pkg}

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat

class DummyForegroundService : Service() {{
    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {{
        val channelId = "monitoreo_channel_high"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
            val channel = NotificationChannel(channelId, "Monitoreo Activo", NotificationManager.IMPORTANCE_HIGH)
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }}

        val notification: Notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Monitoreo en curso")
            .setContentText("Leyendo sensores en segundo plano")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {{
            startForeground(199, notification, android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
        }} else {{
            startForeground(199, notification)
        }}
        return START_STICKY
    }}
}}
"""
    pkg_path = pkg.replace('.', os.sep)
    dest = os.path.join(app, "app", "src", "main", "java", pkg_path, "DummyForegroundService.kt")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Restored {dest}")
