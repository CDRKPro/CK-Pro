"""
Dozr — doseur à poudre (forme fidèle au visuel produit).

    pip install manifold3d trimesh numpy scipy networkx lxml
    python3 dozr.py   -> STL des pièces + assemblage (3MF / GLB / STL)

Unités : mm. Origine au centre de l'entonnoir, manche selon +X, Z vers le haut.

Forme (d'après la photo) :
  - entonnoir évasé, cannelé verticalement à l'extérieur ET à l'intérieur,
    fond arrondi, fond intérieur plat avec un tamis métallique rond au centre ;
  - manche plat et droit, bouts arrondis, trou de suspension au bout ;
  - longue fente noire en forme de pilule sur le manche, bouton rond noir
    placé côté entonnoir.

Mécanisme (caché) : une languette glisse dans un canal sous le fond.
Bouton côté entonnoir (position de la photo) = fermé ; bouton tiré vers
le bout du manche = ouvert, la poudre tombe par le bec dans la bouteille.

Pièces : 1 corps inférieur (bec + canal), 2 corps supérieur (entonnoir +
dessus du manche), 3 languette, 4 bouton, 5 tamis, 6 insert noir (pilule).
"""
import math
import os

import numpy as np
from manifold3d import CrossSection, Manifold, JoinType, OpType
import trimesh

RIBS = 48
SEG = RIBS * 8

# ----------------------------------------------------------------- cotes
LENGTH = 175.0                       # longueur totale
CUP_R_TOP, CUP_R_BOT = 28.0, 22.0    # rayons extérieurs de l'entonnoir
CUP_H = 46.0
CUP_FILLET = 4.0                     # arrondi du fond
WALL = 2.2
RIB_OUT, RIB_IN = 0.8, 0.45          # profondeur des cannelures

HANDLE_W, HANDLE_T = 30.0, 9.0
HANDLE_END = LENGTH - CUP_R_TOP      # 147
EDGE_R = 1.2                         # arrondi des arêtes du manche
HANG_D, HANG_X = 6.0, HANDLE_END - 9.0

# Pilule noire + bouton
PILL_X0, PILL_X1, PILL_W, PILL_DEPTH = 36.0, 100.0, 22.0, 1.5
KNOB_D, KNOB_H = 17.0, 4.0

# Fond intérieur, tamis, bec
FLOOR_Z = 11.0
SIEVE_D, SIEVE_T = 23.0, 1.6
BORE_D = 14.0
SPOUT_L, SPOUT_OD_TOP, SPOUT_OD_TIP = 10.0, 20.5, 19.0

# Mécanisme
CLR = 0.3
Z_CHAN, CHAN_H = 2.0, 2.4
Z_SPLIT = Z_CHAN + CHAN_H            # 4.4 : plan de joint
PLATE_W, PLATE_T = 18.0, 2.0
PLATE_FRONT = -(BORE_D / 2 + 2.5)    # -9.5 en position fermée
TRAVEL = BORE_D + 4.0                # 18 : la languette dégage le bec
STEM_S = 5.6
KNOB_X = PILL_X0 + KNOB_D / 2 + 2.0  # bouton côté entonnoir (fermé)
PLATE_REAR = KNOB_X + TRAVEL + 4.0   # couvre toute la fente : on ne voit que du noir
KNOB_Z0 = HANDLE_T + 0.3
SOCKET = 3.0

PIN_D, PIN_DEPTH = 2.1, 1.8
PINS = [(-12, 12), (-12, -12), (32, 12.2), (32, -12.2), (125, 12.2), (125, -12.2)]


# ----------------------------------------------------------------- outils
def rrect(x0, x1, w, r):
    return (CrossSection.square((x1 - x0 - 2 * r, w - 2 * r)).translate((x0 + r, -w / 2 + r))
            .offset(r, JoinType.Round, circular_segments=48))


def cyl(h, r1, r2=None, x=0.0, y=0.0, z=0.0, seg=128):
    return Manifold.cylinder(h, r1, r1 if r2 is None else r2, seg).translate((x, y, z))


def union(parts):
    return Manifold.batch_boolean(parts, OpType.Add)


def rounded_extrude(cs, h, r, steps=6):
    """Extrusion avec arêtes haut/bas arrondies (approximation par tranches)."""
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
    """Cannelures : modulation radiale proportionnelle selon l'angle."""
    def f(v):
        x, y, z = v
        a = math.atan2(y, x)
        s = 1 - k * 0.5 * (1 - math.cos(RIBS * a))
        return (x * s, y * s, z)
    return m.warp(f)


