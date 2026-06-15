import os
import re

APPS = [
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulseDeteccionCaidas9clases",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionTensorFlowAndKeras17",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulse17",
    r"C:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app"
]

def update_manifest(app_path):
    manifest_path = os.path.join(app_path, "app", "src", "main", "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        return
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Change FOREGROUND_SERVICE_DATA_SYNC to FOREGROUND_SERVICE_HEALTH
    content = content.replace("FOREGROUND_SERVICE_DATA_SYNC", "FOREGROUND_SERVICE_HEALTH")
    
    # Check if DATA_SYNC was missing but HEALTH is not there
    if "FOREGROUND_SERVICE_HEALTH" not in content:
        content = content.replace('<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>',
                                  '<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>\n    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_HEALTH"/>')

    # Change foregroundServiceType="dataSync" to "health"
    content = content.replace('android:foregroundServiceType="dataSync"', 'android:foregroundServiceType="health"')
    
    if 'android:foregroundServiceType="health"' not in content:
        content = content.replace('<service android:name=".DummyForegroundService" />', 
                                  '<service android:name=".DummyForegroundService" android:foregroundServiceType="health" android:exported="false" />')
        
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_service(app_path):
    for root, dirs, files in os.walk(os.path.join(app_path, "app", "src", "main", "java")):
        for f in files:
            if f == "DummyForegroundService.kt" or f == "DummyForegroundService.java":
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                content = content.replace("FOREGROUND_SERVICE_TYPE_DATA_SYNC", "FOREGROUND_SERVICE_TYPE_HEALTH")
                content = content.replace("FOREGROUND_SERVICE_TYPE_SPECIAL_USE", "FOREGROUND_SERVICE_TYPE_HEALTH")
                
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)

def update_activity(app_path):
    for root, dirs, files in os.walk(os.path.join(app_path, "app", "src", "main", "java")):
        for f in files:
            if f == "MainActivity.kt" or f == "MainActivity.java":
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Replace getSystemService(Context.SENSOR_SERVICE) with applicationContext.getSystemService(Context.SENSOR_SERVICE)
                # But handle already replaced ones just in case
                content = re.sub(r'(?<!applicationContext\.)getSystemService\(Context\.SENSOR_SERVICE\)', 'applicationContext.getSystemService(Context.SENSOR_SERVICE)', content)
                
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)

for app in APPS:
    print(f"Fixing {app}...")
    update_manifest(app)
    update_service(app)
    update_activity(app)
print("Fix applied successfully.")
