import os
import re

APPS = [
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulseDeteccionCaidas9clases\python_tools\generar_videos.py",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionTensorFlowAndKeras17\python_tools\generar_videos.py",
    r"C:\Users\HECTO\AndroidStudioProjects\AplicacionEdgeImpulse17\python_tools\generar_videos.py",
    r"C:\Users\HECTO\AndroidStudioProjects\tflite-keras-9class-app\python_tools\generar_videos.py"
]

for app in APPS:
    if os.path.exists(app):
        print(f"Fixing {app}...")
        with open(app, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix Predictions graph ticks
        content = re.sub(r"ax\.tick_params\(axis='x', rotation=\d+\).*?\n", 
                         "ax.tick_params(axis='x', rotation=90, labelsize=8, colors='#E0E0E0')\n", content)
        
        # In case the previous replace didn't hit because it lacked axis='x' or had different formatting
        # Let's be more robust:
        # 1. Ensure MultipleLocator is 1
        content = re.sub(r"ax\.xaxis\.set_major_locator\(ticker\.MultipleLocator\(.*?\)\)", 
                         "ax.xaxis.set_major_locator(ticker.MultipleLocator(1))", content)
                         
        # 2. Fix the general ax.tick_params(colors='#E0E0E0') to include rotation for x-axis in both graphs
        # We will just replace all ax.tick_params(colors='#E0E0E0') with two lines:
        content = re.sub(r"ax\.tick_params\(colors='#E0E0E0'\)", 
                         "ax.tick_params(axis='y', colors='#E0E0E0')\n    ax.tick_params(axis='x', rotation=90, labelsize=8, colors='#E0E0E0')", content)
        
        # Also fix visible_window and max_window to ensure it's not too crowded
        # Usually 15 or 10 is fine if rotation is 90
        
        with open(app, 'w', encoding='utf-8') as f:
            f.write(content)
print("Done fixing python scripts.")
