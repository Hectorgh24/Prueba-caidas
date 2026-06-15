import os

app = r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulseDeteccionCaidas9clases"
m_path = os.path.join(app, "app", "src", "main", "AndroidManifest.xml")

with open(m_path, "r", encoding="utf-8") as f:
    content = f.read()

if "android.permission.POST_NOTIFICATIONS" not in content:
    content = content.replace(
        "<uses-permission android:name=\"android.permission.INTERNET\" />",
        "<uses-permission android:name=\"android.permission.INTERNET\" />\n    <uses-permission android:name=\"android.permission.POST_NOTIFICATIONS\" />"
    )

with open(m_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Permission added.")
