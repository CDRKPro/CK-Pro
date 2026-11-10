"""Assemble index.html (page unique) : page_source.html + aperçu + modèle 3D intégrés.

    python3 construire.py      (après avoir régénéré ../web/dozr_web.json avec ../plan.py si le modèle change)
"""
import base64, io, os
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(ICI, "page_source.html"), encoding="utf-8").read()
img = Image.open(os.path.join(ICI, "..", "images", "dozr_detoure.png")).convert("RGBA")
img = img.resize((760, int(img.height * 760 / img.width)), Image.LANCZOS)
b = io.BytesIO(); img.save(b, "WEBP", quality=82, method=6)
modele = open(os.path.join(ICI, "..", "web", "dozr_web.json"), encoding="utf-8").read()
assert "</script" not in modele
page = src.replace("__APERCU__", base64.b64encode(b.getvalue()).decode()).replace("__MODELE__", modele)
open(os.path.join(ICI, "index.html"), "w", encoding="utf-8").write(page)
print("index.html", round(len(page.encode()) / 1e6, 2), "Mo")
