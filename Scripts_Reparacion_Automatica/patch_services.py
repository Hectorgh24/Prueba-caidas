import os
import re

APPS = [
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulseDeteccionCaidas9clases",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionTensorFlowAndKeras17",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulse17",
    r"C:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app"
]

def get_package_name(app_path, manifest_path):
    # Try AndroidManifest first
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'package="([^"]+)"', content)
        if match: return match.group(1)
        
    # Try build.gradle / build.gradle.kts
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

def patch_app(app_path):
    print(f"Patching {os.path.basename(app_path)}...")
    manifest_path = os.path.join(app_path, "app", "src", "main", "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        print(f"  Manifest not found at {manifest_path}")
        return

    pkg = get_package_name(app_path, manifest_path)
    if not pkg:
        print("  Could not parse package name")
        return

    pkg_path = pkg.replace('.', os.sep)
    src_dir = os.path.join(app_path, "app", "src", "main", "java", pkg_path)
    
    # 1. Create DummyForegroundService.kt
    service_content = f"""package {pkg}

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
        val channelId = "monitoreo_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
            val channel = NotificationChannel(channelId, "Monitoreo Activo", NotificationManager.IMPORTANCE_LOW)
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }}

        val notification: Notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Monitoreo en curso")
            .setContentText("Leyendo sensores en segundo plano")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build()

        startForeground(199, notification)
        return START_STICKY
    }}
}}
"""
    service_file = os.path.join(src_dir, "DummyForegroundService.kt")
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(service_content)
    print("  Created DummyForegroundService.kt")

    # 2. Patch Manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest_content = f.read()

    if "FOREGROUND_SERVICE" not in manifest_content:
        manifest_content = manifest_content.replace("<application", '<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>\n    <application')

    if ".DummyForegroundService" not in manifest_content:
        manifest_content = manifest_content.replace("</application>", '    <service android:name=".DummyForegroundService" />\n    </application>')

    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    print("  Patched AndroidManifest.xml")

    # 3. Patch MainActivity.kt
    main_activity = os.path.join(src_dir, "MainActivity.kt")
    if os.path.exists(main_activity):
        with open(main_activity, 'r', encoding='utf-8') as f:
            main_content = f.read()
            
        # Add to startMonitoring
        if "DummyForegroundService" not in main_content:
            if "sensorManager.registerListener(" in main_content:
                main_content = main_content.replace(
                    "sensorManager.registerListener(",
                    "androidx.core.content.ContextCompat.startForegroundService(this, android.content.Intent(this, DummyForegroundService::class.java))\n            sensorManager.registerListener("
                )
            # Add to stopMonitoring
            if "sensorManager.unregisterListener(this)" in main_content:
                main_content = main_content.replace(
                    "sensorManager.unregisterListener(this)",
                    "stopService(android.content.Intent(this, DummyForegroundService::class.java))\n        sensorManager.unregisterListener(this)"
                )
            with open(main_activity, 'w', encoding='utf-8') as f:
                f.write(main_content)
            print("  Patched MainActivity.kt")
        else:
            print("  MainActivity already patched")
    else:
        print("  MainActivity.kt not found")

for app in APPS:
    try:
        patch_app(app)
    except Exception as e:
        print(f"Error patching {app}: {e}")
