"""
Dozr — doseur à poudre, forme calquée sur les vues de référence (face + 3/4).

    pip install manifold3d trimesh numpy scipy networkx lxml
    python3 dozr.py   -> STL des pièces + assemblage (3MF / GLB / STL)

Unités : mm. Origine au centre du fond de l'entonnoir, manche selon +X,
Z vers le haut (ouverture de l'entonnoir et bouton vers le haut).

Proportions relevées sur la vue de face (échelle : manche = 30 mm) :
  entonnoir Ø55, manche 30 mm, longueur totale ~160 mm, pilule noire
  17,3 × 49 mm à 38 mm du centre, bouton Ø16 avec disque central Ø9,
  trou de suspension Ø6 à 125 mm, tamis Ø26.
Profil relevé sur la vue 3/4 : entonnoir bas (~26 mm) à fond très arrondi,
cannelures dehors (jusque sur l'arrondi) et dedans, manche plat collé
sous le fond, pilule noire en creux, bouton cylindrique en relief.

Mécanisme caché : une languette glisse dans un canal sous le fond.
Bouton côté entonnoir (comme sur les vues) = fermé ; bouton tiré vers
le bout du manche = ouvert.

Pièces : 1 corps inférieur (bec + canal), 2 corps supérieur (entonnoir +
dessus du manche), 3 languette, 4 bouton, 5 tamis, 6 insert noir (pilule).
"""
import math
import os

import numpy as np
from manifold3d import CrossSection, Manifold, JoinType, OpType
import trimesh

RIBS = 52
SEG = RIBS * 8

# ----------------------------------------------------------------- entonnoir
CUP_R = 27.5            # rayon extérieur au bord
CUP_H = 28.0            # hauteur totale (fond -> bord)
BOT_R = 14.0            # rayon du méplat sous le fond
BOT_FILLET = 12.0       # grand arrondi du fond
WALL = 1.8
RIB_OUT, RIB_IN = 0.8, 0.45
FLOOR_Z = 9.5           # fond intérieur
FLOOR_FILLET = 4.0

# ----------------------------------------------------------------- manche
HANDLE_W, HANDLE_T = 30.0, 9.0
HANDLE_X0, HANDLE_END = 16.0, 133.0
HANDLE_CORNER, EDGE_R = 4.0, 1.5
HANG_X, HANG_D, HANG_CSK = 124.7, 6.0, 8.5

# Pilule noire (en creux) + bouton
PILL_X0, PILL_X1, PILL_W = 37.7, 86.7, 17.3
PILL_RECESS = 2.2       # profondeur de la cuvette
INSERT_T = 1.2          # insert noir : surface noire 1 mm sous le manche
KNOB_D, KNOB_H = 16.2, 5.5
KNOB_DISC_D = 9.0
KNOB_X = PILL_X0 + PILL_W / 2   # concentrique au bout de la pilule côté entonnoir = fermé

# Tamis, bec
SIEVE_D, SIEVE_T = 26.0, 1.6
BORE_D = 14.0
SPOUT_L, SPOUT_OD_TOP, SPOUT_OD_TIP = 0.0, 20.5, 19.0   # 0 = fond plat posé sur le goulot (comme les vues) ; 8 = bec qui rentre dans le goulot

# Mécanisme
CLR = 0.3
Z_CHAN, CHAN_H = 2.0, 2.4
Z_SPLIT = Z_CHAN + CHAN_H            # 4.4 : plan de joint
PLATE_W, PLATE_T = 14.5, 2.0
PLATE_FRONT = -(BORE_D / 2 + 2.5)
TRAVEL = BORE_D + 4.0                # 18 mm
STEM_S = 5.6
PLATE_REAR = KNOB_X + TRAVEL + 4.0
Z_INSERT = HANDLE_T - PILL_RECESS
KNOB_Z0 = Z_INSERT + INSERT_T + 0.3
SOCKET = 3.0

PIN_D, PIN_DEPTH = 2.1, 1.8
PINS = [(-12, 11), (-12, -11), (40, 11.6), (40, -11.6), (112, 11.6), (112, -11.6)]


# ----------------------------------------------------------------- outils
def rrect(x0, x1, w, r):
    return (CrossSection.square((x1 - x0 - 2 * r, w - 2 * r)).translate((x0 + r, -w / 2 + r))
            .offset(r, JoinType.Round, circular_segments=48))


def cyl(h, r1, r2=None, x=0.0, y=0.0, z=0.0, seg=128):
    return Manifold.cylinder(h, r1, r1 if r2 is None else r2, seg).translate((x, y, z))


def union(parts):
    return Manifold.batch_boolean(parts, OpType.Add)


def rounded_extrude(cs, h, r, steps=6):
    """Extrusion à arêtes haut/bas arrondies (tranches)."""
    parts = []
    zs = [r * (1 - math.cos(math.pi / 2 * i / steps)) for i in range(steps + 1)]
    for i in range(steps):
        z0, z1 = zs[i], zs[i + 1]
        inset = r - math.sqrt(max(r * r - (r - z1) ** 2, 0))
        sl = cs.offset(-inset, JoinType.Round, circular_segments=48)
        parts += [sl.extrude(z1 - z0 + 1e-3).translate((0, 0, z0)),
                  sl.extrude(z1 - z0 + 1e-3).translate((0, 0, h - z1))]
    parts.append(cs.extrude(h - 2 * r + 2e-3).translate((0, 0, r - 1e-3)))
    return union(parts)


