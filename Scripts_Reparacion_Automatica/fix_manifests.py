import os

APPS = [
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulseDeteccionCaidas9clases",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionTensorFlowAndKeras17",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulse17",
    r"C:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app"
]

for app in APPS:
    m_path = os.path.join(app, "app", "src", "main", "AndroidManifest.xml")
    if os.path.exists(m_path):
        with open(m_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "FOREGROUND_SERVICE_DATA_SYNC" not in content:
            if "<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE\" />" in content:
                content = content.replace(
                    "<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE\" />",
                    "<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE\" />\n    <uses-permission android:name=\"android.permission.FOREGROUND_SERVICE_DATA_SYNC\" />"
                )
            elif "<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE\"/>" in content:
                content = content.replace(
                    "<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE\"/>",
                    "<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE\"/>\n    <uses-permission android:name=\"android.permission.FOREGROUND_SERVICE_DATA_SYNC\" />"
                )
        
        with open(m_path, "w", encoding="utf-8") as f:
            f.write(content)

print("Manifests fixed.")
