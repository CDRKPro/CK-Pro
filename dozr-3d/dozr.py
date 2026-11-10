"""
Dozr — doseur à poudre, forme calquée sur les vues de référence.

    pip install manifold3d trimesh numpy scipy networkx lxml
    python3 dozr.py   -> STL des pièces + assemblage (3MF / GLB / STL)

Unités : mm. Origine au centre du dessous de l'entonnoir, manche selon +X,
Z vers le haut. Le bec dépasse sous l'entonnoir (Z < 0).

Forme :
  - entonnoir en bol conique (Ø55 en haut, paroi verticale qui s'arrondit vers le tube), paroi
    cannelée (cannelures visibles dehors et dedans), lèvre arrondie ;
  - bec de 10 mm sous le fond, Ø20 : rentre dans un goulot standard
    (bouteilles d'eau / shakers, passage ~21,7 mm) ;
  - entonnoir + manche = UNE SEULE pièce, sans joint visible dessus ni
    sur les côtés, arêtes du manche réellement arrondies ;
  - pilule noire en creux, bouton rond noir en relief côté entonnoir,
    trou de suspension chanfreiné.

Clapet complet d'une seule pièce noire : languette qui passe entre l'entonnoir et
le tube + pilule visible qui coulisse dans le manche + bouton.
Bouton côté entonnoir = fermé ; bouton tiré vers le bout du manche = ouvert.
Le canal est fermé par dessous par le couvercle qui porte le bec
(seul joint du modèle, invisible une fois posé sur la bouteille).

Pièces : 1 corps (entonnoir + manche), 2 couvercle avec tube, 3 clapet complet.
"""
import math
import os

import numpy as np
from manifold3d import CrossSection, Manifold, JoinType, OpType, FillRule
import trimesh

RIBS = 48
SEG = RIBS * 14

# ----------------------------------------------------------------- entonnoir
CUP_R_TOP = 27.5        # rayon extérieur au bord (Ø55)
CUP_R_BOT = 13.0        # rayon extérieur en bas, juste au-dessus du tube (Ø26)
BOWL = 0.65             # 0 = cône droit, 1 = bol arrondi : « légèrement arrondi, conique »
CUP_H = 32.0
WALL = 2.0
LIP_R = 0.95            # arrondi de la lèvre
RIB_K = 1.0 / CUP_R_TOP  # profondeur des rainures (1 mm au bord)
RIM_BAND = 1.8          # bandeau lisse sous la lèvre
RIB_START = 15.5        # rayon à partir duquel la paroi est cannelée
FUNNEL_ANGLE = 50.0     # pente du fond (°) : la poudre descend direct vers le trou
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

# Clapet complet (une seule pièce noire) : languette + pilule visible + bouton
PILL_X0, PILL_X1, PILL_W = 37.7, 86.7, 17.3   # fenêtre en pilule dans le manche
KNOB_D, KNOB_H, KNOB_DISC_D = 16.2, 5.5, 9.0
CLR = 0.3
Z_CHAN, CHAN_H = 2.0, 2.4          # canal sous le fond de l'entonnoir et dans le manche
BASE_T = 2.0                       # semelle du clapet
TRAVEL = BORE_D + 4.0              # 18 mm : la languette dégage tout le tube
TONGUE_W = 16.0                    # languette qui passe entre l'entonnoir et le tube
TONGUE_FRONT = -(BORE_D / 2 + 2.5)  # avant de la languette, clapet fermé
WIDE_W = 21.4                      # semelle élargie sous la fenêtre (retient le clapet)
WIDE_X0 = PILL_X0 - 2.0
BOSS_X0 = PILL_X0 + CLR
BOSS_TOP = HANDLE_T - 1.0          # base du chapeau du bouton
BASE_REAR = PILL_X1 + 0.5          # la semelle reste visible dans la fenêtre : tout est noir
KNOB_X = BOSS_X0 + KNOB_D / 2 + 0.25   # bouton au bout côté entonnoir
NARROW_CH = (TONGUE_FRONT - CLR - 0.5, WIDE_X0 + TRAVEL + 1.0, TONGUE_W + 2 * CLR)
WIDE_CH = (WIDE_X0 - CLR - 0.5, BASE_REAR + TRAVEL + CLR + 0.5, WIDE_W + 2 * CLR)
COVER_T = Z_CHAN
COVER_DISC_R = 11.6
FUNNEL_Z0 = Z_CHAN + CHAN_H + 1.2   # bas du fond conique (1,2 mm au-dessus du clapet)

