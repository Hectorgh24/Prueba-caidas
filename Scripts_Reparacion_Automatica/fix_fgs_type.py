import os
import re

APPS = [
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulseDeteccionCaidas9clases",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionTensorFlowAndKeras17",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulse17",
    r"C:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app"
]

def get_package_name(app_path, manifest_path):
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'package="([^"]+)"', content)
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

for app_path in APPS:
    print(f"Fixing {os.path.basename(app_path)}...")
    manifest_path = os.path.join(app_path, "app", "src", "main", "AndroidManifest.xml")
    if not os.path.exists(manifest_path): continue
    
    pkg = get_package_name(app_path, manifest_path)
    if not pkg: continue
    
    pkg_path = pkg.replace('.', os.sep)
    src_dir = os.path.join(app_path, "app", "src", "main", "java", pkg_path)
    service_file = os.path.join(src_dir, "DummyForegroundService.kt")
    
    # 1. Update Manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        m_content = f.read()
        
    if "FOREGROUND_SERVICE_DATA_SYNC" not in m_content:
        m_content = m_content.replace('<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>', 
                                      '<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>\n    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC"/>')
    
    if 'android:foregroundServiceType="dataSync"' not in m_content:
        m_content = m_content.replace('<service android:name=".DummyForegroundService" />', 
                                      '<service android:name=".DummyForegroundService" android:foregroundServiceType="dataSync" android:exported="false" />')
        
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(m_content)
        
    # 2. Update Kotlin
    if os.path.exists(service_file):
        with open(service_file, 'r', encoding='utf-8') as f:
            s_content = f.read()
            
        if "FOREGROUND_SERVICE_TYPE_DATA_SYNC" not in s_content:
            s_content = s_content.replace("startForeground(199, notification)", 
"""        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(199, notification, android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
        } else {
            startForeground(199, notification)
        }""")
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(s_content)
    print("Done.")
