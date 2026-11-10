"""
Dozr — doseur à poudre avec entonnoir, tamis et trappe coulissante.
Modèle paramétrique imprimable en 3D (5 pièces).

    pip install manifold3d trimesh numpy
    python3 dozr.py            -> génère les STL + l'assemblage (3MF / GLB)

Unités : millimètres. Repère : centre de l'entonnoir à l'origine,
manche selon +X, Z vers le haut (position d'utilisation, bec vers le bas).

Principe :
  - Corps inférieur : semelle + bec qui s'emboîte dans le goulot,
    creusé d'un canal où glisse la trappe.
  - Corps supérieur : entonnoir cannelé + dessus du manche avec la fenêtre
    du bouton. Collé sur le corps inférieur (4 tiges d'alignement Ø2).
  - Trappe : plaque coulissante percée ; bouton vers l'avant = ouvert,
    bouton vers l'arrière = fermé.
  - Bouton : capuchon emmanché sur la tige de la trappe.
  - Tamis : grille posée sur un épaulement au fond de l'entonnoir.
"""
import math
import os

import numpy as np
from manifold3d import CrossSection, Manifold, JoinType
import trimesh

SEG = 128  # finesse des cercles

# ---------------------------------------------------------------- paramètres
CLR = 0.3            # jeu de coulissement (par côté)

# Empilement en Z
BASE_T = 2.0         # fond du corps inférieur
CHAN_H = 2.4         # hauteur du canal de la trappe
TOP_T = 3.5          # épaisseur du dessus du manche
Z_CHAN = BASE_T                  # 2.0
Z_SPLIT = BASE_T + CHAN_H        # 4.4 : plan de joint entre les 2 corps
Z_TOP = Z_SPLIT + TOP_T          # 7.9

# Contour
DISC_R = 26.5        # rayon de la base sous l'entonnoir
HANDLE_W = 32.0
HANDLE_END = 125.0   # bout du manche (X)
HANG_X, HANG_D = 116.0, 6.0      # trou de suspension
FILLET = 6.0

# Bec (goulot standard ~21.7 mm de passage)
BORE_D = 13.0
SPOUT_OD_TOP, SPOUT_OD_TIP = 20.5, 18.8
SPOUT_L = 12.0

# Entonnoir
CUP_H = 40.0
CUP_R_BOT, CUP_R_TOP = DISC_R, 30.0
CUP_WALL = 2.2
RIBS, RIB_A = 40, 0.7            # cannelures extérieures
SIEVE_R, SIEVE_T = 15.0, 1.6     # tamis
LEDGE_R = 13.5                   # épaulement qui porte le tamis

# Trappe
PLATE_W, PLATE_T = 20.0, 2.0
TRAVEL = BORE_D + 2.0            # 15 mm de course
PLATE_FRONT_CLOSED = -(BORE_D / 2 + 1.5)       # -8
HOLE_X_CLOSED = TRAVEL                         # 15 : trou côté manche quand fermé
STEM_X_CLOSED = 80.0
PLATE_REAR_CLOSED = 88.0
STEM_S = 5.6                     # tige carrée

# Bouton
KNOB_D, KNOB_H = 13.0, 5.0
RECESS_D = 0.8                   # cuvette autour de la fenêtre
KNOB_Z0 = Z_TOP - RECESS_D + 0.3
SOCKET_DEPTH = 3.5
STEM_TOP = KNOB_Z0 + SOCKET_DEPTH

# Tiges d'alignement (Ø2 mm : filament 1.75, tige acier, trombone…)
PIN_D = 2.1
PIN_DEPTH = 1.8
PINS = [(25, 13.2), (25, -13.2), (105, 13.2), (105, -13.2), (-15, 18), (-15, -18)]


# ------------------------------------------------------------------- outils
def rrect(x0, x1, w, r):
    """Rectangle arrondi (CrossSection) de x0 à x1, largeur w centrée en y."""
    return (CrossSection.square((x1 - x0 - 2 * r, w - 2 * r))
            .translate((x0 + r, -w / 2 + r))
            .offset(r, JoinType.Round, circular_segments=48))


def cyl(h, r1, r2=None, z=0.0, x=0.0, y=0.0):
    return Manifold.cylinder(h, r1, r1 if r2 is None else r2, SEG).translate((x, y, z))


def outline():
    disc = CrossSection.circle(DISC_R, SEG)
    handle = (CrossSection.square((HANDLE_END - HANDLE_W / 2, HANDLE_W))
              .translate((0, -HANDLE_W / 2))
              + CrossSection.circle(HANDLE_W / 2, SEG).translate((HANDLE_END - HANDLE_W / 2, 0)))
    shape = disc + handle
    # congé dans l'angle rentrant disque / manche
    return shape.offset(FILLET, JoinType.Round, circular_segments=48).offset(
        -FILLET, JoinType.Round, circular_segments=48)


