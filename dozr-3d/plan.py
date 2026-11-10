"""
Plan coté du Dozr (A3 paysage, échelle 1:1) + GLB allégé pour la vue 3D web.

    python3 plan.py   -> plan.pdf, plan.svg, plan.png, web/dozr_web.glb

Toutes les géométries viennent de dozr.py : le plan suit le modèle.
"""
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle, FancyBboxPatch
import trimesh

import dozr as d

ROOT = os.path.dirname(os.path.abspath(__file__))
INK, THIN, HATCH = "#1d232b", 0.25, "#1d232b"
DIM = "#2a5d8f"


# ----------------------------------------------------------------- outils de dessin
def polys(cs):
    return [np.asarray(p) for p in cs.to_polygons() if len(p) > 2]


def draw_cs(ax, cs, ox, oy, fill=None, hatch=None, lw=0.35, color=INK, z=2):
    for p in polys(cs):
        ax.add_patch(Polygon(p + (ox, oy), closed=True, fill=fill is not None, fc=fill or "none",
                             ec=color, lw=lw, hatch=hatch, zorder=z))


def dim_h(ax, x1, x2, y, yref1, yref2, txt, above=True):
    """Cote horizontale entre x1 et x2 placée à la hauteur y (lignes d'attache depuis yref)."""
    for x, yr in ((x1, yref1), (x2, yref2)):
        ax.plot([x, x], [yr, y + (1.2 if y > yr else -1.2)], color=DIM, lw=0.2)
    ax.annotate("", (x1, y), (x2, y), arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.3,
                                                       mutation_scale=4, shrinkA=0, shrinkB=0))
    ax.text((x1 + x2) / 2, y + (0.9 if above else -0.9), txt, ha="center", va="bottom" if above else "top",
            fontsize=6.5, color=DIM)


def dim_v(ax, y1, y2, x, xref1, xref2, txt, right=True):
    for y, xr in ((y1, xref1), (y2, xref2)):
        ax.plot([xr, x + (1.2 if x > xr else -1.2)], [y, y], color=DIM, lw=0.2)
    ax.annotate("", (x, y1), (x, y2), arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.3,
                                                       mutation_scale=4, shrinkA=0, shrinkB=0))
    ax.text(x + (0.9 if right else -0.9), (y1 + y2) / 2, txt, ha="left" if right else "right", va="center",
            fontsize=6.5, color=DIM, rotation=90 if False else 0)


