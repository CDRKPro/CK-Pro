"""
Dozr — doseur à poudre, forme calquée sur les vues de référence.

    pip install manifold3d trimesh numpy scipy networkx lxml
    python3 dozr.py   -> STL des pièces + assemblage (3MF / GLB / STL)

Unités : mm. Origine au centre du dessous de l'entonnoir, manche selon +X,
Z vers le haut. Le bec dépasse sous l'entonnoir (Z < 0).

Forme :
  - entonnoir CONIQUE vers le bas (Ø55 en haut -> Ø34 en bas), paroi
    cannelée (cannelures visibles dehors et dedans), lèvre arrondie ;
  - bec de 10 mm sous le fond, Ø20 : rentre dans un goulot standard
    (bouteilles d'eau / shakers, passage ~21,7 mm) ;
  - entonnoir + manche = UNE SEULE pièce, sans joint visible dessus ni
    sur les côtés, arêtes du manche réellement arrondies ;
  - pilule noire en creux, bouton rond noir en relief côté entonnoir,
    trou de suspension chanfreiné.

Mécanisme caché : une languette glisse dans un canal sous le fond.
Bouton côté entonnoir = fermé ; bouton tiré vers le bout du manche = ouvert.
Le canal est fermé par dessous par le couvercle qui porte le bec
(seul joint du modèle, invisible une fois posé sur la bouteille).

Pièces : 1 corps (entonnoir + manche), 2 couvercle avec bec, 3 languette
avec tige, 4 bouton, 5 tamis, 6 insert noir (pilule).
"""
import math
import os

import numpy as np
from manifold3d import CrossSection, Manifold, JoinType, OpType
import trimesh

RIBS = 48
SEG = RIBS * 14

# ----------------------------------------------------------------- entonnoir
CUP_R_TOP = 27.5        # rayon extérieur au bord (Ø55)
CUP_R_BOT = 17.0        # rayon extérieur en bas (Ø34) : forme conique
CUP_H = 34.0
BOT_FILLET = 2.5        # arrondi du bord inférieur
WALL = 2.0
LIP_R = 0.95            # arrondi de la lèvre
RIB_K = 1.0 / CUP_R_TOP  # profondeur des rainures (1 mm au bord)
RIM_BAND = 1.8          # bandeau lisse sous la lèvre
RIB_START = 15.5        # rayon à partir duquel la paroi est cannelée
FLOOR_Z = 9.5           # fond intérieur
FLOOR_FILLET = 3.0

# ----------------------------------------------------------------- bec (sur le couvercle)
SPOUT_L = 10.0
SPOUT_OD, SPOUT_OD_TIP = 20.0, 19.2
BORE_D = 14.0

# ----------------------------------------------------------------- manche
HANDLE_W, HANDLE_T = 30.0, 9.0
HANDLE_X0, HANDLE_END = 0.0, 133.0
HANDLE_CORNER, EDGE_R = 4.0, 1.6
HANG_X, HANG_D, HANG_CSK = 124.7, 6.0, 8.5

# Pilule noire (en creux) + bouton
PILL_X0, PILL_X1, PILL_W = 37.7, 86.7, 17.3
PILL_RECESS = 2.2
INSERT_T = 1.2
KNOB_D, KNOB_H, KNOB_DISC_D = 16.2, 5.5, 9.0
KNOB_X = PILL_X0 + PILL_W / 2      # bouton concentrique au bout de la pilule = fermé

# Tamis
SIEVE_D, SIEVE_T = 26.0, 1.6

# Mécanisme
CLR = 0.3
Z_CHAN, CHAN_H = 2.0, 2.4
PLATE_W, PLATE_T = 14.5, 2.0
PLATE_FRONT = -(BORE_D / 2 + 2.5)
TRAVEL = BORE_D + 4.0              # 18 mm
STEM_S = 5.6
PLATE_REAR = KNOB_X + TRAVEL + 4.0
CH_X0, CH_X1 = PLATE_FRONT - CLR - 0.5, PLATE_REAR + TRAVEL + CLR + 0.5
CH_W = PLATE_W + 2 * CLR
Z_INSERT = HANDLE_T - PILL_RECESS
KNOB_Z0 = Z_INSERT + INSERT_T + 0.3
SOCKET = 3.0
COVER_T = Z_CHAN
COVER_DISC_R = 12.5