def flute(m, k):
    """Cannelures verticales : modulation radiale proportionnelle à l'angle."""
    def f(v):
        x, y, z = v
        s = 1 - k * 0.5 * (1 - math.cos(RIBS * math.atan2(y, x)))
        return (x * s, y * s, z)
    return m.warp(f)


def outer_profile(extend=0.0):
    """Demi-profil extérieur (r, z) : méplat, grand arrondi, flanc légèrement évasé."""
    pts = [(0, 0)]
    cx, cz = BOT_R, BOT_FILLET
    for i in range(25):
        t = -math.pi / 2 + math.pi / 2 * i / 24
        pts.append((cx + BOT_FILLET * math.cos(t), cz + BOT_FILLET * math.sin(t)))
    pts += [(CUP_R, CUP_H + extend), (0, CUP_H + extend)]
    return pts


# ----------------------------------------------------------------- formes
def cup_outer():
    return flute(CrossSection([outer_profile()]).revolve(SEG), RIB_OUT / CUP_R)


def cup_cavity():
    cs = CrossSection([outer_profile(extend=10)]).offset(-WALL, JoinType.Round, circular_segments=64)
    cs = cs ^ CrossSection.square((CUP_R + 5, CUP_H + 20)).translate((0, FLOOR_Z))
    cs = cs.offset(-FLOOR_FILLET, JoinType.Round, circular_segments=64).offset(
        FLOOR_FILLET, JoinType.Round, circular_segments=64)                 # congé du fond
    cs = cs + CrossSection.square((FLOOR_FILLET * 2 + 1, CUP_H + 20)).translate((0, FLOOR_Z))  # axe
    cs = cs ^ CrossSection.square((CUP_R + 5, CUP_H + 30)).translate((0, -1))
    m = flute(cs.revolve(SEG), -RIB_IN / CUP_R)
    z_rec = FLOOR_Z - SIEVE_T
    m = m + cyl(SIEVE_T + 0.5, SIEVE_D / 2 + 0.2, z=z_rec)                  # logement du tamis
    m = m + cyl(z_rec - Z_SPLIT - 2.6 + 0.01, BORE_D / 2, SIEVE_D / 2 - 1.5, z=Z_SPLIT + 2.6)
    m = m + cyl(2.7, BORE_D / 2, z=Z_SPLIT - 0.05)
    return m


def stem_slot(h):
    return rrect(KNOB_X - STEM_S / 2 - 0.6, KNOB_X + TRAVEL + STEM_S / 2 + 0.6, STEM_S + 0.5, 1.0).extrude(h)


def full_body():
    handle = rounded_extrude(rrect(HANDLE_X0, HANDLE_END, HANDLE_W, HANDLE_CORNER), HANDLE_T, EDGE_R)
    body = cup_outer() + handle
    if SPOUT_L > 0:
        body = body + cyl(SPOUT_L + 0.5, SPOUT_OD_TIP / 2, SPOUT_OD_TOP / 2, z=-SPOUT_L)
    body = body - cup_cavity()
    body = body - cyl(SPOUT_L + 6, BORE_D / 2, z=-SPOUT_L - 1)
    # trou de suspension chanfreiné des deux côtés
    body = body - cyl(HANDLE_T + 2, HANG_D / 2, x=HANG_X, z=-1)
    c = (HANG_CSK - HANG_D) / 2
    body = body - cyl(c + 0.01, HANG_CSK / 2, HANG_D / 2, x=HANG_X, z=-0.01)
    body = body - cyl(c + 0.01, HANG_D / 2, HANG_CSK / 2, x=HANG_X, z=HANDLE_T - c)
    # cuvette en pilule + fente de la tige + canal
    body = body - rrect(PILL_X0, PILL_X1, PILL_W, PILL_W / 2).extrude(PILL_RECESS + 1).translate((0, 0, Z_INSERT))
    body = body - stem_slot(HANDLE_T).translate((0, 0, Z_SPLIT - 1))
    body = body - rrect(PLATE_FRONT - CLR - 0.5, PLATE_REAR + TRAVEL + CLR + 0.5, PLATE_W + 2 * CLR, 2.0).extrude(
        CHAN_H).translate((0, 0, Z_CHAN))
    return body


def pins():
    return union([cyl(2 * PIN_DEPTH, PIN_D / 2, x=x, y=y, z=Z_SPLIT - PIN_DEPTH, seg=32) for x, y in PINS])


def bodies():
    b = full_body() - pins()
    return b.trim_by_plane((0, 0, -1), -Z_SPLIT), b.trim_by_plane((0, 0, 1), Z_SPLIT)


