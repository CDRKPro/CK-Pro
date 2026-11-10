"""Compose les images produit à partir des rendus 3D (fond transparent) du modèle.

    python3 images_produit.py <hero.png> <low.png>   -> images/dozr_packshot.png, images/dozr_visuel.png
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
INTER = "/usr/share/fonts/opentype/inter/"
F_LOGO = os.path.join(ROOT, "fonts", "Inter-BlackItalic.otf")
YEL = (232, 172, 40)


def font(name, size):
    p = name if os.path.isabs(name) else os.path.join(INTER, name)
    return ImageFont.truetype(p, size)


def trim(im, pad=0):
    bb = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    return im.crop((bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad))


def packshot(hero, out, size=2000):
    obj = trim(hero, 10)
    s = size * 0.86 / obj.width
    obj = obj.resize((int(obj.width * s), int(obj.height * s)), Image.LANCZOS)
    bg = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    bg.alpha_composite(obj, ((size - obj.width) // 2, (size - obj.height) // 2 + 40))
    bg.convert("RGB").save(out, quality=95)


def visuel(hero, low, out, size=2000):
    W = H = size
    # fond sombre avec halo chaud derrière le produit
    bg = Image.new("RGB", (W, H), (16, 18, 22))
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).ellipse((300, 1150, 1950, 2050), fill=130)
    halo = halo.filter(ImageFilter.GaussianBlur(260))
    bg = Image.composite(Image.new("RGB", (W, H), (58, 54, 48)), bg, halo).convert("RGBA")
    d = ImageDraw.Draw(bg)

    # logo DOZR + trait jaune
    f_logo = font(F_LOGO, 300)
    d.text((110, 70), "DOZR", font=f_logo, fill=(245, 245, 245))
    lb = d.textbbox((110, 70), "DOZR", font=f_logo)
    d.text((lb[2] + 6, lb[1] - 10), "®", font=font("Inter-Bold.otf", 60), fill=(245, 245, 245))
    sw = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sw).polygon([(110, lb[3] + 26), (lb[2] + 40, lb[3] + 6), (lb[2] + 30, lb[3] + 30), (120, lb[3] + 44)],
                               fill=YEL + (255,))
    bg.alpha_composite(sw)

    # bandeau accroche
    tag = "Le doseur malin pour toutes tes poudres !"
    f_tag = font("Inter-ExtraBoldItalic.otf", 64)
    tb = d.textbbox((0, 0), tag, font=f_tag)
    x0, y0 = 110, lb[3] + 90
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.polygon([(x0 - 10, y0), (x0 + tb[2] + 70, y0 - 8), (x0 + tb[2] + 50, y0 + tb[3] + 44), (x0 - 24, y0 + tb[3] + 50)],
               fill=YEL + (255,))
    bg.alpha_composite(band)
    d.text((x0 + 28, y0 + 14), tag, font=f_tag, fill=(20, 20, 22))

    # produit
    obj = trim(hero, 6)
    s = 1440 / obj.width
    obj = obj.resize((int(obj.width * s), int(obj.height * s)), Image.LANCZOS)
    bg.alpha_composite(obj, (W - obj.width - 80, H - obj.height - 40))

    # arguments (vrais, tirés du modèle)
    feats = [("Clapet coulissant", "s'ouvre et se ferme d'une main"),
             ("Passage direct Ø14", "sans grille, la poudre tombe tout de suite"),
             ("Tube Ø20 mm", "rentre dans les bouteilles standard"),
             ("Entonnoir Ø55 mm", "pour verser sans en mettre partout")]
    f1, f2 = font("Inter-ExtraBold.otf", 50), font("Inter-Medium.otf", 36)
    y = y0 + tb[3] + 130
    for t1, t2 in feats:
        cx, cy, r = 150, y + 34, 34
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=YEL, width=6)
        d.line([(cx - 15, cy + 1), (cx - 4, cy + 13), (cx + 17, cy - 12)], fill=YEL, width=7, joint="curve")
        d.text((210, y - 2), t1, font=f1, fill=(245, 245, 245))
        d.text((210, y + 58), t2, font=f2, fill=(178, 184, 190))
        y += 150

    # médaillon détail (vue rapprochée)
    det = trim(low, 6)
    s = 640 / det.width
    det = det.resize((int(det.width * s), int(det.height * s)), Image.LANCZOS)
    D = 560
    med = Image.new("RGBA", (D, D), (34, 37, 42, 255))
    med.alpha_composite(det, ((D - det.width) // 2, (D - det.height) // 2 + 20))
    mask = Image.new("L", (D, D), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, D - 1, D - 1), fill=255)
    ring = Image.new("RGBA", (D + 24, D + 24), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, D + 23, D + 23), fill=(245, 245, 245, 255))
    mx, my = W - D - 120, 600
    bg.alpha_composite(ring, (mx - 12, my - 12))
    bg.paste(med, (mx, my), mask)
    bg.convert("RGB").save(out, quality=95)


def gamme(heroes, out, W=2400, H=2400):
    """Les coloris en grille 2 × 2 sur fond blanc, chacun avec son nom."""
    bg = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(bg)
    d.text((W // 2, 150), "DOZR", font=font(F_LOGO, 190), fill=(24, 24, 26), anchor="mm")
    d.text((W // 2, 300), f"Disponible en {len(heroes)} coloris", font=font("Inter-Medium.otf", 64),
           fill=(110, 116, 122), anchor="mm")
    top, cols = 400, 2
    rows = (len(heroes) + cols - 1) // cols
    cw, ch = W / cols, (H - top - 40) / rows
    for k, (name, im) in enumerate(heroes):
        r, c = divmod(k, cols)
        obj = trim(im, 6)
        s = min(cw * 0.86 / obj.width, (ch - 170) / obj.height)
        obj = obj.resize((int(obj.width * s), int(obj.height * s)), Image.LANCZOS)
        cx, cy = int(cw * (c + 0.5)), int(top + ch * r)
        bg.alpha_composite(obj, (cx - obj.width // 2, cy + int((ch - 150 - obj.height) / 2)))
        d.text((cx, cy + ch - 90), name, font=font("Inter-Bold.otf", 70), fill=(24, 24, 26), anchor="mm")
    bg.convert("RGB").save(out, quality=95)


if __name__ == "__main__":
    # python3 images_produit.py hero.png low.png [suffixe]
    hero = Image.open(sys.argv[1]).convert("RGBA")
    low = Image.open(sys.argv[2]).convert("RGBA")
    suf = ("_" + sys.argv[3]) if len(sys.argv) > 3 else ""
    os.makedirs(os.path.join(ROOT, "images"), exist_ok=True)
    packshot(hero, os.path.join(ROOT, "images", f"dozr_packshot{suf}.png"))
    visuel(hero, low, os.path.join(ROOT, "images", f"dozr_visuel{suf}.png"))
    o = trim(hero, 20)
    o.save(os.path.join(ROOT, "images", f"dozr_detoure{suf}.png"))
    print(f"images/dozr_*{suf}.png")
