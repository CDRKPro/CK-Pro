# Generates index.html and compositions/*.html for the CK Web Designer promo (v2, staged like the reference).
# Run: python3 build.py   (edit copy/timings here, then re-run)
import html, pathlib

ROOT = pathlib.Path(__file__).parent
W, H = 1080, 1920

SCENES = [  # id, start, duration
    ("s1", 0.0, 4.6),
    ("s2", 4.6, 2.8),
    ("s3", 7.4, 4.2),
    ("s4", 11.6, 5.4),
    ("s5", 17.0, 5.6),
    ("s6", 22.6, 3.8),
    ("s7", 26.4, 4.4),
    ("s8", 30.8, 4.4),
    ("s9", 35.2, 4.2),
    ("s10", 39.4, 5.0),
]
TOTAL = 44.4

GRAD = "linear-gradient(90deg, #38A8F5 0%, #8E8CF6 55%, #B98AF5 100%)"
BASE_CSS = """
@font-face { font-family: 'Syne'; src: url('assets/fonts/syne.woff2') format('woff2'); font-weight: 400 800; }
@font-face { font-family: 'Bricolage Grotesque'; src: url('assets/fonts/bricolage.woff2') format('woff2'); font-weight: 200 800; }
#root { position: absolute; inset: 0; background: #07080D; color: #fff; overflow: hidden;
  font-family: 'Bricolage Grotesque', sans-serif; }
#root .t { font-family: 'Syne', sans-serif; font-weight: 600; font-size: 72px; line-height: 1.14; letter-spacing: -0.01em; }
#root .lbl { font-family: 'Bricolage Grotesque'; font-weight: 600; font-size: 28px; letter-spacing: 0.32em; text-transform: uppercase; }
#root .g { background: GRAD; -webkit-background-clip: text; background-clip: text; color: transparent; }
#root .w { display: inline-block; white-space: pre; }
#root .grey { color: #8C8F9C; }
#root .abs { position: absolute; }
#root .center { left: 0; right: 0; text-align: center; }
#root .c2 { position: absolute; background: rgba(15, 17, 25, 0.94); border: 1px solid #232634; border-radius: 28px;
  box-shadow: 0 30px 70px rgba(0, 0, 0, 0.55); }
#root .tag { font-size: 28px; font-weight: 600; letter-spacing: 0.22em; color: #8C8F9C; text-transform: uppercase; }
#root .tile { border-radius: 16px; display: flex; align-items: center; justify-content: center; background: GRAD; }
#root .tile svg { width: 56%; height: 56%; }
#root .arc { position: absolute; width: 2600px; height: 2600px; border-radius: 50%; border: 2px solid rgba(120, 140, 246, 0.16); }
#root .arc.a1 { left: -1900px; top: 1330px; } #root .arc.a2 { left: 380px; top: 1330px; }
#root .cursor { position: absolute; left: 0; top: 0; width: 72px; height: 72px; z-index: 50; }
#root .vig { position: absolute; inset: 0; background: radial-gradient(ellipse 70% 55% at 50% 42%, rgba(7,8,13,0) 0%, rgba(7,8,13,0.75) 70%, #07080D 100%); }
""".replace("GRAD", GRAD)

ARCS = '<div class="arc a1"></div><div class="arc a2"></div>'
CURSOR = """<svg viewBox="0 0 24 24" width="72" height="72"><path d="M4 2.5 L4 19.5 L8.6 15.3 L11.6 22 L14.6 20.7 L11.7 14.1 L18 14.1 Z" fill="#fff" stroke="#000" stroke-width="1.3" stroke-linejoin="round"/></svg>"""

def ic(path, stroke="#000", sw=2):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'

P = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "doc": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    "cal": '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.8-4.5 4.2 1.1 6-5.4-3-5.4 3 1.1-6L3.2 9.4l6.1-.8z"/>',
    "pin": '<path d="M12 21s-7-7-7-12a7 7 0 0 1 14 0c0 5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5"/>',
    "home": '<path d="M4 11l8-7 8 7v9H4z"/><path d="M10 20v-5h4v5"/>',
    "spark": '<path d="M12 3v6M12 15v6M3 12h6M15 12h6"/>',
}

def words(text, cls="w"):
    ws = text.split(" ")
    return "".join(f'<span class="{cls}">{html.escape(w)}{" " if i < len(ws) - 1 else ""}</span>' for i, w in enumerate(ws))

def letters(text, cls="w g"):
    return "".join(f'<span class="{cls} lt">{html.escape(c)}</span>' for c in text)

def scene(sid, dur, css, body, js):
    return f"""<template>
  <style>{BASE_CSS}{css}</style>
  <div id="root" data-composition-id="{sid}" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
    {ARCS}
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    // word / line entrances: blur to sharp, no slide
    const W_IN = (sel, t, st = 0.07) => tl.fromTo(sel, {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.35, ease: "power4.out", stagger: st }}, t);
    // accent letters drop in one by one
    const L_IN = (sel, t) => tl.fromTo(sel, {{ opacity: 0, y: -34, filter: "blur(6px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out", stagger: 0.035 }}, t);
    const OUT = (sel, t, st = 0) => tl.to(sel, {{ opacity: 0, filter: "blur(10px)", duration: 0.25, ease: "power3.in", stagger: st }}, t);
    const CLICK = (cur, target, t) => {{
      tl.to(cur, {{ scale: 0.85, duration: 0.07, ease: "power2.in" }}, t); tl.to(cur, {{ scale: 1, duration: 0.1, ease: "power2.out" }}, t + 0.07);
      tl.to(target, {{ scale: 0.94, duration: 0.07, ease: "power2.in" }}, t); tl.to(target, {{ scale: 1, duration: 0.12, ease: "power2.out" }}, t + 0.07);
    }};
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""

# A field of the site's own pages lying in 3D perspective (the reference's backdrop)
FIELD_SHOTS = ["services", "method", "demos", "tarifs2", "faq", "form", "estim", "services2", "rdv", "contact", "tarifs3"]
FIELD_CSS = """
#{p}-field { position: absolute; inset: 0; perspective: 1700px; perspective-origin: 50% 35%; }
#{p}-plane { position: absolute; left: 50%; top: 50%; width: 3000px; height: 3600px; margin-left: -1500px; margin-top: -1800px;
  display: grid; grid-template-columns: repeat(7, 360px); gap: 70px 60px; }
#{p}-plane img { width: 360px; height: 627px; object-fit: cover; object-position: top; border-radius: 22px; opacity: OPA;
  border: 1px solid #262A38; }