# Logo gravé en creux sur le manche
LOGO_TEXT, LOGO_H, LOGO_DEPTH = "DOZR", 6.0, 0.8
LOGO_X = 104.0          # centre du logo (entre la pilule et le trou)
LOGO_FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Inter-BlackItalic.otf")


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


def _r_bowl(z):
    u = min(max(z / CUP_H, 0.0), 1.0)
    ell = math.sqrt(max(1 - (1 - u) ** 2, 0.0))
    return CUP_R_BOT + (CUP_R_TOP - CUP_R_BOT) * (BOWL * ell + (1 - BOWL) * u)


def _z45():
    """Hauteur sous laquelle la pente du bol dépasserait 45° (surplomb à l'impression)."""
    z = 0.001
    while (_r_bowl(z + 0.01) - _r_bowl(z)) / 0.01 > 1.0:
        z += 0.01
    return z


Z45 = _z45()


def r_out(z):
    """Profil extérieur : paroi presque verticale en haut qui s'arrondit en se
    resserrant vers le tube (mélange quart d'ellipse / cône, cf. croquis).
    Les ~2 mm du bas sont un chanfrein à 45° : imprimable sans support."""
    if z < Z45:
        return _r_bowl(Z45) - (Z45 - z)
    return _r_bowl(z)


# ----------------------------------------------------------------- corps
def cup_section():
    """Demi-coupe (r, z) de l'entonnoir plein : bol conique, lèvre arrondie."""
    curve = [(r_out(CUP_H * (i / 80) ** 1.5), CUP_H * (i / 80) ** 1.5) for i in range(81)]
    outer = [(0, 0)] + curve + [(0, CUP_H)]
    outer_ext = [(0, 0)] + curve + [(CUP_R_TOP, CUP_H + 10), (0, CUP_H + 10)]

    cav = CrossSection([outer_ext]).offset(-WALL, JoinType.Round, circular_segments=96)
    r0, top = BORE_D / 2, CUP_H + 20
    cone = CrossSection([[(0, FUNNEL_Z0), (r0, FUNNEL_Z0),
                          (r0 + (top - FUNNEL_Z0) / math.tan(math.radians(FUNNEL_ANGLE)), top), (0, top)]])
    cav = cav ^ cone
    cav = cav.offset(-FLOOR_FILLET, JoinType.Round, circular_segments=64).offset(
        FLOOR_FILLET, JoinType.Round, circular_segments=64)
    cav = cav + CrossSection.square((r0, top - FUNNEL_Z0)).translate((0, FUNNEL_Z0))

    sec = CrossSection([outer]) - cav
    sec = sec.offset(-LIP_R, JoinType.Round, circular_segments=48).offset(LIP_R, JoinType.Round, circular_segments=48)
    sec = sec + CrossSection.square((2.5, FUNNEL_Z0))         # rétablit l'axe
    sec = sec ^ CrossSection.square((CUP_R_TOP + 5, CUP_H + 5))
    return sec, cav


def handle():
    """Manche plat à coins et arêtes réellement arrondis (enveloppe de 4 palets)."""
    rc, re, t = HANDLE_CORNER, EDGE_R, HANDLE_T
    prof = [(0, 0), (rc - re, 0)] + arc(rc - re, re, re, -math.pi / 2, 0, 12)[1:] + \
        arc(rc - re, t - re, re, 0, math.pi / 2, 12) + [(0, t)]
    puck = CrossSection([prof]).revolve(64)
    y = HANDLE_W / 2 - rc
    return Manifold.batch_hull([puck.translate((x, s * y, 0))
                                for x in (HANDLE_X0 + rc, HANDLE_END - rc) for s in (-1, 1)])


def channel_outline():
    x0, x1, w = NARROW_CH
    X0, X1, W = WIDE_CH
    return rrect(x0, x1, w, w / 2) + rrect(X0, X1, W, 2.0)


def cover_outline():
    return CrossSection.circle(COVER_DISC_R, 128) + channel_outline().offset(1.2, JoinType.Round)