# ----------------------------------------------------------------- outils
def rrect(x0, x1, w, r):
    return (CrossSection.square((x1 - x0 - 2 * r, w - 2 * r)).translate((x0 + r, -w / 2 + r))
            .offset(r, JoinType.Round, circular_segments=64))


def cyl(h, r1, r2=None, x=0.0, y=0.0, z=0.0, seg=128):
    return Manifold.cylinder(h, r1, r1 if r2 is None else r2, seg).translate((x, y, z))


def union(parts):
    return Manifold.batch_boolean(parts, OpType.Add)


def arc(cx, cz, r, a0, a1, n=16):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cz + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def fillet(p0, p1, p2, r, n=16):
    """Points d'un congé de rayon r au sommet p1 (entre p0->p1 et p1->p2)."""
    v1 = np.subtract(p0, p1); v1 = v1 / np.linalg.norm(v1)
    v2 = np.subtract(p2, p1); v2 = v2 / np.linalg.norm(v2)
    ang = math.acos(np.clip(np.dot(v1, v2), -1, 1))
    d = r / math.tan(ang / 2)
    t1, t2 = np.add(p1, v1 * d), np.add(p1, v2 * d)
    bis = (v1 + v2) / np.linalg.norm(v1 + v2)
    c = np.add(p1, bis * (r / math.sin(ang / 2)))
    a0 = math.atan2(t1[1] - c[1], t1[0] - c[0])
    a1 = math.atan2(t2[1] - c[1], t2[0] - c[0])
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    return [(c[0] + r * math.cos(a0 + da * i / n), c[1] + r * math.sin(a0 + da * i / n)) for i in range(n + 1)]


def flute(m):
    """Paroi cannelée : modulation radiale selon l'angle, seulement sur la paroi."""
    def f(v):
        x, y, z = v
        r = math.hypot(x, y)
        t = min(max((r - RIB_START) / 2.0, 0.0), 1.0)
        w = t * t * (3 - 2 * t)
        u = min(max((CUP_H - RIM_BAND - z) / 1.2, 0.0), 1.0)   # bandeau lisse en haut
        w *= u * u * (3 - 2 * u)
        # côtes larges et bombées séparées par des rainures fines (comme le visuel)
        g = (1 - abs(math.sin(RIBS * math.atan2(y, x) / 2))) ** 1.8
        s = 1 - RIB_K * w * g
        return (x * s, y * s, z)
    return m.warp(f)


def r_out(z):
    return CUP_R_BOT + (CUP_R_TOP - CUP_R_BOT) * z / CUP_H


# ----------------------------------------------------------------- corps
def cup_section():
    """Demi-coupe (r, z) de l'entonnoir plein : cône, fond plat, lèvre arrondie."""
    top = (CUP_R_TOP, CUP_H)
    corner = (CUP_R_BOT, 0.0)
    outer = [(0, 0)] + fillet((0, 0), corner, top, BOT_FILLET) + [top, (0, CUP_H)]
    ext = (r_out(CUP_H + 10), CUP_H + 10)
    outer_ext = [(0, 0)] + fillet((0, 0), corner, ext, BOT_FILLET) + [ext, (0, CUP_H + 10)]

    cav = CrossSection([outer_ext]).offset(-WALL, JoinType.Round, circular_segments=96)
    cav = cav ^ CrossSection.square((CUP_R_TOP + 10, CUP_H + 20)).translate((0, FLOOR_Z))
    cav = cav.offset(-FLOOR_FILLET, JoinType.Round, circular_segments=64).offset(
        FLOOR_FILLET, JoinType.Round, circular_segments=64)
    cav = cav + CrossSection.square((2 * FLOOR_FILLET + 1, CUP_H + 20)).translate((0, FLOOR_Z))

    sec = CrossSection([outer]) - cav
    sec = sec.offset(-LIP_R, JoinType.Round, circular_segments=48).offset(LIP_R, JoinType.Round, circular_segments=48)
    sec = sec + CrossSection.square((2.5, FLOOR_Z))           # rétablit l'axe
    sec = sec ^ CrossSection.square((CUP_R_TOP + 5, CUP_H + 5))
    return sec