"""
def field(p, opacity):
    imgs = "".join(f'<img src="assets/shots/{FIELD_SHOTS[(i * 5) % len(FIELD_SHOTS)]}.jpg" alt="">' for i in range(35))
    css = FIELD_CSS.replace("{p}", p).replace("OPA", str(opacity))
    return css, f'<div id="{p}-field" data-layout-ignore><div id="{p}-plane">{imgs}</div></div><div class="vig"></div>'

files = {}

# ---------------- S1: search ----------------
fcss, fhtml = field("s1", 0.38)
query = "couvreur près de chez moi"
chars = "".join(f'<span class="ch">{html.escape(c)}</span>' for c in query)
files["s1"] = scene("s1", 4.6, fcss + """
#s1-lbl { top: 300px; }
#s1-t1 { top: 360px; } #s1-t2 { top: 442px; } #s1-t3 { top: 524px; }
#s1-box { left: 80px; top: 700px; width: 920px; height: 116px; border-radius: 24px; }
#s1-box .ico { position: absolute; left: 34px; top: 36px; width: 44px; height: 44px; }
#s1-text { position: absolute; left: 100px; top: 30px; height: 56px; font-size: 40px; white-space: pre; display: flex; align-items: center; }
#s1-text .ch { opacity: 0; }
#s1-caret { display: inline-block; width: 3px; height: 46px; margin-left: 4px; background: #8E8CF6; }
#s1-btn { position: absolute; right: 18px; top: 18px; width: 80px; height: 80px; border-radius: 50%; }
#s1-drop { left: 80px; top: 832px; width: 920px; height: 272px; border-radius: 24px; }
#s1-drop .row { position: absolute; left: 20px; right: 20px; height: 76px; border-radius: 16px; display: flex; align-items: center;
  gap: 22px; padding-left: 22px; font-size: 34px; color: #8C8F9C; }
#s1-drop .row svg { width: 30px; height: 30px; flex: none; }
#s1-drop .row b { color: #fff; font-weight: 500; }
#s1-r0 { top: 20px; } #s1-r1 { top: 98px; } #s1-r2 { top: 176px; }
#s1-hl { position: absolute; left: 20px; right: 20px; top: 98px; height: 76px; border-radius: 16px; background: #1A1D2A; }
""", f"""
    {fhtml}
    <div id="s1-lbl" class="abs center lbl g">Aujourd'hui</div>
    <div id="s1-t1" class="abs center t">{words("Vos futurs clients")}</div>
    <div id="s1-t2" class="abs center t">{words("vous cherchent")}</div>
    <div id="s1-t3" class="abs center t">{letters("en ligne.")}</div>
    <div id="s1-box" class="c2">
      <div class="ico">{ic(P["search"], "#8C8F9C")}</div>
      <div id="s1-text">{chars}<span id="s1-caret"></span></div>
      <div id="s1-btn" class="tile">{ic(P["arrow"], "#000", 2.6)}</div>
    </div>
    <div id="s1-drop" class="c2">
      <div id="s1-hl"></div>
      <div id="s1-r0" class="row">{ic(P["search"], "#5D6070")}<span><b>couvreur</b> près de chez moi</span></div>
      <div id="s1-r1" class="row">{ic(P["search"], "#5D6070")}<span><b>couvreur</b> avis clients</span></div>
      <div id="s1-r2" class="row">{ic(P["search"], "#5D6070")}<span><b>couvreur</b> devis rapide</span></div>
    </div>
    <div id="s1-cursor" class="cursor">{CURSOR}</div>
""", """
    // the camera drifts slowly over the field of pages for the whole shot
    tl.fromTo("#s1-plane", { rotationX: 55, rotationZ: -32, x: 120, y: 200 }, { rotationX: 55, rotationZ: -32, x: -60, y: -160, duration: 4.6, ease: "none" }, 0);
    // frame 0: search box and label already on screen
    tl.fromTo("#s1-box", { scale: 0.96 }, { scale: 1, duration: 0.7, ease: "expo.out" }, 0);
    document.querySelectorAll("#s1-text .ch").forEach((c, i) => tl.set(c, { opacity: 1 }, 0.25 + i * 0.045));
    W_IN("#s1-t1 .w", 0.55, 0.08);
    W_IN("#s1-t2 .w", 1.05, 0.08);
    L_IN("#s1-t3 .lt", 1.5);
    tl.fromTo("#s1-drop", { opacity: 0, y: -16 }, { opacity: 1, y: 0, duration: 0.45, ease: "expo.out" }, 1.45);
    tl.fromTo("#s1-drop .row", { opacity: 0 }, { opacity: 1, duration: 0.3, stagger: 0.06 }, 1.5);
    tl.fromTo("#s1-cursor", { x: 1150, y: 1500 }, { x: 640, y: 960, duration: 0.8, ease: "expo.out" }, 1.9);
    tl.fromTo("#s1-hl", { opacity: 0 }, { opacity: 1, duration: 0.15 }, 2.5);
    tl.to("#s1-cursor", { x: 930, y: 760, duration: 0.55, ease: "expo.out" }, 2.95);
    CLICK("#s1-cursor", "#s1-btn", 3.6);
    tl.to("#s1-cursor", { opacity: 0, duration: 0.15 }, 3.8);
    // push through the search bar into the next scene
    OUT(["#s1-lbl", "#s1-t1", "#s1-t2", "#s1-t3"], 3.8, 0.03);
    tl.to(["#s1-box", "#s1-drop"], { scale: 1.25, opacity: 0, filter: "blur(14px)", duration: 0.4, ease: "power3.in", stagger: 0.03 }, 3.85);
    tl.to("#s1-field", { opacity: 0, duration: 0.4, ease: "power2.in" }, 3.9);
