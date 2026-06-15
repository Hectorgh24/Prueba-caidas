import os

APPS = [
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulseDeteccionCaidas9clases",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionTensorFlowAndKeras17",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulse17",
    r"C:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app"
]

for app_path in APPS:
    try:
        # Search for MainActivity.kt
        for root, dirs, files in os.walk(os.path.join(app_path, "app", "src", "main", "java")):
            if "MainActivity.kt" in files:
                main_activity = os.path.join(root, "MainActivity.kt")
                with open(main_activity, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Remove from startMonitoring
                if "androidx.core.content.ContextCompat.startForegroundService" in content:
                    content = content.replace("androidx.core.content.ContextCompat.startForegroundService(this, android.content.Intent(this, DummyForegroundService::class.java))\n            sensorManager.registerListener(", "sensorManager.registerListener(")
                
                if "stopService(android.content.Intent(this, DummyForegroundService::class.java))" in content:
                    content = content.replace("stopService(android.content.Intent(this, DummyForegroundService::class.java))\n        sensorManager.unregisterListener(this)", "sensorManager.unregisterListener(this)")
                
                # Add to onCreate
                if "super.onCreate(savedInstanceState)" in content and "DummyForegroundService" not in content:
                    content = content.replace(
                        "super.onCreate(savedInstanceState)", 
                        "super.onCreate(savedInstanceState)\n        try { androidx.core.content.ContextCompat.startForegroundService(this, android.content.Intent(this, DummyForegroundService::class.java)) } catch (e: Exception) {}"
                    )
                
                with open(main_activity, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed MainActivity in {os.path.basename(app_path)}")
    except Exception as e:
        print(e)