def slide_plate(open_=False):
    p = rrect(PLATE_FRONT, PLATE_REAR, PLATE_W, 4.0).extrude(PLATE_T).translate((0, 0, Z_CHAN))
    h = KNOB_Z0 + SOCKET - (Z_CHAN + PLATE_T)
    p = p + Manifold.cube((STEM_S, STEM_S, h + 0.01)).translate(
        (KNOB_X - STEM_S / 2, -STEM_S / 2, Z_CHAN + PLATE_T - 0.01))
    return p.translate((TRAVEL if open_ else 0, 0, 0))


def knob(open_=False):
    """Bouton cylindrique à dessus plat, bord adouci, disque central en relief."""
    r, h, ch = KNOB_D / 2, KNOB_H, 0.7
    prof = [(0, 0), (r, 0), (r, h - ch)]
    for i in range(1, 9):
        t = i / 8 * math.pi / 2
        prof.append((r - ch + ch * math.cos(t), h - ch + ch * math.sin(t)))
    prof.append((0, h))
    k = CrossSection([prof]).revolve(128)
    rd = KNOB_DISC_D / 2
    disc = CrossSection([[(0, h - 0.1), (rd, h - 0.1), (rd, h + 0.35), (rd - 0.25, h + 0.6), (0, h + 0.6)]]).revolve(128)
    groove = (CrossSection.circle(rd + 0.65, 96) - CrossSection.circle(rd + 0.1, 96)).extrude(0.6).translate((0, 0, h - 0.4))
    k = k + disc - groove
    s = STEM_S + 0.15
    k = k - Manifold.cube((s, s, SOCKET + 0.2)).translate((-s / 2, -s / 2, -0.2))
    return k.translate((KNOB_X + (TRAVEL if open_ else 0), 0, KNOB_Z0))


def pill_insert():
    p = rrect(PILL_X0 + 0.15, PILL_X1 - 0.15, PILL_W - 0.3, (PILL_W - 0.3) / 2).extrude(INSERT_T)
    p = p - stem_slot(INSERT_T + 2).translate((0, 0, -1))
    return p.translate((0, 0, Z_INSERT))


def sieve():
    r = SIEVE_D / 2 - 0.1
    hole, bar = 1.2, 0.8
    pitch = hole + bar
    n = int(r / pitch) + 2
    cuts = [Manifold.cube((hole, hole, SIEVE_T + 2)).translate((i * pitch - hole / 2, j * pitch - hole / 2, -1))
            for i in range(-n, n + 1) for j in range(-n, n + 1)
            if math.hypot(abs(i * pitch) + hole / 2, abs(j * pitch) + hole / 2) < r - 1.4]
    return (cyl(SIEVE_T, r) - union(cuts)).translate((0, 0, FLOOR_Z - SIEVE_T))


# ----------------------------------------------------------------- export
def to_tm(m, color=None):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=True)
    if color is not None:
        t.visual.face_colors = color
    return t


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(root, "stl")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))

    lower, upper = bodies()
    plate, kn, sv, pill = slide_plate(), knob(), sieve(), pill_insert()

    printable = {
        "1_corps_inferieur": lower.rotate((180, 0, 0)),   # plan de joint sur le plateau, bec en l'air
        "2_corps_superieur_entonnoir": upper,
        "3_languette": plate,
        "4_bouton": kn.rotate((180, 0, 0)),                # dessus sur le plateau
        "5_tamis": sv,
        "6_insert_noir": pill,
    }
    for name, m in printable.items():
        t = to_tm(m)
        assert t.is_watertight, name
        b = t.bounds
        t.apply_translation((-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]))
        t.export(os.path.join(out, f"{name}.stl"))
        print(f"{name:30s} {t.extents.round(1)} mm  {t.volume / 1000:.1f} cm3")

    grey, black, steel = [118, 122, 128, 255], [24, 24, 26, 255], [150, 152, 155, 255]
    parts = [("corps_inferieur", lower, grey), ("corps_superieur", upper, grey), ("languette", plate, black),
             ("bouton", kn, black), ("tamis", sv, steel), ("insert_noir", pill, black)]
    scene = trimesh.Scene()
    for name, m, c in parts:
        scene.add_geometry(to_tm(m, c), node_name=name, geom_name=name)
    scene.export(os.path.join(root, "dozr_assemblage.glb"))
    scene.export(os.path.join(root, "dozr_assemblage.3mf"))
    to_tm(union([m for _, m, _ in parts])).export(os.path.join(root, "dozr_assemblage.stl"))

    fixed = lower + upper + pill + sv
    for open_ in (False, True):
        mov = slide_plate(open_) + knob(open_)
        print(f"interférence ({'ouvert' if open_ else 'fermé'}) : {(mov ^ fixed).volume():.3f} mm3")
    bore = cyl(40, BORE_D / 2 - 0.05, z=-12)
    print("obstruction du bec — ouvert :", round((bore ^ slide_plate(True)).volume(), 2),
          "mm3 | fermé :", round((bore ^ slide_plate(False)).volume(), 1), "mm3")
    t = to_tm(lower + upper)
    print("encombrement :", t.extents.round(1), "mm | min. paroi tamis/canal ok")


if __name__ == "__main__":
    main()