def handle():
    """Manche plat à coins et arêtes réellement arrondis (enveloppe de 4 palets)."""
    rc, re, t = HANDLE_CORNER, EDGE_R, HANDLE_T
    prof = [(0, 0), (rc - re, 0)] + arc(rc - re, re, re, -math.pi / 2, 0, 12)[1:] + \
        arc(rc - re, t - re, re, 0, math.pi / 2, 12) + [(0, t)]
    puck = CrossSection([prof]).revolve(64)
    y = HANDLE_W / 2 - rc
    return Manifold.batch_hull([puck.translate((x, s * y, 0))
                                for x in (HANDLE_X0 + rc, HANDLE_END - rc) for s in (-1, 1)])


def cover_outline():
    return CrossSection.circle(COVER_DISC_R, 128) + rrect(CH_X0 - 2, CH_X1 + 2, CH_W + 4, 3.0)


def stem_slot(h):
    return rrect(KNOB_X - STEM_S / 2 - 0.6, KNOB_X + TRAVEL + STEM_S / 2 + 0.6, STEM_S + 0.5, 1.0).extrude(h)


def body():
    b = flute(cup_section().revolve(SEG).refine_to_length(0.8)) + handle()
    # passage de la poudre sous le tamis
    z_rec = FLOOR_Z - SIEVE_T
    b = b - cyl(SIEVE_T + 0.5, SIEVE_D / 2 + 0.2, z=z_rec)
    b = b - cyl(z_rec - (Z_CHAN + CHAN_H + 2.6) + 0.01, BORE_D / 2, SIEVE_D / 2 - 1.5, z=Z_CHAN + CHAN_H + 2.6)
    b = b - cyl(z_rec, BORE_D / 2, z=Z_CHAN)
    # canal de la languette + logement du couvercle (par dessous)
    b = b - rrect(CH_X0, CH_X1, CH_W, 2.0).extrude(CHAN_H).translate((0, 0, Z_CHAN))
    b = b - cover_outline().offset(0.15, JoinType.Round).extrude(COVER_T + 1).translate((0, 0, -1))
    # pilule en creux avec petit chanfrein
    L = PILL_X1 - PILL_X0
    pill = rrect(-L / 2, L / 2, PILL_W, PILL_W / 2)
    b = b - pill.extrude(PILL_RECESS + 1).translate(((PILL_X0 + PILL_X1) / 2, 0, Z_INSERT))
    b = b - pill.extrude(0.61, scale_top=((L + 1.2) / L, (PILL_W + 1.2) / PILL_W)).translate(
        ((PILL_X0 + PILL_X1) / 2, 0, HANDLE_T - 0.6))
    b = b - stem_slot(HANDLE_T).translate((0, 0, Z_CHAN + CHAN_H - 1))
    # trou de suspension chanfreiné des deux côtés
    c = (HANG_CSK - HANG_D) / 2
    b = b - cyl(HANDLE_T + 2, HANG_D / 2, x=HANG_X, z=-1)
    b = b - cyl(c + 0.01, HANG_CSK / 2, HANG_D / 2, x=HANG_X, z=-0.01)
    b = b - cyl(c + 0.01, HANG_D / 2, HANG_CSK / 2, x=HANG_X, z=HANDLE_T - c)
    return b


def cover():
    """Couvercle du canal + bec qui rentre dans la bouteille."""
    c = cover_outline().extrude(COVER_T)
    r1, r0 = SPOUT_OD / 2, SPOUT_OD_TIP / 2
    sp = cyl(SPOUT_L - 0.8 + 0.01, r0, r1, z=-(SPOUT_L - 0.8)) + cyl(0.8, r0 - 0.8, r0, z=-SPOUT_L)
    rf = 1.5   # congé à la racine du bec
    root_pts = [(r1 - 0.01, 0.01), (r1 + rf, 0.01)] + arc(r1 + rf, -rf, rf, math.pi / 2, math.pi, 12)[1:] \
        + [(r1 - 0.01, -rf)]
    root = CrossSection([root_pts[::-1]]).revolve(128)
    c = c + sp + root
    c = c - cyl(SPOUT_L + COVER_T + 2, BORE_D / 2, z=-SPOUT_L - 1)
    c = c - cyl(0.6, BORE_D / 2 + 0.6, BORE_D / 2, z=-SPOUT_L - 0.01)   # chanfrein intérieur
    return c


