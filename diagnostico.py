"""
Diagnóstico: ejecutar desde la carpeta del proyecto (donde está manage.py),
con el venv activo:
    python diagnostico.py
Descarga la API real del CMA y muestra qué colección detecta tu detector.
"""
import sys, os, json, urllib.request

# Ajusta esta ruta si tu paquete WebBuilder está en otro sitio:
sys.path.insert(0, "WebBuilder")

from utils.analysis.detection import find_main_items, _path_penalty

print("Penalización anidados (debe ser >=9):", _path_penalty(["data", 0, "citations"]))
print("-" * 50)

url = "https://openaccess-api.clevelandart.org/api/artworks/?limit=15&has_image=1&cc0=1"
print("Descargando:", url)
data = json.load(urllib.request.urlopen(url, timeout=30))

res = find_main_items(data)
print("PATH detectado :", res["path"])
print("Nº items       :", res["count"])
print("Keys (primeras):", res["sample_keys"][:8])
print("-" * 50)
if res["path"] == ["data"] and "title" in res["sample_keys"]:
    print("✅ DETECCIÓN CORRECTA — el problema está en el planner LLM, no en el detector.")
else:
    print("❌ DETECCIÓN INCORRECTA — el detector elige el array equivocado.")
    print("   Path:", res["path"])