def r_out(z):
    return CUP_R_BOT + (CUP_R_TOP - CUP_R_BOT) * z / CUP_H


# ----------------------------------------------------------------- formes
def cup_outer():
    rf = CUP_FILLET
    prof = [(0, 0)]
    for i in range(13):  # arrondi du fond
        t = -math.pi / 2 + math.pi / 2 * i / 12
        prof.append((r_out(rf) - rf + rf * math.cos(t), rf + rf * math.sin(t)))
    prof += [(r_out(CUP_H), CUP_H), (0, CUP_H)]
    return flute(CrossSection([prof]).revolve(SEG), RIB_OUT / CUP_R_TOP)


def cup_cavity():
    rf = 3.0
    ri = lambda z: r_out(z) - WALL
    prof = [(0, FLOOR_Z)]
    for i in range(10):
        t = -math.pi / 2 + math.pi / 2 * i / 9
        prof.append((ri(FLOOR_Z + rf) - rf + rf * math.cos(t), FLOOR_Z + rf + rf * math.sin(t)))
    prof += [(ri(CUP_H) + 0.01, CUP_H + 1), (0, CUP_H + 1)]
    m = flute(CrossSection([prof]).revolve(SEG), -RIB_IN / CUP_R_TOP)  # nervures intérieures
    z_rec = FLOOR_Z - SIEVE_T
    m = m + cyl(SIEVE_T + 0.5, SIEVE_D / 2 + 0.2, z=z_rec)                       # logement du tamis
    m = m + cyl(z_rec - Z_SPLIT - 2.6 + 0.01, BORE_D / 2, SIEVE_D / 2 - 1.5, z=Z_SPLIT + 2.6)
    m = m + cyl(2.7, BORE_D / 2, z=Z_SPLIT - 0.05)
    return m


def stem_slot(h):
    return rrect(KNOB_X - STEM_S / 2 - 0.6, KNOB_X + TRAVEL + STEM_S / 2 + 0.6, STEM_S + 0.5, 1.0).extrude(h)


def full_body():
    body = cup_outer() + rounded_extrude(rrect(0, HANDLE_END, HANDLE_W, 6.0), HANDLE_T, EDGE_R)
    body = body + cyl(SPOUT_L + 0.5, SPOUT_OD_TIP / 2, SPOUT_OD_TOP / 2, z=-SPOUT_L)
    body = body - cup_cavity()
    body = body - cyl(SPOUT_L + 6, BORE_D / 2, z=-SPOUT_L - 1)
    body = body - cyl(HANDLE_T + 2, HANG_D / 2, x=HANG_X, z=-1)
    body = body - rrect(PILL_X0, PILL_X1, PILL_W + 0.3, (PILL_W + 0.3) / 2).extrude(PILL_DEPTH + 1).translate(
        (0, 0, HANDLE_T - PILL_DEPTH))
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
    r, hc, hd = KNOB_D / 2, KNOB_H - 1.0, 1.0
    prof = [(0, 0), (r, 0), (r, hc - 0.6)]
    for i in range(1, 13):  # bord arrondi + léger bombé
        t = i / 12 * math.pi / 2
        prof.append((r - 0.6 * (1 - math.cos(t)) - (r - 0.6) * (1 - math.cos(t)) * 0.12,
                     hc - 0.6 + (0.6 + hd) * math.sin(t)))
    prof.append((0, hc + hd))
    k = CrossSection([prof]).revolve(96)
    ring = (CrossSection.circle(5.8, 96) - CrossSection.circle(5.0, 96)).extrude(1.5).translate((0, 0, hc + hd - 0.55))
    k = k - ring  # cercle intérieur du bouton
    s = STEM_S + 0.15
    k = k - Manifold.cube((s, s, SOCKET + 0.2)).translate((-s / 2, -s / 2, -0.2))
    return k.translate((KNOB_X + (TRAVEL if open_ else 0), 0, KNOB_Z0))


def pill_insert():
    p = rrect(PILL_X0 + 0.1, PILL_X1 - 0.1, PILL_W, PILL_W / 2).extrude(PILL_DEPTH)
    p = p - stem_slot(PILL_DEPTH + 2).translate((0, 0, -1))
    return p.translate((0, 0, HANDLE_T - PILL_DEPTH))


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

    grey, black, steel = [165, 170, 176, 255], [28, 28, 30, 255], [125, 128, 132, 255]
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
    print("longueur totale :", round(to_tm(lower + upper).extents[0], 1), "mm")


if __name__ == "__main__":
    main()