def logo():
    """« DOZR® » gravé en creux, lisible depuis le bout du manche vers l'entonnoir."""
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(fname=LOGO_FONT)

    def polys(txt, size, dx=0.0, dy=0.0):
        """Contours des lettres, courbes de Bézier échantillonnées finement."""
        from matplotlib.path import Path
        tp = TextPath((0, 0), txt, size=size, prop=fp)
        contours, cur = [], []
        for seg, code in tp.iter_bezier():
            if code == Path.MOVETO:
                if len(cur) > 2:
                    contours.append(cur)
                cur = [tuple(seg.control_points[0])]
                continue
            if code == Path.CLOSEPOLY:
                continue
            n = 1 if code == Path.LINETO else 10
            for i in range(1, n + 1):
                cur.append(tuple(seg(i / n)))
        if len(cur) > 2:
            contours.append(cur)
        return [[(x + dx, y + dy) for x, y in c] for c in contours]

    main = polys(LOGO_TEXT, LOGO_H / 0.73)           # hauteur des capitales ≈ LOGO_H
    xs = [x for p in main for x, _ in p]
    reg = polys("®", LOGO_H * 0.55, dx=max(xs) + 0.4, dy=LOGO_H * 0.55)
    cs = CrossSection(main + reg, FillRule.EvenOdd)
    (x0, y0, x1, y1) = cs.bounds()
    cs = cs.translate((-(x0 + x1) / 2, -(y0 + y1) / 2)).rotate(180).translate((LOGO_X, 0))
    return cs.extrude(LOGO_DEPTH + 1).translate((0, 0, HANDLE_T - LOGO_DEPTH))


def body():
    sec, cav = cup_section()
    # le manche ne doit pas remplir le fond de l'entonnoir (zone non cannelée : forme exacte)
    hdl = handle() - cav.offset(0.05, JoinType.Round).revolve(SEG)
    b = flute(sec.revolve(SEG).refine_to_length(0.8)) + hdl
    # passage direct : fond conique -> trou Ø14 -> clapet (pas de grille)
    b = b - cyl(FUNNEL_Z0 - Z_CHAN + 0.5, BORE_D / 2, z=Z_CHAN)
    b = b - logo()
    # canal de la languette + logement du couvercle (par dessous)
    b = b - channel_outline().extrude(CHAN_H).translate((0, 0, Z_CHAN))
    b = b - cover_outline().offset(0.15, JoinType.Round).extrude(COVER_T + 1).translate((0, 0, -1))
    # fenêtre en pilule traversante (le clapet y coulisse), petit chanfrein en haut
    L = PILL_X1 - PILL_X0
    pill = rrect(-L / 2, L / 2, PILL_W, PILL_W / 2)
    b = b - pill.extrude(HANDLE_T).translate(((PILL_X0 + PILL_X1) / 2, 0, Z_CHAN + CHAN_H - 0.5))
    b = b - pill.extrude(0.61, scale_top=((L + 1.2) / L, (PILL_W + 1.2) / PILL_W)).translate(
        ((PILL_X0 + PILL_X1) / 2, 0, HANDLE_T - 0.6))
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
    rf = 1.0   # congé à la racine du tube
    root_pts = [(r1 - 0.01, 0.01), (r1 + rf, 0.01)] + arc(r1 + rf, -rf, rf, math.pi / 2, math.pi, 12)[1:] \
        + [(r1 - 0.01, -rf)]
    root = CrossSection([root_pts[::-1]]).revolve(128)
    c = c + sp + root
    c = c - cyl(SPOUT_L + COVER_T + 2, BORE_D / 2, z=-SPOUT_L - 1)
    c = c - cyl(0.6, BORE_D / 2 + 0.6, BORE_D / 2, z=-SPOUT_L - 0.01)   # chanfrein intérieur
    return c


def knob(drop=0.0):
    """Bouton ; drop = longueur dont le fût descend sous le chapeau."""
    r, h, ch = KNOB_D / 2, KNOB_H, 0.7
    prof = [(0, -drop), (r, -drop), (r, h - ch)] + arc(r - ch, h - ch, ch, 0, math.pi / 2, 10)[1:] + [(0, h)]
    k = CrossSection([prof]).revolve(128)
    rd = KNOB_DISC_D / 2
    disc = CrossSection([[(0, h - 0.1), (rd, h - 0.1), (rd, h + 0.35), (rd - 0.25, h + 0.6), (0, h + 0.6)]]).revolve(128)
    groove = (CrossSection.circle(rd + 0.65, 96) - CrossSection.circle(rd + 0.1, 96)).extrude(0.6).translate(
        (0, 0, h - 0.4))
    return k + disc - groove