""")

# ---------------- S2 / S3 / S10: logo lockup ----------------
LOCK_CSS = """
#{p}-lock { position: absolute; left: 0; right: 0; top: 600px; height: 420px; transform-origin: 50% 50%; }
#{p}-lock .mk { position: absolute; left: 50%; margin-left: -170px; top: -62px; width: 340px; height: 340px; }
#{p}-lock .mk video, #{p}-lock .mk img { position: absolute; left: 0; top: 0; width: 340px; height: 340px; }
#{p}-lock .wm { position: absolute; left: 0; right: 0; top: 290px; text-align: center; font-size: 76px; font-weight: 600; white-space: nowrap; }
"""
def lockup(p, dur=None):
    lt = "".join(f'<span class="w l">{html.escape(c)}</span>' for c in "CK Web Designer")
    mark = (f'<video id="{p}-logo" class="clip" src="assets/logo-anime.webm" data-start="0" data-duration="{dur}" data-track-index="2" muted playsinline></video>'
            if dur else f'<img id="{p}-logo" src="assets/logo-still.png" alt="CK Web Designer">')
    return f'<div id="{p}-lock"><div class="mk">{mark}</div><div class="wm t">{lt}</div></div>'

files["s2"] = scene("s2", 2.8, LOCK_CSS.replace("{p}", "s2"), f"    {lockup('s2', 2.8)}", """
    tl.fromTo("#s2-lock .l", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power2.out", stagger: 0.035 }, 1.05);
    // carry across: the lockup shrinks up to become the next scene's header
    tl.to("#s2-lock", { scale: 0.3, y: -500, duration: 0.5, ease: "power2.inOut" }, 2.25);
""")

# ---------------- S3: vitrine digitale + phone rising in 3D ----------------
files["s3"] = scene("s3", 4.2, LOCK_CSS.replace("{p}", "s3") + """
#s3-lock { transform: translateY(-500px) scale(0.3); }
#s3-t1 { top: 410px; } #s3-t2 { top: 492px; } #s3-t3 { top: 596px; font-size: 38px; }
#s3-stage { position: absolute; inset: 0; perspective: 1500px; perspective-origin: 50% 20%; }
#s3-phone { position: absolute; left: 220px; top: 710px; width: 640px; height: 1300px; border-radius: 70px; background: #14161E;
  padding: 12px; border: 1px solid #2A2E3C; transform-origin: 50% 0%; }
#s3-screen { width: 100%; height: 100%; border-radius: 58px; overflow: hidden; background: #000; position: relative; }
#s3-shot { position: absolute; left: 0; top: 0; width: 616px; }
""", f"""
    {lockup("s3")}
    <div id="s3-t1" class="abs center t">{words("On crée")}</div>
    <div id="s3-t2" class="abs center t">{letters("la vitrine digitale")}</div>
    <div id="s3-t3" class="abs center grey">{words("de votre entreprise.")}</div>
    <div id="s3-stage" data-layout-allow-overflow><div id="s3-phone"><div id="s3-screen"><img id="s3-shot" src="assets/shots/hero.jpg" alt="ckwebdesigner.fr"></div></div></div>
""", """
    W_IN("#s3-t1 .w", 0.05, 0.08);
    L_IN("#s3-t2 .lt", 0.3);
    W_IN("#s3-t3 .w", 0.9, 0.06);
    // the phone rises out of the floor, tilted back, and stands up
    tl.fromTo("#s3-phone", { y: 900, rotationX: 58, scale: 0.92 }, { y: 0, rotationX: 0, scale: 1, duration: 1.2, ease: "expo.out" }, 0.55);
    // a real scroll on the site, with a smear while it moves
    tl.fromTo("#s3-shot", { y: 0, filter: "blur(0px)" }, { y: -420, duration: 1.0, ease: "power2.inOut" }, 2.2);
    tl.to("#s3-shot", { filter: "blur(5px)", duration: 0.5, ease: "power2.in" }, 2.2);
    tl.to("#s3-shot", { filter: "blur(0px)", duration: 0.5, ease: "power2.out" }, 2.7);
    tl.to("#s3-lock", { opacity: 0, duration: 0.2 }, 3.7);
    OUT(["#s3-t1", "#s3-t2", "#s3-t3"], 3.75, 0.03);
    tl.to("#s3-phone", { y: -300, scale: 1.35, opacity: 0, filter: "blur(16px)", duration: 0.45, ease: "power3.in" }, 3.75);
""")

# ---------------- S4: réalisations over the 3D field ----------------
fcss, fhtml = field("s4", 0.55)
feat = [("hero", "Accueil", "ckwebdesigner.fr"), ("timeline", "Méthode", "ckwebdesigner.fr"), ("projets", "Projets", "ckwebdesigner.fr")]
fcards = "".join(
    f'<div id="s4-f{i}" class="feat"><img src="assets/shots/{s}.jpg" alt=""></div>'
    f'<div id="s4-c{i}" class="cap"><i></i><b>{html.escape(a)}</b><span class="grey">{html.escape(b)}</span></div>'
    for i, (s, a, b) in enumerate(feat))
files["s4"] = scene("s4", 5.4, fcss + """
#s4-lbl { left: 90px; top: 220px; }
#s4-t1 { left: 90px; top: 280px; }
#s4-roll { left: 90px; top: 362px; width: 960px; height: 96px; overflow: hidden; }
#s4-roll .rw { position: absolute; left: 0; top: 0; white-space: nowrap; }
#s4-ul { left: 90px; top: 478px; width: 200px; height: 3px; background: #262A38; }
#s4-ul i { display: block; width: 70px; height: 3px; background: linear-gradient(90deg, #38A8F5, #B98AF5); }
#s4-stage { position: absolute; inset: 0; perspective: 1600px; }
#root .feat { position: absolute; left: 250px; top: 540px; width: 580px; height: 700px; border-radius: 26px; overflow: hidden;
  border: 1px solid #2E3242; box-shadow: 0 40px 90px rgba(0,0,0,0.7); background: #000; }
#root .feat img { width: 580px; display: block; }
#root .cap { position: absolute; left: 250px; top: 1262px; display: flex; align-items: center; gap: 16px; font-size: 28px; white-space: nowrap; }
#root .cap i { display: block; width: 12px; height: 12px; border-radius: 50%; background: linear-gradient(135deg, #38A8F5, #B98AF5); }
""", f"""
    {fhtml}
    <div id="s4-lbl" class="abs lbl g">Nos réalisations</div>
    <div id="s4-t1" class="abs t">{words("Un site")}</div>
    <div id="s4-roll" class="abs" data-layout-allow-overflow>
      <div id="s4-w0" class="rw t g">sur mesure.</div>
      <div id="s4-w1" class="rw t g">moderne.</div>
      <div id="s4-w2" class="rw t g">à votre image.</div>
    </div>
    <div id="s4-ul" class="abs"><i></i></div>
    <div id="s4-stage">{fcards}</div>
""", """
    tl.fromTo("#s4-plane", { rotationX: 52, rotationZ: -34, x: -200, y: 300 }, { rotationX: 52, rotationZ: -34, x: 160, y: -260, duration: 5.4, ease: "none" }, 0);
    tl.fromTo("#s4-field", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 0);
    W_IN("#s4-lbl", 0.1);
    W_IN("#s4-t1 .w", 0.2, 0.08);
    tl.fromTo("#s4-ul i", { x: -80 }, { x: 0, duration: 0.6, ease: "expo.out" }, 0.4);
    tl.set(["#s4-w1", "#s4-w2"], { yPercent: 110, opacity: 0 }, 0);
    tl.fromTo("#s4-w0", { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.5, ease: "expo.out" }, 0.4);
    // each word brings its own page: the old one whips out, the new one lands tilted and settles
    tl.set(["#s4-f1", "#s4-f2", "#s4-c1", "#s4-c2"], { opacity: 0 }, 0);
    tl.fromTo("#s4-f0", { x: 500, rotationY: -30, rotationX: 8, opacity: 0, filter: "blur(10px)" }, { x: 0, rotationY: -12, rotationX: 4, opacity: 1, filter: "blur(0px)", duration: 0.9, ease: "expo.out" }, 0.45);
    tl.to("#s4-f0", { rotationY: -6, duration: 1.0, ease: "power2.out" }, 1.35);
    W_IN("#s4-c0", 0.9);
    [[0, 1, 2.05], [1, 2, 3.65]].forEach(([a, b, t]) => {
      tl.to("#s4-w" + a, { yPercent: -110, opacity: 0, filter: "blur(6px)", duration: 0.3, ease: "power3.in" }, t);
      tl.fromTo("#s4-w" + b, { yPercent: 110, opacity: 0, filter: "blur(6px)" }, { yPercent: 0, opacity: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }, t + 0.15);
      tl.to("#s4-f" + a, { x: -700, rotationY: 25, opacity: 0, filter: "blur(14px)", duration: 0.35, ease: "power3.in" }, t);
      tl.to("#s4-c" + a, { opacity: 0, duration: 0.15 }, t);
      tl.fromTo("#s4-f" + b, { x: 600, rotationY: -32, rotationX: 8, opacity: 0, filter: "blur(14px)" }, { x: 0, rotationY: -12, rotationX: 4, opacity: 1, filter: "blur(0px)", duration: 0.7, ease: "expo.out" }, t + 0.2);
      tl.to("#s4-f" + b, { rotationY: -6, duration: 0.9, ease: "power2.out" }, t + 0.9);
      W_IN("#s4-c" + b, t + 0.45);
    });
    OUT(["#s4-lbl", "#s4-t1", "#s4-roll", "#s4-ul", "#s4-c2"], 5.0, 0.02);
    tl.to("#s4-f2", { scale: 0.85, opacity: 0, filter: "blur(14px)", duration: 0.35, ease: "power3.in" }, 5.0);
    tl.to("#s4-field", { opacity: 0, duration: 0.35 }, 5.0);
""")

# ---------------- S5: visible (cards + hub with orbiting nodes) ----------------
sats = [("mail", 200), ("pin", 255), ("star", 320), ("phone", 20), ("chart", 145)]
sat_html = "".join(f'<div class="sat" style="transform:rotate({a}deg) translateX(300px) rotate({-a}deg)"><div class="sb">{ic(P[k], "#9AA0B4", 1.8)}</div></div>' for k, a in sats)
roads = "".join(f'<path d="{d}"/>' for d in [
    "M-20 50 C200 80 380 30 960 110", "M-20 180 C300 150 600 210 960 170", "M160 -20 C190 90 140 180 210 300",
    "M540 -20 C500 110 580 200 560 300", "M740 -20 C780 130 720 220 800 300"])
files["s5"] = scene("s5", 5.6, """
#s5-t1 { left: 90px; top: 210px; font-size: 92px; }
#s5-roll { left: 90px; top: 326px; width: 960px; height: 70px; overflow: hidden; }
#s5-roll .rw { position: absolute; left: 0; top: 0; font-size: 52px; white-space: nowrap; }
#s5-a { left: 90px; top: 440px; width: 900px; height: 176px; }
#s5-b { left: 90px; top: 636px; width: 900px; height: 236px; }
#s5-c { left: 90px; top: 892px; width: 900px; height: 196px; }
#root .hd { position: absolute; left: 28px; top: 20px; display: flex; gap: 12px; align-items: center; }
#root .hd svg { width: 26px; height: 26px; }
#root .hq { position: absolute; right: 28px; top: 16px; padding: 4px 16px; border-radius: 12px; background: #1A1D2A; font-size: 28px; color: #8C8F9C; }
#s5-a .num { position: absolute; left: 28px; top: 84px; width: 60px; height: 60px; border-radius: 14px; font: 700 30px 'Syne'; color: #000; }
#s5-a .nm { position: absolute; left: 110px; top: 72px; font-size: 38px; font-weight: 600; }
#s5-a .rt { position: absolute; left: 110px; top: 122px; font-size: 28px; color: #8C8F9C; white-space: nowrap; }
#s5-a .rt .st { letter-spacing: 3px; }
#s5-map { position: absolute; left: 20px; right: 20px; top: 72px; bottom: 20px; border-radius: 18px; background: #E9EBF1; overflow: hidden; }
#s5-map svg.rd { position: absolute; inset: 0; }
#s5-map svg.rd path { fill: none; stroke: #C9CDD8; stroke-width: 10; stroke-linecap: round; }
#s5-pin { position: absolute; left: 400px; top: 34px; width: 46px; height: 60px; }
#s5-pl { position: absolute; left: 462px; top: 42px; padding: 6px 18px; border-radius: 12px; background: #0B0C12; color: #fff; font-size: 28px; font-weight: 600; white-space: nowrap; }
#s5-q { position: absolute; right: 28px; top: 70px; padding: 12px 22px; border-radius: 20px 20px 6px 20px; background: #1E2130; font-size: 30px; }
#s5-ans { position: absolute; left: 28px; top: 134px; font-size: 30px; color: #C9CBD6; white-space: nowrap; }
#s5-ans b { color: #fff; }
#s5-hub { position: absolute; left: 540px; top: 1250px; width: 0; height: 0; }
#s5-hub .ring { position: absolute; border-radius: 50%; border: 1px solid rgba(142, 140, 246, 0.28); }
#s5-orb { position: absolute; left: 0; top: 0; }
#root .sat { position: absolute; left: -32px; top: -32px; }
#root .sb { width: 64px; height: 64px; border-radius: 50%; background: #0F1119; border: 1px solid #262A38; display: flex; align-items: center; justify-content: center; }
#root .sb svg { width: 30px; height: 30px; }
#s5-node { position: absolute; left: -130px; top: -80px; width: 260px; height: 160px; border-radius: 30px; background: #0F1119; border: 1px solid #2E3242;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; }
#s5-node svg { width: 56px; height: 56px; }
#s5-node span { font-size: 28px; color: #C9CBD6; }
#s5-comet { position: absolute; left: 0; top: 0; }
#s5-comet i { position: absolute; left: 172px; top: -6px; width: 12px; height: 12px; border-radius: 50%; background: #8E8CF6; }
""", f"""
    <div id="s5-t1" class="abs t">{words("Visible")}</div>
    <div id="s5-roll" class="abs" data-layout-allow-overflow>
      <div id="s5-w0" class="rw t g">sur Google.</div>
      <div id="s5-w1" class="rw t g">sur Maps.</div>
      <div id="s5-w2" class="rw t g">et même dans ChatGPT.</div>
    </div>
    <div id="s5-hub" data-layout-ignore>
      <div class="ring" style="left:-180px;top:-180px;width:360px;height:360px"></div>
      <div class="ring" style="left:-300px;top:-300px;width:600px;height:600px"></div>
      <div id="s5-comet"><i></i></div>
      <div id="s5-orb">{sat_html}</div>
      <div id="s5-node">{ic(P["globe"], "#8E8CF6", 1.6)}<span>votre-entreprise.fr</span></div>
    </div>
    <div id="s5-a" class="c2">
      <div class="hd">{ic(P["search"], "#8C8F9C")}<span class="tag">Google</span></div><div class="hq">couvreur près de chez moi</div>
      <div class="num tile">1</div><div class="nm">Votre entreprise</div>
      <div class="rt"><span class="st g">★★★★★</span>  Ouvert · Appeler · Itinéraire</div>
    </div>
    <div id="s5-b" class="c2">
      <div class="hd">{ic(P["pin"], "#8C8F9C")}<span class="tag">Maps</span></div>
      <div id="s5-map"><svg class="rd" width="860" height="144">{roads}</svg>
        <svg id="s5-pin" viewBox="0 0 30 39"><defs><linearGradient id="s5pg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#38A8F5"/><stop offset="1" stop-color="#B98AF5"/></linearGradient></defs><path d="M15 38C15 38 2 23 2 14a13 13 0 0 1 26 0c0 9-13 24-13 24z" fill="url(#s5pg)"/><circle cx="15" cy="14" r="5" fill="#fff"/></svg>
        <div id="s5-pl">Votre entreprise · Ouvert</div></div>
    </div>
    <div id="s5-c" class="c2">
      <div class="hd">{ic(P["spark"], "#8C8F9C")}<span class="tag">ChatGPT</span></div>
      <div id="s5-q">Un bon couvreur près de chez moi ?</div>
      <div id="s5-ans">{words("Je vous recommande")} <b>{words("Votre entreprise.")}</b></div>
    </div>
""", """
    // the hub keeps orbiting slowly (about 4 degrees a second)
    tl.fromTo("#s5-orb", { rotation: 0 }, { rotation: 22, duration: 5.6, ease: "none" }, 0);
    tl.fromTo("#s5-orb .sb", { rotation: 0 }, { rotation: -22, duration: 5.6, ease: "none" }, 0);
    tl.fromTo("#s5-comet", { rotation: -40 }, { rotation: 320, duration: 5.6, ease: "none" }, 0);
    tl.fromTo("#s5-hub", { opacity: 0, scale: 0.85 }, { opacity: 1, scale: 1, duration: 0.9, ease: "expo.out" }, 0.1);
    tl.fromTo("#s5-t1 .w", { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "power4.out" }, 0.05);
    tl.set(["#s5-w1", "#s5-w2"], { yPercent: 110, opacity: 0 }, 0);
    tl.fromTo("#s5-w0", { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.45, ease: "expo.out" }, 0.35);
    [[0, 1, 1.85], [1, 2, 3.35]].forEach(([a, b, t]) => {
      tl.to("#s5-w" + a, { yPercent: -110, opacity: 0, filter: "blur(6px)", duration: 0.3, ease: "power3.in" }, t);
      tl.fromTo("#s5-w" + b, { yPercent: 110, opacity: 0, filter: "blur(6px)" }, { yPercent: 0, opacity: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }, t + 0.15);
    });
    // each card is sent out from the hub
    const CARD = (sel, t) => tl.fromTo(sel, { y: 380, scale: 0.7, opacity: 0, filter: "blur(12px)" }, { y: 0, scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.7, ease: "expo.out" }, t);
    CARD("#s5-a", 0.5);
    tl.fromTo("#s5-a .st", { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 0.5, ease: "power2.out" }, 0.95);
    CARD("#s5-b", 2.0);
    tl.fromTo("#s5-pin", { y: -70, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "expo.out" }, 2.4);
    tl.fromTo("#s5-pl", { opacity: 0, x: -14 }, { opacity: 1, x: 0, duration: 0.35, ease: "power4.out" }, 2.65);
    CARD("#s5-c", 3.3);
    tl.fromTo("#s5-q", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 3.5);
    tl.fromTo("#s5-ans .w", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, stagger: 0.07 }, 3.8);
    OUT(["#s5-t1", "#s5-roll", "#s5-hub"], 5.25);
    tl.to(["#s5-a", "#s5-b", "#s5-c"], { y: -60, opacity: 0, filter: "blur(10px)", duration: 0.3, ease: "power3.in", stagger: 0.04 }, 5.25);
