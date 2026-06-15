import os

app = r"C:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app"
m_path = os.path.join(app, "app", "src", "main", "AndroidManifest.xml")

with open(m_path, "r", encoding="utf-8") as f:
    content = f.read()

if "android.permission.POST_NOTIFICATIONS" not in content:
    content = content.replace(
        "<uses-permission android:name=\"android.permission.INTERNET\" />",
        "<uses-permission android:name=\"android.permission.INTERNET\" />\n    <uses-permission android:name=\"android.permission.POST_NOTIFICATIONS\" />"
    )
    if "android.permission.POST_NOTIFICATIONS" not in content: # fallback
        content = content.replace(
            "<uses-permission android:name=\"android.permission.INTERNET\"/>",
            "<uses-permission android:name=\"android.permission.INTERNET\"/>\n    <uses-permission android:name=\"android.permission.POST_NOTIFICATIONS\" />"
        )
    with open(m_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Manifest patched.")
else:
    print("Manifest already has POST_NOTIFICATIONS.")

for root, dirs, files in os.walk(os.path.join(app, "app", "src", "main", "java")):
    if "MainActivity.kt" in files:
        main_activity = os.path.join(root, "MainActivity.kt")
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
            print("MainActivity already has onResume.")
