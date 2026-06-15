import os

app = r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulseDeteccionCaidas9clases"
m_path = os.path.join(app, "app", "src", "main", "java", "com", "empresa", "aplicacionedgeimpulse", "MainActivity.kt")

with open(m_path, "r", encoding="utf-8") as f:
    content = f.read()

if "override fun onResume()" not in content:
    # Inject before override fun onDestroy()
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
    content = content.replace("override fun onDestroy() {", injection + "override fun onDestroy() {")
    with open(m_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Injected onResume.")