def slide_plate(open_=False):
    p = rrect(PLATE_FRONT, PLATE_REAR, PLATE_W, 4.0).extrude(PLATE_T).translate((0, 0, Z_CHAN))
    h = KNOB_Z0 + SOCKET - (Z_CHAN + PLATE_T)
    p = p + Manifold.cube((STEM_S, STEM_S, h + 0.01)).translate(
        (KNOB_X - STEM_S / 2, -STEM_S / 2, Z_CHAN + PLATE_T - 0.01))
    return p.translate((TRAVEL if open_ else 0, 0, 0))


def knob(open_=False):
    r, h, ch = KNOB_D / 2, KNOB_H, 0.7
    prof = [(0, 0), (r - 0.3, 0), (r, 0.3), (r, h - ch)] + arc(r - ch, h - ch, ch, 0, math.pi / 2, 10)[1:] + [(0, h)]
    k = CrossSection([prof]).revolve(128)
    rd = KNOB_DISC_D / 2
    disc = CrossSection([[(0, h - 0.1), (rd, h - 0.1), (rd, h + 0.35), (rd - 0.25, h + 0.6), (0, h + 0.6)]]).revolve(128)
    groove = (CrossSection.circle(rd + 0.65, 96) - CrossSection.circle(rd + 0.1, 96)).extrude(0.6).translate(
        (0, 0, h - 0.4))
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

    bd, cv = body(), cover()
    plate, kn, sv, pill = slide_plate(), knob(), sieve(), pill_insert()

    printable = {
        "1_corps_entonnoir_manche": bd,                # debout, dessous à plat
        "2_couvercle_bec": cv.rotate((180, 0, 0)),     # face plate sur le plateau, bec en l'air
        "3_languette": plate,
        "4_bouton": kn,
        "5_tamis": sv,
        "6_insert_noir": pill,
    }
    for name, m in printable.items():
        t = to_tm(m)
        assert t.is_watertight, name
        b = t.bounds
        t.apply_translation((-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]))
        t.export(os.path.join(out, f"{name}.stl"))
        print(f"{name:28s} {t.extents.round(1)} mm  {t.volume / 1000:.1f} cm3")

    grey, black, steel = [112, 116, 122, 255], [22, 22, 24, 255], [160, 162, 165, 255]
    parts = [("corps", bd, grey), ("couvercle_bec", cv, grey), ("languette", plate, black),
             ("bouton", kn, black), ("tamis", sv, steel), ("insert_noir", pill, black)]
    scene = trimesh.Scene()
    for name, m, c in parts:
        scene.add_geometry(to_tm(m, c), node_name=name, geom_name=name)
    scene.export(os.path.join(root, "dozr_assemblage.glb"))
    scene.export(os.path.join(root, "dozr_assemblage.3mf"))
    to_tm(union([m for _, m, _ in parts])).export(os.path.join(root, "dozr_assemblage.stl"))

    print("interférence corps/couvercle :", round((bd ^ cv).volume(), 3), "mm3")
    fixed = bd + cv + pill + sv
    for open_ in (False, True):
        mov = slide_plate(open_) + knob(open_)
        print(f"interférence mécanisme ({'ouvert' if open_ else 'fermé'}) : {(mov ^ fixed).volume():.3f} mm3")
    bore = cyl(40, BORE_D / 2 - 0.05, z=-12)
    print("obstruction du passage — ouvert :", round((bore ^ slide_plate(True)).volume(), 2),
          "mm3 | fermé :", round((bore ^ slide_plate(False)).volume(), 1), "mm3")
    print("encombrement :", to_tm(bd + cv).extents.round(1), "mm")


if __name__ == "__main__":
    main()
