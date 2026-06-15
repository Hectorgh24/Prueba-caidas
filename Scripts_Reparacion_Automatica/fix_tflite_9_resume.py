import os

app = r"C:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app"
main_activity = os.path.join(app, "app", "src", "main", "java", "com", "empresa", "aplicaciontensorflowliteandkeras", "MainActivity.kt")

with open(main_activity, "r", encoding="utf-8") as f:
    c = f.read()

if "override fun onResume()" not in c:
    injection = """
    override fun onResume() {
        super.onResume()
        try {
            androidx.core.content.ContextCompat.startForegroundService(this, android.content.Intent(this, DummyForegroundService::class.java))
        } catch (e: Exception) {
            android.util.Log.e("FGS", "Error al iniciar", e)
        }
    }
    
    """
    if "override fun onDestroy() {" in c:
        c = c.replace("override fun onDestroy() {", injection + "override fun onDestroy() {")
        with open(main_activity, "w", encoding="utf-8") as f:
            f.write(c)
        print("MainActivity patched.")
    else:
        print("Could not find onDestroy")
else:
    print("MainActivity already has onResume.")