def leader(ax, xy, xytext, txt):
    ax.annotate(txt, xy, xytext, fontsize=6.5, color=DIM, ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", color=DIM, lw=0.3, mutation_scale=4, shrinkA=0, shrinkB=0.5))


def title(ax, x, y, txt, sub=None):
    ax.text(x, y, txt, fontsize=9, weight="bold", color=INK, ha="left", va="bottom")
    if sub:
        ax.text(x, y - 0.6, sub, fontsize=6, color="#5b6570", ha="left", va="top")


def axis_line(ax, x1, y1, x2, y2):
    ax.plot([x1, x2], [y1, y2], color="#8a939c", lw=0.2, dashes=(6, 1.5, 1, 1.5), zorder=1)


# ----------------------------------------------------------------- vues
def main():
    bd, cv = d.body(), d.cover()
    cl_f, cl_o = d.clapet(False), d.clapet(True)
    whole = bd + cv + cl_f
    X0 = -d.CUP_R_TOP                       # bord gauche de l'objet (bord de l'entonnoir)

    fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((10, 10), 400, 277, fill=False, ec=INK, lw=0.7))

    # ---- 1. Vue de dessus (x -> droite, y -> haut)
    ox, oy = 40 - X0, 228
    draw_cs(ax, whole.project(), ox, oy, lw=0.5)
    rim_in = d.r_out(d.CUP_H) - d.WALL
    ax.add_patch(Circle((ox, oy), rim_in, fill=False, ec=INK, lw=0.3))
    ax.add_patch(Circle((ox, oy), d.BORE_D / 2, fill=False, ec=INK, lw=0.3))
    for r in (rim_in - 4, rim_in - 9):
        ax.add_patch(Circle((ox, oy), r, fill=False, ec="#9aa3ab", lw=0.15, ls=(0, (2, 1.5))))
    L = d.PILL_X1 - d.PILL_X0
    draw_cs(ax, d.rrect(d.PILL_X0, d.PILL_X1, d.PILL_W, d.PILL_W / 2), ox, oy, lw=0.35)
    ax.add_patch(Circle((ox + d.KNOB_X, oy), d.KNOB_D / 2, fc="#2b2f35", ec=INK, lw=0.35, zorder=3))
    ax.add_patch(Circle((ox + d.KNOB_X, oy), d.KNOB_DISC_D / 2, fill=False, ec="#9aa3ab", lw=0.3, zorder=4))
    ax.add_patch(Circle((ox + d.HANG_X, oy), d.HANG_D / 2, fill=False, ec=INK, lw=0.35))
    ax.add_patch(Circle((ox + d.HANG_X, oy), d.HANG_CSK / 2, fill=False, ec=INK, lw=0.25))
    draw_cs(ax, d.logo().slice(d.HANDLE_T - 0.3), ox, oy, fill="#c9cfd5", lw=0.2)
    axis_line(ax, ox + X0 - 6, oy, ox + d.HANDLE_END + 6, oy)
    axis_line(ax, ox, oy - 34, ox, oy + 34)
    title(ax, 22, 270, "VUE DE DESSUS", "clapet fermé")
    dim_h(ax, ox + X0, ox + d.HANDLE_END, oy + 38, oy, oy + d.HANDLE_W / 2, f"{d.HANDLE_END - X0:.1f}")
    dim_v(ax, oy - d.CUP_R_TOP, oy + d.CUP_R_TOP, ox + X0 - 8, ox, ox, f"Ø{2 * d.CUP_R_TOP:.0f}", right=False)
    dim_v(ax, oy - d.HANDLE_W / 2, oy + d.HANDLE_W / 2, ox + d.HANDLE_END + 8, ox + d.HANDLE_END,
          ox + d.HANDLE_END, f"{d.HANDLE_W:.0f}")
    dim_h(ax, ox, ox + d.PILL_X0, oy - 24, oy, oy - d.PILL_W / 2, f"{d.PILL_X0:.1f}", above=False)
    dim_h(ax, ox + d.PILL_X0, ox + d.PILL_X1, oy - 24, oy - d.PILL_W / 2, oy - d.PILL_W / 2, f"{L:.0f}", above=False)
    dim_h(ax, ox + d.PILL_X1, ox + d.HANG_X, oy - 24, oy - d.PILL_W / 2, oy, f"{d.HANG_X - d.PILL_X1:.0f}", above=False)
    leader(ax, (ox + d.HANG_X + 2, oy + 2), (ox + d.HANG_X + 12, oy + 24), f"Ø{d.HANG_D:.0f} chanfr. Ø{d.HANG_CSK}")
    leader(ax, (ox + d.KNOB_X + 5, oy + 6), (ox + d.KNOB_X + 2, oy + 24), f"bouton Ø{d.KNOB_D}")
    leader(ax, (ox + d.PILL_X0 + 30, oy + d.PILL_W / 2), (ox + d.PILL_X0 + 22, oy + 30), f"fenêtre {d.PILL_W} × {L:.0f}")
    leader(ax, (ox + d.LOGO_X, oy + 2.5), (ox + d.LOGO_X + 4, oy + 30), "logo gravé 0,8")

    # ---- 2. Vue de côté (x -> droite, z -> haut)
    ox2, oy2 = ox, 140
    side = whole.rotate((-90, 0, 0))
    draw_cs(ax, side.project(), ox2, oy2, lw=0.5)
    ax.plot([ox2 + 18, ox2 + d.HANDLE_END - 1], [oy2 + d.HANDLE_T, oy2 + d.HANDLE_T], color=INK, lw=0.2)
    axis_line(ax, ox2, oy2 - d.SPOUT_L - 5, ox2, oy2 + d.CUP_H + 5)
    title(ax, 22, 186, "VUE DE CÔTÉ")
    zmin, zmax = -d.SPOUT_L, d.CUP_H
    dim_v(ax, oy2 + zmin, oy2 + zmax, ox2 + X0 - 8, ox2 - d.SPOUT_OD / 2, ox2 + X0, f"{zmax - zmin:.0f}", right=False)
    dim_v(ax, oy2, oy2 + zmax, ox2 + X0 - 18, ox2 + X0, ox2 + X0, f"{d.CUP_H:.0f}", right=False)
    dim_v(ax, oy2 + zmin, oy2, ox2 + 18, ox2 + d.SPOUT_OD / 2, ox2 + 14, f"{d.SPOUT_L:.0f}")
    dim_v(ax, oy2, oy2 + d.HANDLE_T, ox2 + d.HANDLE_END + 8, ox2 + d.HANDLE_END, ox2 + d.HANDLE_END, f"{d.HANDLE_T:.0f}")
    ktop = d.BOSS_TOP + d.KNOB_H + 0.6
    dim_v(ax, oy2 + d.HANDLE_T, oy2 + ktop, ox2 + d.KNOB_X + 14, ox2 + d.KNOB_X, ox2 + d.KNOB_X,
          f"{ktop - d.HANDLE_T:.1f}")
    dim_h(ax, ox2 - d.SPOUT_OD / 2, ox2 + d.SPOUT_OD / 2, oy2 + zmin - 7, oy2 + zmin, oy2 + zmin,
          f"Ø{d.SPOUT_OD:.0f}", above=False)

    # ---- 3. Coupes A-A : fermé / ouvert
    def section(oxs, oys, cl, label, sub):
        for m, fc, h in [(bd, "#e3e7ea", "////"), (cv, "#eef0f2", "\\\\\\\\"), (cl, "#30353c", None)]:
            draw_cs(ax, m.rotate((-90, 0, 0)).slice(0.0), oxs, oys, fill=fc, hatch=h, lw=0.35, z=2)
        axis_line(ax, oxs, oys - d.SPOUT_L - 5, oxs, oys + d.CUP_H + 5)
        title(ax, oxs + X0, oys + d.CUP_H + 8, label, sub)

    plt.rcParams["hatch.linewidth"] = 0.15
    sx, sy = 236 - X0, 222
    section(sx, sy, cl_f, "COUPE A-A — CLAPET FERMÉ", "bouton côté entonnoir : la languette bouche le tube")
    dim_h(ax, sx - d.BORE_D / 2, sx + d.BORE_D / 2, sy - d.SPOUT_L - 6, sy - d.SPOUT_L, sy - d.SPOUT_L,
          f"Ø{d.BORE_D:.0f} passage", above=False)
    leader(ax, (sx + 14, sy + d.FUNNEL_Z0 + 8.5), (sx + 30, sy + 30), f"fond conique {d.FUNNEL_ANGLE:.0f}°")
    leader(ax, (sx - 3, sy + d.Z_CHAN + 1), (sx - 52, sy - 8), "languette (clapet)")
    leader(ax, (sx + d.r_out(20) - 0.5, sy + 20), (sx + 34, sy + 18), f"paroi {d.WALL}")

    sx2, sy2 = sx, 140
    section(sx2, sy2, cl_o, "COUPE A-A — CLAPET OUVERT", "bouton tiré vers le bout du manche : passage libre")
    dim_h(ax, sx2 + d.KNOB_X, sx2 + d.KNOB_X + d.TRAVEL, sy2 + 22, sy2 + 14, sy2 + 14, f"course {d.TRAVEL:.0f}")
    ax.annotate("", (sx2, sy2 - d.SPOUT_L - 4), (sx2, sy2 + 22),
                arrowprops=dict(arrowstyle="-|>", color="#c2861a", lw=0.8, mutation_scale=7))
    ax.text(sx2 + 2, sy2 + 24, "poudre", fontsize=6.5, color="#c2861a")

    # ---- 4. Vue 3D + nomenclature + cartouche
    img = os.path.join(ROOT, "apercu.png")
    if os.path.exists(img):
        im = plt.imread(img)
        h = 92
        w = h * im.shape[1] / im.shape[0]
        ax.imshow(im, extent=(18, 18 + w, 18, 18 + h), zorder=1)
        ax.text(18, 18 + h + 2, "VUES 3D", fontsize=9, weight="bold", color=INK)

    bx, by = 262, 18
    rows = [("Rep.", "Pièce", "Couleur", "Qté"),
            ("1", "Corps : entonnoir + manche", "gris", "1"),
            ("2", "Couvercle + tube Ø20", "gris", "1"),
            ("3", "Clapet complet (languette + bouton)", "noir", "1")]
    cw = [12, 82, 22, 12]
    for i, row in enumerate(rows):
        y = by + 70 - i * 7
        x = bx
        for j, (c, w) in enumerate(zip(row, cw)):
            ax.add_patch(Rectangle((x, y), w, 7, fill=i == 0, fc="#e9edf0", ec=INK, lw=0.3))
            ax.text(x + 1.5, y + 3.5, c, fontsize=6.5, va="center", weight="bold" if i == 0 else "normal", color=INK)
            x += w
    cart = [("DOZR", "Doseur à poudre — plan d'ensemble", 13),
            ("Échelle", "1:1 (A3)", 7), ("Unités", "mm", 7), ("Matière", "PETG alimentaire ou PLA", 7),
            ("Tolérance", "jeu de coulissement 0,3 / côté", 7), ("Date", "10/11/2026", 7)]
    y = by + 36
    for k, v, fs in cart:
        hgt = 10 if fs > 10 else 6
        ax.add_patch(Rectangle((bx, y - hgt), 128, hgt, fill=False, ec=INK, lw=0.3))
        if fs > 10:
            ax.text(bx + 3, y - hgt / 2, k, fontsize=fs, weight="bold", va="center", color=INK, style="italic")
            ax.text(bx + 30, y - hgt / 2, v, fontsize=7, va="center", color=INK)
        else:
            ax.text(bx + 3, y - hgt / 2, k, fontsize=6, va="center", color="#5b6570")
            ax.text(bx + 30, y - hgt / 2, v, fontsize=6.5, va="center", color=INK)
        y -= hgt

    for ext in ("pdf", "svg", "png"):
        fig.savefig(os.path.join(ROOT, f"plan.{ext}"), dpi=200 if ext == "png" else None, facecolor="white")
    print("plan.pdf / plan.svg / plan.png")

    # ---- GLB web : normales lissées, matériaux, nœuds séparés pour l'animation
    os.makedirs(os.path.join(ROOT, "web"), exist_ok=True)
    sc = trimesh.Scene()
    for name, m, rgba, rough in [("corps", bd, [0.17, 0.18, 0.2, 1], 0.5),
                                 ("couvercle", cv, [0.17, 0.18, 0.2, 1], 0.5),
                                 ("clapet", cl_f, [0.012, 0.012, 0.014, 1], 0.38)]:
        t = d.to_tm(m)
        t = t.smooth_shaded
        t.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=rgba, metallicFactor=0.0, roughnessFactor=rough))
        sc.add_geometry(t, node_name=name, geom_name=name)
    # glTF JSON à tampons intégrés (.json : type servi par l'hébergement des pages)
    from trimesh.exchange.gltf import export_gltf
    files = export_gltf(sc, embed_buffers=True)
    data = files["model.gltf"]
    out = os.path.join(ROOT, "web", "dozr_web.json")
    with open(out, "wb") as f:
        f.write(data)
    print("web/dozr_web.json", round(os.path.getsize(out) / 1e6, 1), "Mo")


if __name__ == "__main__":
    main()