""")

# ---------------- S6: visiteurs -> clients, live feed ----------------
feed = [
    ("doc", "Nouvelle demande de devis", "Site web · Formulaire", "à l'instant"),
    ("phone", "Appel entrant", "Depuis votre fiche Google", "1 min"),
    ("cal", "Rendez-vous réservé", "Jeudi · 10:00", "3 min"),
    ("star", "Nouvel avis 5 étoiles", "Google", "6 min"),
    ("doc", "Nouvelle demande de devis", "Recommandé par ChatGPT", "9 min"),
    ("pin", "Demande d'itinéraire", "Google Maps", "12 min"),
    ("chat", "Nouveau message", "Formulaire de contact", "15 min"),
    ("cal", "Rendez-vous réservé", "Lundi · 14:30", "18 min"),
    ("phone", "Appel entrant", "Depuis votre site", "21 min"),
    ("doc", "Nouvelle demande de devis", "Site web · Formulaire", "25 min"),
]
frows = "".join(
    f'<div class="fr c2" style="top:{i * 118}px"><div class="tile">{ic(P[k])}</div><div class="a">{html.escape(a)}</div>'
    f'<div class="b grey">{html.escape(b)}</div><div class="tm grey">{html.escape(t)}</div></div>' for i, (k, a, b, t) in enumerate(feed))
files["s6"] = scene("s6", 3.8, """
#s6-t1 { left: 90px; top: 210px; } #s6-t2 { left: 90px; top: 292px; } #s6-t3 { left: 90px; top: 374px; }
#s6-vis { position: relative; }
#s6-strike { position: absolute; left: 0; right: 14px; top: 56%; height: 5px; border-radius: 3px; background: linear-gradient(90deg, #38A8F5, #B98AF5); transform-origin: 0 50%; }
#s6-win { position: absolute; left: 90px; top: 520px; width: 900px; height: 810px; overflow: hidden;
  -webkit-mask-image: linear-gradient(180deg, transparent 0, #000 14%, #000 80%, transparent 100%); mask-image: linear-gradient(180deg, transparent 0, #000 14%, #000 80%, transparent 100%); }
#s6-col { position: absolute; left: 0; top: 0; width: 900px; }
#root .fr { left: 0; width: 900px; height: 102px; border-radius: 22px; }
#root .fr .tile { position: absolute; left: 20px; top: 21px; width: 60px; height: 60px; }
#root .fr .a { position: absolute; left: 104px; top: 14px; font-size: 32px; font-weight: 600; white-space: nowrap; }
#root .fr .b { position: absolute; left: 104px; top: 56px; font-size: 28px; white-space: nowrap; }
#root .fr .tm { position: absolute; right: 26px; top: 16px; font-size: 28px; }
""", f"""
    <div id="s6-t1" class="abs t"><span class="w">Vos </span><span class="w" id="s6-vis">visiteurs<span id="s6-strike"></span></span></div>
    <div id="s6-t2" class="abs t">{words("deviennent")}</div>
    <div id="s6-t3" class="abs t">{letters("des clients.")}</div>
    <div id="s6-win" data-layout-allow-overflow><div id="s6-col">{frows}</div></div>
""", """
    // the feed scrolls up continuously: new requests keep arriving
    tl.fromTo("#s6-col", { y: 760 }, { y: -380, duration: 3.8, ease: "none" }, 0);
    W_IN("#s6-t1 .w", 0.05, 0.08);
    W_IN("#s6-t2 .w", 0.4);
    tl.fromTo("#s6-strike", { scaleX: 0 }, { scaleX: 1, duration: 0.35, ease: "power3.inOut" }, 1.0);
    tl.to("#s6-vis", { color: "#4A4D5A", duration: 0.3 }, 1.1);
    L_IN("#s6-t3 .lt", 1.25);
    OUT(["#s6-t1", "#s6-t2", "#s6-t3", "#s6-win"], 3.45, 0.03);
""")

# ---------------- S7: votre interlocuteur (real quote + method) ----------------
steps = ["Échange", "Maquette", "Création", "En ligne"]
dots = "".join(f'<div id="s7-d{i}" class="sd" style="left:{i * 280}px"><i></i><span>{s}</span></div>' for i, s in enumerate(steps))
files["s7"] = scene("s7", 4.4, """
#s7-lbl { top: 300px; }
#s7-card { left: 90px; top: 380px; width: 900px; height: 420px; }
#s7-av { position: absolute; left: 36px; top: 36px; width: 96px; height: 96px; border-radius: 50%; padding: 3px; background: linear-gradient(135deg, #38A8F5, #B98AF5); }
#s7-av div { width: 90px; height: 90px; border-radius: 50%; background: #07080D; overflow: hidden; position: relative; }
#s7-av img { position: absolute; left: -9px; top: -6px; width: 108px; height: 108px; }
#s7-nm { position: absolute; left: 156px; top: 40px; font: 600 40px 'Syne'; }
#s7-rl { position: absolute; left: 156px; top: 92px; font-size: 28px; }
#s7-q { position: absolute; left: 36px; right: 36px; top: 168px; font-size: 42px; line-height: 1.32; }
#s7-big { left: 90px; top: 860px; font: 700 200px 'Syne'; line-height: 1; }
#s7-bl { left: 260px; top: 890px; font: 600 52px 'Syne'; line-height: 1.12; }
#s7-line { left: 140px; top: 1170px; width: 840px; height: 3px; background: #262A38; }
#s7-fill { position: absolute; left: 0; top: 0; width: 840px; height: 3px; background: linear-gradient(90deg, #38A8F5, #B98AF5); transform-origin: 0 50%; }
#root .sd { position: absolute; top: -9px; }
#root .sd i { display: block; width: 20px; height: 20px; margin-left: -10px; border-radius: 50%; background: #262A38; }
#root .sd span { position: absolute; left: 50%; top: 40px; transform: translateX(-50%); font-size: 30px; white-space: nowrap; color: #8C8F9C; }
""", f"""
    <div id="s7-lbl" class="abs center lbl g">Votre interlocuteur</div>
    <div id="s7-card" class="c2">
      <div id="s7-av"><div><img src="assets/logo-still.png" alt=""></div></div>
      <div id="s7-nm">Cédric</div><div id="s7-rl" class="grey">Fondateur · CK Web Designer</div>
      <div id="s7-q">« {words("Je crée des sites")} {words("sur mesure", "w g")} {words("pour les")} {words("artisans, les commerces", "w g")} {words("et les indépendants. »")}</div>
    </div>
    <div id="s7-big" class="abs g">1</div>
    <div id="s7-bl" class="abs">seul interlocuteur,<br><span class="grey">du début à la fin.</span></div>
    <div id="s7-line" class="abs"><div id="s7-fill"></div>{dots}</div>
""", """
    W_IN("#s7-lbl", 0.0);
    tl.fromTo("#s7-card", { y: 60, opacity: 0, filter: "blur(10px)" }, { y: 0, opacity: 1, filter: "blur(0px)", duration: 0.7, ease: "expo.out" }, 0.1);
    tl.fromTo("#s7-card", { borderColor: "#232634" }, { borderColor: "#5D5BC9", duration: 0.5 }, 0.6);
    tl.fromTo("#s7-q .w", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.22, stagger: 0.07 }, 0.6);
    tl.fromTo("#s7-big", { opacity: 0, y: 40, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, 1.6);
    W_IN("#s7-bl", 1.8);
    tl.fromTo("#s7-line", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 2.0);
    tl.fromTo("#s7-fill", { scaleX: 0 }, { scaleX: 1, duration: 1.4, ease: "power2.inOut" }, 2.1);
    [0, 1, 2, 3].forEach((i) => {
      tl.to(`#s7-d${i} i`, { background: "#8E8CF6", scale: 1.3, duration: 0.2 }, 2.1 + i * 0.45);
      tl.to(`#s7-d${i} span`, { color: "#ffffff", duration: 0.2 }, 2.1 + i * 0.45);
    });
    OUT(["#s7-lbl", "#s7-card", "#s7-big", "#s7-bl", "#s7-line"], 4.05, 0.03);
""")

# ---------------- S8: on s'occupe de tout (depth-of-field pass, then the grid assembles) ----------------
files["s8"] = scene("s8", 4.4, """
#s8-t1 { top: 220px; } #s8-t2 { top: 302px; }
#s8-grid { position: absolute; inset: 0; transform-origin: 50% 50%; }
#root .bx .hd2 { position: absolute; left: 28px; top: 24px; display: flex; gap: 16px; align-items: center; font: 600 34px 'Syne'; white-space: nowrap; }
#root .bx .hd2 .tile { width: 52px; height: 52px; border-radius: 14px; }
#root .bx .sm { position: absolute; font-size: 28px; color: #8C8F9C; }
#root .bx .big { position: absolute; font: 700 84px 'Syne'; line-height: 1; }
#s8-a { left: 90px; top: 470px; width: 900px; height: 300px; }
#s8-a .ck { position: absolute; left: 28px; font-size: 28px; color: #C9CBD6; }
#s8-a .ck b { color: #8E8CF6; }
#s8-a .th { position: absolute; right: 24px; top: 24px; width: 330px; height: 252px; border-radius: 16px; overflow: hidden; border: 1px solid #2E3242; }
#s8-a .th img { width: 330px; display: block; }
#s8-b { left: 90px; top: 790px; width: 440px; height: 250px; }
#s8-c { left: 550px; top: 790px; width: 440px; height: 250px; }
#s8-d { left: 90px; top: 1060px; width: 440px; height: 250px; }
#s8-e { left: 550px; top: 1060px; width: 440px; height: 250px; }
#s8-new { position: absolute; left: 28px; top: 120px; padding: 6px 18px; border-radius: 14px; background: linear-gradient(90deg, #38A8F5, #B98AF5); color: #000; font-size: 28px; font-weight: 600; letter-spacing: 0.1em; }
#s8-bars { position: absolute; left: 28px; right: 28px; bottom: 26px; height: 90px; display: flex; align-items: flex-end; gap: 14px; }
#s8-bars i { flex: 1; border-radius: 6px; background: #262A38; transform-origin: 50% 100%; }
#s8-bars i:last-child { background: linear-gradient(180deg, #B98AF5, #38A8F5); }
""", f"""
    <div id="s8-t1" class="abs center t">{words("On s'occupe")}</div>
    <div id="s8-t2" class="abs center t">{letters("de tout.")}</div>
    <div id="s8-grid">
      <div id="s8-a" class="c2 bx"><div class="hd2"><div class="tile">{ic(P["globe"])}</div>Site vitrine</div>
        <div class="sm" style="left:28px;top:100px">à partir de</div><div class="big g" style="left:28px;top:136px"><span id="s8-num">599</span> €</div>
        <div class="ck" style="top:236px"><b>✓</b> Hébergement et domaine 1 an</div>
        <div class="th"><img src="assets/shots/hero.jpg" alt=""></div></div>
      <div id="s8-b" class="c2 bx"><div class="hd2"><div class="tile">{ic(P["pin"])}</div>Référencement</div>
        <div class="sm" style="left:28px;top:104px">Google, Maps et IA</div>
        <div id="s8-bars"><i style="height:30%"></i><i style="height:42%"></i><i style="height:38%"></i><i style="height:60%"></i><i style="height:74%"></i><i style="height:100%"></i></div></div>
      <div id="s8-c" class="c2 bx"><div class="hd2"><div class="tile">{ic(P["check"])}</div>Maintenance</div>
        <div class="big g" style="left:28px;top:110px">49 €</div><div class="sm" style="left:28px;top:200px">par mois</div></div>
      <div id="s8-d" class="c2 bx"><div class="hd2"><div class="tile">{ic(P["star"])}</div>Identité visuelle</div>
        <div class="sm" style="left:28px;top:104px;width:390px;line-height:1.35">Logo, couleurs et style qui vous ressemblent</div></div>
      <div id="s8-e" class="c2 bx"><div class="hd2"><div class="tile">{ic(P["code"])}</div>Application</div>
        <div id="s8-new">NOUVEAU SERVICE</div><div class="sm" style="left:28px;top:180px">Pour gérer votre activité</div></div>
    </div>
""", """
    // pass 1: the camera glides close over the cards, out of focus except the one it passes
    const off = { "#s8-a": [-120, -90, 3], "#s8-b": [-160, 60, 6], "#s8-c": [140, 40, 0], "#s8-d": [-90, 140, 9], "#s8-e": [170, 120, 5] };
    Object.entries(off).forEach(([s, [x, y, b]]) => {
      tl.fromTo(s, { x: x, y: y, filter: `blur(${b}px)`, opacity: 0.85 }, { x: x * 0.8, y: y * 0.8, filter: `blur(${b}px)`, opacity: 0.85, duration: 1.7, ease: "none" }, 0);
      tl.to(s, { x: 0, y: 0, filter: "blur(0px)", opacity: 1, duration: 0.8, ease: "expo.out" }, 1.7);
    });
    tl.fromTo("#s8-grid", { scale: 1.75, x: -330, y: 120 }, { scale: 1.6, x: -230, y: 60, duration: 1.7, ease: "none" }, 0);
    // pass 2: pull back, everything lands in the grid
    tl.to("#s8-grid", { scale: 1, x: 0, y: 0, duration: 0.9, ease: "expo.out" }, 1.7);
    W_IN("#s8-t1 .w", 2.15, 0.08);
    L_IN("#s8-t2 .lt", 2.35);
    const n = { v: 0 }; const el = document.getElementById("s8-num");
    tl.fromTo(n, { v: 0 }, { v: 599, duration: 1.0, ease: "power2.out", onUpdate: () => { el.textContent = Math.round(n.v); } }, 1.9);
    tl.fromTo("#s8-bars i", { scaleY: 0.1 }, { scaleY: 1, duration: 0.6, ease: "expo.out", stagger: 0.06 }, 2.0);
    OUT(["#s8-t1", "#s8-t2"], 4.05);
    tl.to(".bx", { opacity: 0, scale: 0.92, filter: "blur(12px)", duration: 0.3, ease: "power3.in", stagger: 0.03 }, 4.05);
""")

# ---------------- S9: CTA ----------------
files["s9"] = scene("s9", 4.2, """
#s9-e1 { top: 300px; } #s9-e2 { top: 382px; }
#s9-stage { position: absolute; inset: 0; perspective: 1500px; perspective-origin: 50% 20%; }
#s9-phone { position: absolute; left: 260px; top: 560px; width: 560px; height: 1140px; border-radius: 62px; background: #14161E; padding: 11px; border: 1px solid #2A2E3C; transform-origin: 50% 0; }
#s9-phone div { width: 100%; height: 100%; border-radius: 52px; overflow: hidden; background: #000; }
#s9-phone img { width: 538px; display: block; }
#s9-r1 { top: 600px; } #s9-r2 { top: 682px; }
#s9-btn { position: absolute; left: 230px; top: 840px; width: 620px; height: 116px; border-radius: 58px; background: linear-gradient(90deg, #38A8F5, #8E8CF6 55%, #B98AF5);
  box-shadow: 0 20px 60px rgba(120, 130, 246, 0.35); color: #000; font-size: 36px; font-weight: 600; }
#s9-btn span { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; gap: 14px; }
#s9-btn svg { width: 40px; height: 40px; }
#s9-sub { top: 990px; font-size: 30px; }
#s9-cursor { z-index: 50; }
""", f"""
    <div id="s9-e1" class="abs center t">{words("Envie d'en faire")}</div>
    <div id="s9-e2" class="abs center t">{letters("autant ?")}</div>
    <div id="s9-stage" data-layout-allow-overflow><div id="s9-phone"><div><img src="assets/shots/projets.jpg" alt=""></div></div></div>
    <div id="s9-r1" class="abs center t">{words("Réservez votre")}</div>
    <div id="s9-r2" class="abs center t">{letters("rendez-vous.")}</div>
    <div id="s9-btn"><span id="s9-b1">Prendre rendez-vous {ic(P["arrow"], "#000", 2.4)}</span><span id="s9-b2">{ic(P["check"], "#000", 2.6)} Rendez-vous confirmé</span></div>
    <div id="s9-sub" class="abs center grey">{words("Vous choisissez l'heure, je vous appelle.")}</div>
    <div id="s9-cursor" class="cursor">{CURSOR}</div>
""", """
    W_IN("#s9-e1 .w", 0.05, 0.08);
    L_IN("#s9-e2 .lt", 0.3);
    tl.fromTo("#s9-phone", { y: 900, rotationX: 55 }, { y: 0, rotationX: 0, duration: 1.0, ease: "expo.out" }, 0.25);
    OUT(["#s9-e1", "#s9-e2"], 1.35, 0.03);
    tl.to("#s9-phone", { y: 700, rotationX: 40, opacity: 0, filter: "blur(10px)", duration: 0.4, ease: "power3.in" }, 1.35);
    W_IN("#s9-r1 .w", 1.6, 0.08);
    L_IN("#s9-r2 .lt", 1.8);
    tl.fromTo("#s9-btn", { opacity: 0, scale: 0.8, filter: "blur(10px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, 2.0);
    W_IN("#s9-sub .w", 2.2, 0.05);
    tl.set("#s9-b2", { opacity: 0 }, 0);
    tl.fromTo("#s9-cursor", { x: 1150, y: 1550 }, { x: 620, y: 900, duration: 0.6, ease: "expo.out" }, 2.25);
    CLICK("#s9-cursor", "#s9-btn", 3.0);
    tl.to("#s9-b1", { opacity: 0, duration: 0.12 }, 3.05);
    tl.to("#s9-b2", { opacity: 1, duration: 0.2 }, 3.1);
    tl.to("#s9-cursor", { opacity: 0, duration: 0.2 }, 3.45);
    OUT(["#s9-r1", "#s9-r2", "#s9-btn", "#s9-sub"], 3.95, 0.03);
""")

# ---------------- S10: end card ----------------
mq_items = ["Sites vitrines", "Boutiques en ligne", "Portfolios", "Applications", "Référencement", "Identité visuelle", "Refonte de site", "Logiciel"]
mq = "".join(f'<span>{html.escape(m)}</span><i></i>' for m in mq_items * 3)
files["s10"] = scene("s10", 5.0, LOCK_CSS.replace("{p}", "s10") + """
#s10-lock { top: 500px; }
#s10-tag { top: 900px; font-size: 44px; }
#s10-ct { top: 990px; }
#s10-mq { position: absolute; left: 0; top: 1240px; display: flex; align-items: center; gap: 28px; white-space: nowrap; font-size: 30px; color: #8C8F9C; }
#s10-mq i { display: block; width: 10px; height: 10px; border-radius: 50%; background: #8E8CF6; }
""", f"""
    {lockup("s10", 5.0)}
    <div id="s10-tag" class="abs center">{words("Un site qui vous")} <span class="w g" style="font-weight:600">ressemble.</span></div>
    <div id="s10-ct" class="abs center lbl grey">ckwebdesigner.fr · 06 34 36 61 70</div>
    <div id="s10-mq" data-layout-allow-overflow>{mq}</div>
""", """
    tl.fromTo("#s10-lock .l", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power2.out", stagger: 0.035 }, 1.05);
    W_IN("#s10-tag .w", 1.65, 0.08);
    W_IN("#s10-ct", 2.1);
    tl.fromTo("#s10-mq", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 1.6);
    tl.fromTo("#s10-mq", { x: 0 }, { x: -1600, duration: 5.0, ease: "none" }, 0);
""")

# ---------------- index ----------------
hosts = "\n".join(
    f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{st}" '
    f'data-duration="{d}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>'
    for sid, st, d in SCENES)
index = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #07080D; }}
      #bg {{ position: absolute; inset: 0; background: #07080D; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
      <div id="bg"></div>
{hosts}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(index)
(ROOT / "compositions").mkdir(exist_ok=True)
for sid, src in files.items():
    (ROOT / f"compositions/{sid}.html").write_text(src)
print("built", len(files), "scenes")