def clapet(open_=False):
    """Clapet complet d'une seule pièce : languette (ferme le tube) + semelle
    noire visible dans la fenêtre du manche + bouton. Fermé : bouton côté entonnoir."""
    tongue = rrect(TONGUE_FRONT, WIDE_X0 + 1.0, TONGUE_W, TONGUE_W / 2)
    base = (tongue + rrect(WIDE_X0, BASE_REAR, WIDE_W, 2.0)).extrude(BASE_T).translate((0, 0, Z_CHAN))
    z1 = Z_CHAN + BASE_T
    # le bouton descend jusqu'à la semelle : seul le bouton rond dépasse dans la fenêtre
    k = knob(drop=BOSS_TOP - z1 + 0.01).translate((KNOB_X, 0, BOSS_TOP))
    return (base + k).translate((TRAVEL if open_ else 0, 0, 0))


# ----------------------------------------------------------------- export
def to_tm(m, color=None):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=True)
    if color is not None:
        t.visual.face_colors = color
    return t


def export_plates(root, printable):
    """Plateaux prêts à trancher (orientation d'impression, posés à Z=0, centrés sur
    un plateau 180 × 180 mm : rentre sur toutes les imprimantes courantes)."""
    grey, black = [112, 116, 122, 255], [22, 22, 24, 255]
    meshes = {}
    for name, m in printable.items():
        t = to_tm(m)
        b = t.bounds
        t.apply_translation((-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]))
        meshes[name] = t

    def plate(names, fname, bed=180.0, gap=8.0):
        rows = [meshes[n] for n in names]
        total = sum(t.extents[1] for t in rows) + gap * (len(rows) - 1)
        y = bed / 2 - total / 2
        sc = trimesh.Scene()
        for n, t in zip(names, rows):
            t = t.copy()
            t.apply_translation((bed / 2, y + t.extents[1] / 2, 0))
            t.visual.face_colors = black if "clapet" in n else grey
            sc.add_geometry(t, node_name=n, geom_name=n)
            y += t.extents[1] + gap
        sc.export(os.path.join(root, fname))

    plate(["1_corps_entonnoir_manche", "2_couvercle_bec"], "plateau_1_gris.3mf")
    plate(["3_clapet_complet"], "plateau_2_noir.3mf")
    plate(["1_corps_entonnoir_manche", "2_couvercle_bec", "3_clapet_complet"], "plateau_complet_multicolore.3mf")


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(root, "stl")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))

    bd, cv = body(), cover()
    cl = clapet()

    printable = {
        "1_corps_entonnoir_manche": bd,                # debout, dessous à plat
        "2_couvercle_bec": cv.rotate((180, 0, 0)),     # face plate sur le plateau, bec en l'air
        "3_clapet_complet": cl,                        # semelle à plat, bouton vers le haut
    }
    for name, m in printable.items():
        t = to_tm(m)
        assert t.is_watertight, name
        b = t.bounds
        t.apply_translation((-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]))
        t.export(os.path.join(out, f"{name}.stl"))
        print(f"{name:28s} {t.extents.round(1)} mm  {t.volume / 1000:.1f} cm3")

    grey, black, _ = [112, 116, 122, 255], [22, 22, 24, 255], [160, 162, 165, 255]
    parts = [("corps", bd, grey), ("couvercle_bec", cv, grey), ("clapet", cl, black)]
    scene = trimesh.Scene()
    for name, m, c in parts:
        scene.add_geometry(to_tm(m, c), node_name=name, geom_name=name)
    scene.export(os.path.join(root, "dozr_assemblage.glb"))
    scene.export(os.path.join(root, "dozr_assemblage.3mf"))
    to_tm(union([m for _, m, _ in parts])).export(os.path.join(root, "dozr_assemblage.stl"))

    export_plates(root, printable)

    print("interférence corps/couvercle :", round((bd ^ cv).volume(), 3), "mm3")
    fixed = bd + cv
    for open_ in (False, True):
        mov = clapet(open_)
        print(f"interférence mécanisme ({'ouvert' if open_ else 'fermé'}) : {(mov ^ fixed).volume():.3f} mm3")
    bore = cyl(40, BORE_D / 2 - 0.05, z=-12)
    print("obstruction du passage — ouvert :", round((bore ^ clapet(True)).volume(), 2),
          "mm3 | fermé :", round((bore ^ clapet(False)).volume(), 1), "mm3")
    print("encombrement :", to_tm(bd + cv).extents.round(1), "mm")


if __name__ == "__main__":
    main()