def pin_holes(z0, depth):
    return Manifold.batch_boolean(
        [cyl(depth, PIN_D / 2, z=z0, x=x, y=y) for x, y in PINS],
        __import__("manifold3d").OpType.Add)


# --------------------------------------------------------------- pièces
def lower_body():
    body = outline().extrude(Z_SPLIT)
    spout = cyl(SPOUT_L, SPOUT_OD_TIP / 2, SPOUT_OD_TOP / 2, z=-SPOUT_L)
    # petit chanfrein au bout du bec
    body = body + spout
    # canal de la trappe (ouvert vers le haut)
    x0 = PLATE_FRONT_CLOSED - TRAVEL - CLR - 0.5
    x1 = PLATE_REAR_CLOSED + CLR + 0.5
    chan = rrect(x0, x1, PLATE_W + 2 * CLR, 1.0).extrude(CHAN_H + 1).translate((0, 0, Z_CHAN))
    body = body - chan
    body = body - cyl(SPOUT_L + Z_CHAN + 1, BORE_D / 2, z=-SPOUT_L - 0.5)
    body = body - cyl(Z_SPLIT + 2, HANG_D / 2, z=-1, x=HANG_X)
    body = body - pin_holes(Z_SPLIT - PIN_DEPTH, PIN_DEPTH + 1)
    return body


def fluted_section(r):
    pts = []
    n = RIBS * 12
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r - RIB_A * 0.5 * (1 - math.cos(RIBS * a))
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    return CrossSection([pts])


def upper_body():
    plate = outline().extrude(TOP_T).translate((0, 0, Z_SPLIT))
    s = CUP_R_TOP / CUP_R_BOT
    cup = fluted_section(CUP_R_BOT).extrude(CUP_H, n_divisions=8, scale_top=(s, s)).translate((0, 0, Z_TOP))
    # lèvre lisse en haut
    lip = cyl(1.6, CUP_R_TOP - RIB_A, CUP_R_TOP - RIB_A + 0.05, z=Z_TOP + CUP_H - 1.6)
    body = plate + cup + lip

    # cavité intérieure (du bas vers le haut)
    z = Z_SPLIT - 0.5
    hole = cyl(Z_TOP - z + 0.01, BORE_D / 2, z=z)
    z_ledge = Z_TOP + 3.0
    under = cyl(z_ledge - Z_TOP, BORE_D / 2, LEDGE_R, z=Z_TOP)
    z_sieve_top = z_ledge + SIEVE_T + 0.4
    pocket = cyl(z_sieve_top - z_ledge + 0.01, SIEVE_R + 0.2, z=z_ledge)
    top_z = Z_TOP + CUP_H + 0.5
    funnel = cyl(top_z - z_sieve_top, SIEVE_R + 0.2, CUP_R_TOP - RIB_A - CUP_WALL + 0.1, z=z_sieve_top)
    body = body - hole - under - pocket - funnel

    # fenêtre du bouton + cuvette
    wx0 = STEM_X_CLOSED - TRAVEL - STEM_S / 2 - 0.4
    wx1 = STEM_X_CLOSED + STEM_S / 2 + 0.4
    window = rrect(wx0, wx1, STEM_S + 0.6, 1.2).extrude(TOP_T + 2).translate((0, 0, Z_SPLIT - 1))
    recess = rrect(wx0 - 5.5, wx1 + 5.5, KNOB_D + 3.0, 7.0).extrude(RECESS_D + 1).translate(
        (0, 0, Z_TOP - RECESS_D))
    body = body - window - recess
    body = body - cyl(TOP_T + 2, HANG_D / 2, z=Z_SPLIT - 1, x=HANG_X)
    body = body - pin_holes(Z_SPLIT - 1, PIN_DEPTH + 1)
    return body


def slide_plate(open_=False):
    dx = -TRAVEL if open_ else 0.0
    p = rrect(PLATE_FRONT_CLOSED, PLATE_REAR_CLOSED, PLATE_W, 1.0).extrude(PLATE_T).translate((0, 0, Z_CHAN))
    p = p - cyl(PLATE_T + 2, BORE_D / 2 + 0.5, z=Z_CHAN - 1, x=HOLE_X_CLOSED)
    stem_h = STEM_TOP - (Z_CHAN + PLATE_T)
    stem = (Manifold.cube((STEM_S, STEM_S, stem_h + 0.01))
            .translate((STEM_X_CLOSED - STEM_S / 2, -STEM_S / 2, Z_CHAN + PLATE_T - 0.01)))
    return (p + stem).translate((dx, 0, 0))


def knob(open_=False):
    dx = -TRAVEL if open_ else 0.0
    # profil de révolution : cylindre + dôme bas (hauteur 2 mm)
    r, hc, hd = KNOB_D / 2, KNOB_H - 2.0, 2.0
    prof = [(0, 0), (r, 0), (r, hc)]
    for i in range(1, 17):
        t = i / 16 * math.pi / 2
        prof.append((r * math.cos(t), hc + hd * math.sin(t)))
    prof[-1] = (0, hc + hd)
    k = CrossSection([prof]).revolve(SEG).translate((0, 0, KNOB_Z0))
    # stries de préhension
    for i in range(-2, 3):
        k = k - Manifold.cube((0.8, KNOB_D + 2, 1.2)).translate(
            (i * 2.2 - 0.4, -KNOB_D / 2 - 1, KNOB_Z0 + KNOB_H - 0.6))
    s = STEM_S + 0.15  # serrage léger (+ colle si besoin)
    k = k - Manifold.cube((s, s, SOCKET_DEPTH + 0.2)).translate((-s / 2, -s / 2, KNOB_Z0 - 0.2))
    return k.translate((STEM_X_CLOSED + dx, 0, 0))


def sieve():
    disc = cyl(SIEVE_T, SIEVE_R - 0.15)
    hole, bar = 1.4, 0.8
    pitch = hole + bar
    n = int(SIEVE_R / pitch) + 2
    cuts = []
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            cx, cy = i * pitch, j * pitch
            if math.hypot(abs(cx) + hole / 2, abs(cy) + hole / 2) < LEDGE_R - 1.0:
                cuts.append(Manifold.cube((hole, hole, SIEVE_T + 2)).translate((cx - hole / 2, cy - hole / 2, -1)))
    from manifold3d import OpType
    return disc - Manifold.batch_boolean(cuts, OpType.Add)


# --------------------------------------------------------------- export
def to_tm(m, color=None):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=True)
    if color is not None:
        t.visual.face_colors = color
    return t


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
    os.makedirs(out, exist_ok=True)

    lower, upper = lower_body(), upper_body()
    plate, kn, sv = slide_plate(), knob(), sieve()
    z_ledge = Z_TOP + 3.0

    # Pièces orientées pour l'impression (face plane sur le plateau)
    print_parts = {
        "1_corps_inferieur": lower.rotate((180, 0, 0)).translate((0, 0, Z_SPLIT)),  # à l'envers, bec en l'air
        "2_corps_superieur_entonnoir": upper.translate((0, 0, -Z_SPLIT)),
        "3_trappe_coulissante": plate.translate((0, 0, -Z_CHAN)),
        "4_bouton": kn.rotate((180, 0, 0)).translate((0, 0, KNOB_Z0 + KNOB_H)),       # dôme sur le plateau
        "5_tamis": sv,
    }
    for name, m in print_parts.items():
        t = to_tm(m)
        assert t.is_watertight, name
        t.apply_translation((-t.bounds[0][0] - (t.bounds[1][0] - t.bounds[0][0]) / 2,
                             -t.bounds[0][1] - (t.bounds[1][1] - t.bounds[0][1]) / 2,
                             -t.bounds[0][2]))
        t.export(os.path.join(out, f"{name}.stl"))
        print(f"{name:32s} {t.extents.round(1)} mm  {t.volume / 1000:.1f} cm3")

    # Assemblage (couleurs du visuel)
    grey, black, steel = [158, 163, 168, 255], [30, 30, 32, 255], [120, 124, 128, 255]
    scene = trimesh.Scene()
    for name, m, c in [("corps_inferieur", lower, grey), ("corps_superieur", upper, grey),
                       ("trappe", plate, black), ("bouton", kn, black),
                       ("tamis", sv.translate((0, 0, z_ledge)), steel)]:
        scene.add_geometry(to_tm(m, c), node_name=name, geom_name=name)
    root = os.path.dirname(out)
    scene.export(os.path.join(root, "dozr_assemblage.glb"))
    scene.export(os.path.join(root, "dozr_assemblage.3mf"))
    to_tm(Manifold.batch_boolean([lower, upper, plate, kn, sv.translate((0, 0, z_ledge))],
                                 __import__("manifold3d").OpType.Add)).export(
        os.path.join(root, "dozr_assemblage.stl"))

    # contrôles d'interférence (fermé et ouvert)
    for open_ in (False, True):
        mov = slide_plate(open_) + knob(open_)
        inter = (mov ^ (lower + upper)).volume()
        print(f"interférence trappe/corps ({'ouvert' if open_ else 'fermé'}) : {inter:.3f} mm3")
    # passage : en position ouverte, le trou de la trappe est aligné avec le bec
    bore = cyl(30, BORE_D / 2 - 0.05, z=-5)
    print("obstruction ouvert :", round((bore ^ slide_plate(True)).volume(), 3), "mm3",
          "| obstruction fermé :", round((bore ^ slide_plate(False)).volume(), 1), "mm3")
    print("capacité entonnoir ≈",
          round(math.pi * CUP_H / 3 * ((SIEVE_R) ** 2 + SIEVE_R * 27.8 + 27.8 ** 2) / 1000), "ml")


if __name__ == "__main__":
    main()
