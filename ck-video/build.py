# Generates index.html and compositions/*.html for the CK Web Designer promo.
# Run: python3 build.py   (edit copy/timings here, then re-run)
import re, html, pathlib

ROOT = pathlib.Path(__file__).parent
LOGO = (ROOT / "assets/logo.svg").read_text()
LOGO_INNER = re.search(r"<svg[^>]*>(.*)</svg>", LOGO, re.S).group(1)
LOGO_VB = re.search(r'viewBox="([^"]+)"', LOGO).group(1)

W, H = 1080, 1920

SCENES = [  # id, start, duration
    ("s1", 0.0, 3.9),
    ("s2", 3.9, 2.4),
    ("s3", 6.3, 4.7),
    ("s4", 11.0, 5.0),
    ("s5", 16.0, 6.2),
    ("s6", 22.2, 4.0),
    ("s7", 26.2, 4.6),
    ("s8", 30.8, 4.4),
    ("s9", 35.2, 4.8),
    ("s10", 40.0, 4.5),
]
TOTAL = 44.5

BASE_CSS = """
@font-face { font-family: 'Syne'; src: url('assets/fonts/syne.woff2') format('woff2'); font-weight: 400 800; }
@font-face { font-family: 'Bricolage Grotesque'; src: url('assets/fonts/bricolage.woff2') format('woff2'); font-weight: 200 800; }
#root { position: absolute; inset: 0; background: #000; color: #fff; overflow: hidden;
  font-family: 'Bricolage Grotesque', sans-serif; }
#root .syne { font-family: 'Syne', sans-serif; letter-spacing: -0.01em; line-height: 1.04; }
#root .q { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 60px; line-height: 1.12; }
#root .g { background: linear-gradient(90deg, #38A8F5 0%, #8E8CF6 55%, #B98AF5 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent; }
#root .w { display: inline-block; white-space: pre; }
#root .grey { color: #9A9AA0; }
#root .abs { position: absolute; }
#root .center { left: 0; right: 0; text-align: center; }
#root .card { position: absolute; background: #111113; border-radius: 32px; }
#root .card::before { content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 2px;
  background: linear-gradient(135deg, #38A8F5, #8E8CF6 55%, #B98AF5);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude; pointer-events: none; }
#root .tile { width: 110px; height: 110px; border-radius: 30px; display: flex; align-items: center;
  justify-content: center; background: linear-gradient(135deg, #38A8F5, #8E8CF6 55%, #B98AF5); }
#root .tile svg { width: 50%; height: 50%; }
#root .arc { position: absolute; left: 50%; width: 2200px; height: 2200px; margin-left: -1100px;
  border-radius: 50%; border: 2px solid rgba(142, 140, 246, 0.16); }
#root .cursor { position: absolute; width: 72px; height: 72px; z-index: 50; }
"""

CURSOR = """<svg viewBox="0 0 24 24" width="72" height="72"><path d="M4 2.5 L4 19.5 L8.6 15.3 L11.6 22 L14.6 20.7 L11.7 14.1 L18 14.1 Z" fill="#fff" stroke="#000" stroke-width="1.3" stroke-linejoin="round"/></svg>"""

ICONS = {
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linejoin="round"><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linejoin="round"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg>',
    "cal": '<svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linecap="round"><rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',
    "chat": '<svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4z"/></svg>',
    "pen": '<svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linejoin="round"><path d="M4 20l4-1L19 8l-3-3L5 16z"/></svg>',
    "code": '<svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 7l-5 5 5 5M16 7l5 5-5 5"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linejoin="round"><path d="M12 3l2.7 5.6 6.1.8-4.5 4.2 1.1 6-5.4-3-5.4 3 1.1-6L3.2 9.4l6.1-.8z"/></svg>',
}


def words(text, cls="w", prefix=None):
    out = []
    for i, w in enumerate(text.split(" ")):
        sep = " " if i < len(text.split(" ")) - 1 else ""
        ident = f' id="{prefix}{i}"' if prefix else ""
        out.append(f'<span class="{cls}"{ident}>{html.escape(w)}{sep}</span>')
    return "".join(out)


def logo_svg(ident, width):
    return f'<svg id="{ident}" viewBox="{LOGO_VB}" width="{width}" style="display:block;overflow:visible">{LOGO_INNER}</svg>'


def scene(sid, dur, css, body, js):
    return f"""<template>
  <style>{BASE_CSS}{css}</style>
  <div id="root" data-composition-id="{sid}" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const W_IN = (sel, t, st = 0.07) => tl.fromTo(sel, {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.35, ease: "power4.out", stagger: st }}, t);
    const OUT = (sel, t, st = 0) => tl.to(sel, {{ opacity: 0, filter: "blur(10px)", duration: 0.25, ease: "power3.in", stagger: st }}, t);
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


files = {}

# ---------------- S1: search ----------------
query = "couvreur près de chez moi"
chars = "".join(f'<span class="ch">{html.escape(c)}</span>' for c in query)
files["s1"] = scene("s1", 3.9, """
#s1-t1 { top: 300px; } #s1-t2 { top: 368px; }
#s1-t3 { top: 450px; font-size: 124px; font-weight: 800; }
#s1-box { left: 70px; top: 720px; width: 940px; height: 132px; border-radius: 40px; }
#s1-box .ico { position: absolute; left: 40px; top: 42px; width: 48px; height: 48px; color: #9A9AA0; }
#s1-text { position: absolute; left: 112px; top: 36px; font-size: 44px; white-space: pre; display: flex; align-items: center; height: 60px; }
#s1-text .ch { opacity: 0; }
#s1-caret { display: inline-block; width: 4px; height: 50px; margin-left: 4px; background: #8E8CF6; }
#s1-btn { position: absolute; right: 20px; top: 20px; width: 92px; height: 92px; border-radius: 28px;
  background: linear-gradient(135deg, #38A8F5, #8E8CF6 55%, #B98AF5); display: flex; align-items: center; justify-content: center; }
#s1-btn svg { width: 46px; height: 46px; }
#s1-drop { left: 70px; top: 872px; width: 940px; height: 300px; border-radius: 32px; transform-origin: 50% 0; }
#s1-drop .row { position: absolute; left: 30px; right: 30px; height: 84px; border-radius: 20px; display: flex; align-items: center;
  gap: 26px; padding-left: 20px; font-size: 38px; color: #9A9AA0; }
#s1-drop .row svg { width: 34px; height: 34px; color: #6A6A70; flex: none; }
#s1-drop .row b { color: #fff; font-weight: 500; }
#s1-r0 { top: 24px; } #s1-r1 { top: 108px; } #s1-r2 { top: 192px; }
#s1-hl { position: absolute; left: 30px; right: 30px; top: 24px; height: 84px; border-radius: 20px; background: #1E1E25; }
""", f"""
    <div class="arc" style="top:1500px"></div>
    <div id="s1-t1" class="abs center q">{words("Vos futurs clients", prefix="s1-a")}</div>
    <div id="s1-t2" class="abs center q">{words("vous cherchent", prefix="s1-b")}</div>
    <div id="s1-t3" class="abs center syne">{words("en ligne.", cls="w g", prefix="s1-c")}</div>
    <div id="s1-box" class="card">
      <div class="ico">{ICONS["search"]}</div>
      <div id="s1-text">{chars}<span id="s1-caret"></span></div>
      <div id="s1-btn">{ICONS["arrow"]}</div>
    </div>
    <div id="s1-drop" class="card">
      <div id="s1-hl"></div>
      <div id="s1-r0" class="row">{ICONS["search"]}<span><b>couvreur près de chez moi</b></span></div>
      <div id="s1-r1" class="row">{ICONS["search"]}<span>couvreur <b>avis clients</b></span></div>
      <div id="s1-r2" class="row">{ICONS["search"]}<span>couvreur <b>devis gratuit</b></span></div>
    </div>
    <div id="s1-cursor" class="cursor" style="left:0;top:0">{CURSOR}</div>
""", """
    // hook: first line + empty search box are on screen at frame 0
    tl.fromTo("#s1-box", { y: 30 }, { y: 0, duration: 0.6, ease: "expo.out" }, 0);
    const ch = document.querySelectorAll("#s1-text .ch");
    ch.forEach((c, i) => tl.set(c, { opacity: 1 }, 0.3 + i * 0.045));
    W_IN("#s1-t2 .w", 0.75, 0.08);
    tl.fromTo("#s1-t3 .w", { opacity: 0, filter: "blur(10px)", scale: 1.06 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.5, ease: "expo.out", stagger: 0.09 }, 1.35);
    tl.fromTo("#s1-drop", { opacity: 0, scaleY: 0.6 }, { opacity: 1, scaleY: 1, duration: 0.45, ease: "expo.out" }, 1.55);
    tl.fromTo("#s1-drop .row", { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.4, ease: "power4.out", stagger: 0.06 }, 1.62);
    tl.fromTo("#s1-hl", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 1.62);
    // cursor flies to the search button and clicks it
    tl.fromTo("#s1-cursor", { x: 1150, y: 1500 }, { x: 930, y: 790, duration: 0.85, ease: "expo.out" }, 2.05);
    tl.to("#s1-cursor", { scale: 0.85, duration: 0.08, ease: "power2.in" }, 3.0);
    tl.to("#s1-cursor", { scale: 1, duration: 0.12, ease: "power2.out" }, 3.08);
    tl.to("#s1-btn", { scale: 0.88, duration: 0.08, ease: "power2.in" }, 3.0);
    tl.to("#s1-btn", { scale: 1, duration: 0.12, ease: "power2.out" }, 3.08);
    // blur swap out
    OUT(["#s1-t1", "#s1-t2", "#s1-t3"], 3.3, 0.04);
    tl.to(["#s1-box", "#s1-drop"], { opacity: 0, scale: 0.94, filter: "blur(12px)", duration: 0.3, ease: "power3.in", stagger: 0.04 }, 3.35);
    tl.to("#s1-cursor", { opacity: 0, duration: 0.2 }, 3.35);
""")

# ---------------- S2: logo reveal ----------------
LOCK_CSS = """
#{p}-lock { position: absolute; left: 0; right: 0; top: 560px; height: 500px; transform-origin: 50% 50%; }
#{p}-lock .mk { position: absolute; left: 50%; margin-left: -160px; top: 0; }
#{p}-lock .wm { position: absolute; left: 0; right: 0; top: 330px; text-align: center; font-size: 68px; font-weight: 800; white-space: nowrap; }
"""
def lockup(p):
    letters = "".join(f'<span class="w l">{html.escape(c)}</span>' for c in "CK Web Designer")
    return f"""<div id="{p}-lock"><div class="mk">{logo_svg(p + "-logo", 320)}</div><div class="wm syne">{letters}</div></div>"""

files["s2"] = scene("s2", 2.4, LOCK_CSS.replace("{p}","s2"), f"""
    <div class="arc" style="top:1500px"></div>
    {lockup("s2")}
""", """
    tl.fromTo("#s2-logo .dash", { x: -260, opacity: 0 }, { x: 0, opacity: 1, duration: 0.55, ease: "expo.out", stagger: 0.05 }, 0.05);
    tl.fromTo("#s2-logo .mark", { x: -70, opacity: 0 }, { x: 0, opacity: 1, duration: 0.6, ease: "expo.out", stagger: 0.08 }, 0.15);
    tl.fromTo("#s2-lock .l", { opacity: 0.0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power2.out", stagger: 0.035 }, 0.55);
    // carry across: lockup shrinks to the top where the next scene keeps it
    tl.to("#s2-lock", { scale: 0.3, y: -530, duration: 0.5, ease: "power2.inOut" }, 1.85);
""")

# ---------------- S3: vitrine digitale + phone ----------------
files["s3"] = scene("s3", 4.7, LOCK_CSS.replace("{p}","s3") + """
#s3-lock { transform: translateY(-530px) scale(0.3); }
#s3-t1 { top: 410px; } #s3-t2 { top: 480px; font-size: 112px; font-weight: 800; } #s3-t3 { top: 595px; font-size: 112px; font-weight: 800; }
#s3-t4 { top: 730px; font-size: 42px; }
#s3-phone { position: absolute; left: 180px; top: 840px; width: 720px; height: 1300px; border-radius: 76px; background: #1A1A1F;
  padding: 12px; box-shadow: 0 0 0 2px #2A2A31; }
#s3-screen { width: 100%; height: 100%; border-radius: 64px; overflow: hidden; background: #000; position: relative; }
#s3-shot { position: absolute; left: 0; top: 0; width: 696px; }
#s3-notch { position: absolute; left: 50%; top: 18px; width: 170px; height: 46px; margin-left: -85px; border-radius: 30px; background: #000; z-index: 2; }
""", f"""
    <div class="arc" style="top:1500px"></div>
    {lockup("s3")}
    <div id="s3-t1" class="abs center q">{words("On crée", prefix="s3-a")}</div>
    <div id="s3-t2" class="abs center syne">{words("la vitrine", cls="w g")}</div>
    <div id="s3-t3" class="abs center syne">{words("digitale", cls="w g")}</div>
    <div id="s3-t4" class="abs center grey">{words("de votre entreprise.")}</div>
    <div id="s3-phone" data-layout-allow-overflow><div id="s3-notch"></div><div id="s3-screen"><img id="s3-shot" src="assets/site-hero.png" alt="ckwebdesigner.fr"></div></div>
""", """
    W_IN("#s3-t1 .w", 0.1, 0.08);
    tl.fromTo(["#s3-t2 .w", "#s3-t3 .w"], { opacity: 0, filter: "blur(10px)", scale: 1.05 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.5, ease: "expo.out", stagger: 0.1 }, 0.35);
    W_IN("#s3-t4 .w", 0.75, 0.06);
    tl.fromTo("#s3-phone", { y: 1000 }, { y: 0, duration: 0.9, ease: "expo.out" }, 0.8);
    tl.fromTo("#s3-shot", { y: 0 }, { y: -170, duration: 1.4, ease: "power2.inOut" }, 2.2);
    tl.to("#s3-lock", { opacity: 0, duration: 0.25 }, 4.1);
    OUT(["#s3-t1", "#s3-t2", "#s3-t3", "#s3-t4"], 4.15, 0.03);
    tl.to("#s3-phone", { scale: 1.3, y: -260, opacity: 0, filter: "blur(14px)", duration: 0.45, ease: "power3.in" }, 4.2);
""")

# ---------------- S4: réalisations ----------------
projects = [
    ("BM Toiture", None), ("Jung Peinture Décors", None), ("StyleTech", None),
    ("CB Alsace Toiture", "SITE + APPLI + COMPTA"), ("Design &amp; Renov", "SITE + APPLI + COMPTA"),
    ("Gestera Pro", "SITE + LOGICIEL"),
]
rows, top = [], 520
for i, (name, tag) in enumerate(projects):
    h = 140 if tag else 96
    chip = f'<span class="chip">{tag}</span>' if tag else ""
    rows.append(f'<div id="s4-p{i}" class="card prow" style="top:{top}px;height:{h}px"><div class="nm syne">{name}</div>{chip}<div class="plus"><span>+</span></div></div>')
    top += h + 16
files["s4"] = scene("s4", 5.0, """
#s4-pill { left: 96px; top: 210px; display: flex; align-items: center; gap: 22px; font-size: 40px; }
#s4-pill .n { padding: 6px 26px; border-radius: 30px; background: linear-gradient(90deg, #38A8F5, #B98AF5); color: #000; font-weight: 800; font-family: 'Syne'; font-size: 32px; }
#s4-pill .s { font-family: 'Syne'; font-weight: 700; }
#s4-t1 { left: 96px; top: 300px; }
#s4-roll { left: 96px; top: 372px; height: 104px; width: 950px; overflow: hidden; }
#s4-roll .rw { position: absolute; left: 0; top: 0; font-size: 84px; font-weight: 800; white-space: nowrap; }
#root .prow { left: 70px; width: 940px; }
#root .prow .nm { position: absolute; left: 44px; top: 26px; font-size: 38px; font-weight: 700; }
#root .prow .chip { position: absolute; left: 44px; top: 82px; padding: 4px 18px; border-radius: 20px; background: #fff; color: #000;
  font-size: 28px; font-weight: 600; letter-spacing: 0.1em; }
#root .prow .plus { position: absolute; right: 30px; top: 50%; margin-top: -32px; width: 64px; height: 64px; border-radius: 50%;
  border: 2px solid #3A3A42; display: flex; align-items: center; justify-content: center; font-size: 40px; }
#root .prow .plus span { display: block; line-height: 1; margin-top: -4px; }
""", f"""
    <div class="arc" style="top:1560px"></div>
    <div id="s4-pill" class="abs"><span class="n">01</span><span class="s">Sites réalisés</span></div>
    <div id="s4-t1" class="abs q">{words("Un site")}</div>
    <div id="s4-roll" class="abs" data-layout-allow-overflow>
      <div id="s4-w0" class="rw syne g">sur mesure.</div>
      <div id="s4-w1" class="rw syne g">moderne.</div>
      <div id="s4-w2" class="rw syne g">à votre image.</div>
    </div>
    {"".join(rows)}
""", """
    W_IN("#s4-pill", 0.0);
    W_IN("#s4-t1 .w", 0.15, 0.08);
    tl.fromTo("#s4-w0", { yPercent: 100, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.45, ease: "expo.out" }, 0.35);
    tl.set(["#s4-w1", "#s4-w2"], { yPercent: 110, opacity: 0 }, 0);
    // slot roll
    [[0, 1, 1.9], [1, 2, 3.3]].forEach(([a, b, t]) => {
      tl.to("#s4-w" + a, { yPercent: -110, opacity: 0, filter: "blur(6px)", duration: 0.3, ease: "power3.in" }, t);
      tl.fromTo("#s4-w" + b, { yPercent: 110, opacity: 0, filter: "blur(6px)" }, { yPercent: 0, opacity: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }, t + 0.15);
    });
    tl.fromTo(".prow", { x: 180, opacity: 0, filter: "blur(8px)" }, { x: 0, opacity: 1, filter: "blur(0px)", duration: 0.6, ease: "expo.out", stagger: 0.07 }, 0.5);
    // a project opens on each beat
    [[0, 1.4], [3, 2.6], [5, 3.8]].forEach(([i, t]) => {
      tl.to(`#s4-p${i}`, { backgroundColor: "#1C1C24", scale: 1.025, duration: 0.3, ease: "power2.out" }, t);
      tl.to(`#s4-p${i} .plus span`, { rotation: 45, duration: 0.3, ease: "power2.out" }, t);
      tl.to(`#s4-p${i}`, { backgroundColor: "#111113", scale: 1, duration: 0.3, ease: "power2.inOut" }, t + 0.9);
      tl.to(`#s4-p${i} .plus span`, { rotation: 0, duration: 0.3, ease: "power2.inOut" }, t + 0.9);
    });
    tl.to(".prow", { y: -140, opacity: 0, filter: "blur(10px)", duration: 0.3, ease: "power3.in", stagger: 0.03 }, 4.55);
    OUT(["#s4-pill", "#s4-t1", "#s4-roll"], 4.55);
""")

# ---------------- S5: visible ----------------
roads = "".join([
    '<path d="M-20 60 C200 90 380 40 980 120" />', '<path d="M-20 200 C300 170 600 230 980 190" />',
    '<path d="M180 -20 C210 100 160 200 230 320" />', '<path d="M560 -20 C520 120 600 220 580 320" />',
    '<path d="M760 -20 C800 140 740 240 820 320" />', '<path d="M-20 270 C200 250 400 290 600 260" />',
])
files["s5"] = scene("s5", 6.2, """
#s5-t1 { left: 96px; top: 200px; font-size: 124px; font-weight: 800; }
#s5-roll { left: 96px; top: 350px; height: 76px; width: 960px; overflow: hidden; }
#s5-roll .rw { position: absolute; left: 0; top: 0; font-size: 56px; font-weight: 700; white-space: nowrap; }
#s5-a { left: 70px; top: 470px; width: 940px; height: 196px; }
#s5-a .fav { position: absolute; left: 40px; top: 40px; width: 64px; height: 64px; border-radius: 50%;
  background: linear-gradient(135deg, #38A8F5, #B98AF5); color: #000; font: 800 32px 'Syne'; display: flex; align-items: center; justify-content: center; }
#s5-a .url { position: absolute; left: 128px; top: 34px; font-size: 28px; color: #9A9AA0; }
#s5-a .ttl { position: absolute; left: 128px; top: 70px; font-size: 38px; font-weight: 700; font-family: 'Syne'; }
#s5-a .rt { position: absolute; left: 128px; top: 126px; font-size: 30px; color: #9A9AA0; display: flex; gap: 14px; align-items: center; }
#s5-a .stars { letter-spacing: 4px; font-size: 32px; }
#s5-a .open { color: #4ADE80; }
#s5-b { left: 70px; top: 690px; width: 940px; height: 290px; overflow: hidden; }
#s5-map { position: absolute; inset: 2px; border-radius: 30px; background: #15151A; overflow: hidden; }
#s5-map svg path { fill: none; stroke: #2B2B33; stroke-width: 14; stroke-linecap: round; }
#s5-pin { position: absolute; left: 440px; top: 70px; width: 60px; height: 78px; }
#s5-plabel { position: absolute; left: 520px; top: 84px; padding: 8px 22px; border-radius: 16px; background: #fff; color: #000; font-size: 30px; font-weight: 600; }
#s5-c { left: 70px; top: 1004px; width: 940px; height: 316px; }
#s5-q { position: absolute; right: 36px; top: 36px; padding: 18px 28px; border-radius: 26px 26px 6px 26px; background: #24242C; font-size: 32px; }
#s5-ai { position: absolute; left: 36px; top: 140px; width: 64px; height: 64px; border-radius: 20px; background: linear-gradient(135deg, #38A8F5, #B98AF5);
  display: flex; align-items: center; justify-content: center; }
#s5-ai svg { width: 34px; height: 34px; }
#s5-dots { position: absolute; left: 124px; top: 160px; display: flex; gap: 10px; }
#s5-dots i { display: block; width: 14px; height: 14px; border-radius: 50%; background: #6A6A72; }
#s5-ans { position: absolute; left: 124px; top: 138px; width: 780px; font-size: 32px; line-height: 1.4; color: #D8D8DE; }
#s5-ans b { color: #fff; font-weight: 700; }
""", f"""
    <div class="arc" style="top:1560px"></div>
    <div id="s5-t1" class="abs syne">{words("Visible")}</div>
    <div id="s5-roll" class="abs" data-layout-allow-overflow>
      <div id="s5-w0" class="rw syne g">sur Google.</div>
      <div id="s5-w1" class="rw syne g">sur Maps.</div>
      <div id="s5-w2" class="rw syne g">et même dans ChatGPT.</div>
    </div>
    <div id="s5-a" class="card">
      <div class="fav">V</div><div class="url">votre-entreprise.fr</div>
      <div class="ttl">Votre entreprise · Couvreur</div>
      <div class="rt"><span class="stars g">★★★★★</span><span>5,0</span><span>·</span><span class="open">Ouvert</span></div>
    </div>
    <div id="s5-b" class="card">
      <div id="s5-map"><svg width="936" height="286">{roads}</svg>
        <svg id="s5-pin" viewBox="0 0 30 39"><defs><linearGradient id="s5pg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#38A8F5"/><stop offset="1" stop-color="#B98AF5"/></linearGradient></defs><path d="M15 38C15 38 2 23 2 14a13 13 0 0 1 26 0c0 9-13 24-13 24z" fill="url(#s5pg)"/><circle cx="15" cy="14" r="5" fill="#000"/></svg>
        <div id="s5-plabel">Votre entreprise</div>
      </div>
    </div>
    <div id="s5-c" class="card">
      <div id="s5-q">Un bon couvreur près de chez moi ?</div>
      <div id="s5-ai">{ICONS["star"]}</div>
      <div id="s5-dots"><i></i><i></i><i></i></div>
      <div id="s5-ans">{words("Je vous recommande")} <b>{words("Votre entreprise.")}</b></div>
    </div>
""", """
    tl.fromTo("#s5-t1 .w", { opacity: 0, filter: "blur(10px)", scale: 1.06 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.5, ease: "expo.out" }, 0.05);
    tl.set(["#s5-w1", "#s5-w2"], { yPercent: 110, opacity: 0 }, 0);
    tl.fromTo("#s5-w0", { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.45, ease: "expo.out" }, 0.3);
    [[0, 1, 1.8], [1, 2, 3.4]].forEach(([a, b, t]) => {
      tl.to("#s5-w" + a, { yPercent: -110, opacity: 0, filter: "blur(6px)", duration: 0.3, ease: "power3.in" }, t);
      tl.fromTo("#s5-w" + b, { yPercent: 110, opacity: 0, filter: "blur(6px)" }, { yPercent: 0, opacity: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }, t + 0.15);
    });
    const CARD_IN = (sel, t) => tl.fromTo(sel, { y: 60, opacity: 0, filter: "blur(10px)" }, { y: 0, opacity: 1, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, t);
    CARD_IN("#s5-a", 0.45);
    tl.fromTo("#s5-a .stars", { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 0.5, ease: "power2.out" }, 0.9);
    CARD_IN("#s5-b", 1.95);
    tl.fromTo("#s5-pin", { y: -120, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "expo.out" }, 2.3);
    tl.fromTo("#s5-plabel", { x: -20, opacity: 0 }, { x: 0, opacity: 1, duration: 0.4, ease: "power4.out" }, 2.6);
    CARD_IN("#s5-c", 3.4);
    tl.fromTo("#s5-q", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "power4.out" }, 3.55);
    tl.fromTo(["#s5-ai", "#s5-dots"], { opacity: 0 }, { opacity: 1, duration: 0.2 }, 3.85);
    tl.fromTo("#s5-dots i", { y: 0 }, { y: -8, duration: 0.15, ease: "power2.out", stagger: 0.08, yoyo: true, repeat: 1 }, 3.85);
    tl.to("#s5-dots", { opacity: 0, duration: 0.1 }, 4.2);
    tl.fromTo("#s5-ans .w", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power2.out", stagger: 0.06 }, 4.25);
    OUT(["#s5-t1", "#s5-roll"], 5.85);
    tl.to(["#s5-a", "#s5-b", "#s5-c"], { y: -80, opacity: 0, filter: "blur(10px)", duration: 0.3, ease: "power3.in", stagger: 0.04 }, 5.85);
""")

# ---------------- S6: visiteurs -> clients ----------------
notifs = [
    ("doc", "Nouvelle demande de devis", "Site web · Formulaire", "à l'instant"),
    ("phone", "Appel entrant", "Depuis votre fiche Google", "2 min"),
    ("cal", "Rendez-vous réservé", "Jeu. 29 oct. · 10:00", "5 min"),
    ("chat", "Nouveau message", "Formulaire de contact", "12 min"),
    ("doc", "Nouvelle demande de devis", "Recommandé par l'IA", "20 min"),
]
nrows = "".join(
    f'<div id="s6-n{i}" class="card nrow" style="top:{580 + i * 136}px"><div class="tile">{ICONS[ic]}</div>'
    f'<div class="tx"><div class="a">{html.escape(a)}</div><div class="b grey">{html.escape(b)}</div></div><div class="tm grey">{html.escape(tm)}</div></div>'
    for i, (ic, a, b, tm) in enumerate(notifs))
files["s6"] = scene("s6", 4.0, """
#s6-t1 { left: 96px; top: 210px; } #s6-t2 { left: 96px; top: 278px; }
#s6-t3 { left: 96px; top: 370px; font-size: 100px; font-weight: 800; }
#s6-vis { position: relative; }
#s6-strike { position: absolute; left: 0; right: 10px; top: 54%; height: 7px; border-radius: 4px; background: linear-gradient(90deg, #38A8F5, #B98AF5); transform-origin: 0 50%; }
#root .nrow { left: 70px; width: 940px; height: 120px; }
#root .nrow .tile { position: absolute; left: 24px; top: 20px; width: 80px; height: 80px; border-radius: 22px; }
#root .nrow .tx { position: absolute; left: 130px; top: 18px; }
#root .nrow .a { font-size: 34px; font-weight: 600; }
#root .nrow .b { font-size: 28px; margin-top: 4px; }
#root .nrow .tm { position: absolute; right: 32px; top: 22px; font-size: 28px; }
""", f"""
    <div class="arc" style="top:1560px"></div>
    <div id="s6-t1" class="abs q"><span class="w">Vos </span><span class="w" id="s6-vis">visiteurs<span id="s6-strike"></span></span></div>
    <div id="s6-t2" class="abs q">{words("deviennent")}</div>
    <div id="s6-t3" class="abs syne">{words("des clients.", cls="w g")}</div>
    {nrows}
""", """
    W_IN("#s6-t1 .w", 0.05, 0.08);
    tl.fromTo("#s6-strike", { scaleX: 0 }, { scaleX: 1, duration: 0.35, ease: "power3.inOut" }, 0.75);
    tl.to("#s6-vis", { color: "#55555C", duration: 0.3 }, 0.85);
    W_IN("#s6-t2 .w", 0.95);
    tl.fromTo("#s6-t3 .w", { opacity: 0, filter: "blur(10px)", scale: 1.06 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.5, ease: "expo.out", stagger: 0.1 }, 1.25);
    tl.fromTo(".nrow", { y: -40, opacity: 0, filter: "blur(8px)", scale: 0.96 }, { y: 0, opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.5, ease: "expo.out", stagger: 0.32 }, 0.6);
    OUT(["#s6-t1", "#s6-t2", "#s6-t3"], 3.6);
    tl.to(".nrow", { x: -120, opacity: 0, filter: "blur(10px)", duration: 0.3, ease: "power3.in", stagger: 0.03 }, 3.6);
""")

# ---------------- S7: méthode (4 étapes) ----------------
steps = [("pen", "1. Échange", "On parle de vos objectifs", 330), ("code", "2. Maquette", "Vous validez avant le code", 750),
         ("star", "3. Création", "J'ajuste selon vos retours", 330), ("check", "4. Mise en ligne", "Je reste disponible après", 750)]
steps[0] = ("chat",) + steps[0][1:]
blocks, paths = [], []
for i, (ic, t, d, cx) in enumerate(steps):
    y = 450 + i * 212
    blocks.append(f'<div id="s7-b{i}" class="stp" style="left:{cx - 270}px;top:{y}px"><div class="tl tile">{ICONS[ic]}</div>'
                  f'<div class="st syne">{html.escape(t)}</div><div class="sd grey">{html.escape(d)}</div></div>')
    if i < 3:
        nx = steps[i + 1][3]
        sx = cx + 55 if nx > cx else cx - 55
        y0, y1 = y + 55, y + 212
        paths.append(f'<path id="s7-l{i}" d="M{sx} {y0} C{nx} {y0} {nx} {y0 + 55} {nx} {y1}" />')
files["s7"] = scene("s7", 4.6, """
#s7-t1 { top: 220px; font-size: 52px; } #s7-t2 { top: 290px; font-size: 66px; font-weight: 800; }
#root .stp { position: absolute; width: 540px; height: 200px; }
#root .stp .tl { position: absolute; left: 215px; top: 0; }
#root .stp .st { position: absolute; left: 0; right: 0; top: 118px; text-align: center; font-size: 40px; font-weight: 700; }
#root .stp .sd { position: absolute; left: 0; right: 0; top: 168px; text-align: center; font-size: 28px; }
#s7-lines { position: absolute; left: 0; top: 0; }
#s7-lines path { fill: none; stroke: url(#s7g); stroke-width: 5; stroke-linecap: round; }
""", f"""
    <div class="arc" style="top:1560px"></div>
    <div id="s7-t1" class="abs center q">{words("Un seul interlocuteur,")}</div>
    <div id="s7-t2" class="abs center syne">{words("du début à la fin.", cls="w g")}</div>
    <svg id="s7-lines" width="1080" height="1920"><defs><linearGradient id="s7g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#38A8F5"/><stop offset="1" stop-color="#B98AF5"/></linearGradient></defs>{"".join(paths)}</svg>
    {"".join(blocks)}
""", """
    W_IN("#s7-t1 .w", 0.05, 0.07);
    tl.fromTo("#s7-t2 .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.35, ease: "power4.out", stagger: 0.07 }, 0.35);
    // all steps present but dim, then light up one after the other along the line
    tl.fromTo(".stp", { opacity: 0, y: 30 }, { opacity: 0.32, y: 0, duration: 0.5, ease: "expo.out", stagger: 0.06 }, 0.3);
    tl.fromTo(".stp .tl", { filter: "grayscale(1) brightness(0.35)" }, { filter: "grayscale(1) brightness(0.35)", duration: 0.01 }, 0);
    document.querySelectorAll("#s7-lines path").forEach((p) => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
    [0, 1, 2, 3].forEach((i) => {
      const t = 0.8 + i * 0.7;
      tl.to(`#s7-b${i}`, { opacity: 1, duration: 0.25, ease: "power2.out" }, t);
      tl.to(`#s7-b${i} .tl`, { filter: "grayscale(0) brightness(1)", duration: 0.25, ease: "power2.out" }, t);
      tl.fromTo(`#s7-b${i} .tl`, { scale: 0.9 }, { scale: 1, duration: 0.45, ease: "back.out(1.6)" }, t);
      if (i < 3) tl.to(`#s7-l${i}`, { strokeDashoffset: 0, duration: 0.45, ease: "power2.inOut" }, t + 0.25);
    });
    OUT(["#s7-t1", "#s7-t2", "#s7-lines"], 4.2);
    tl.to(".stp", { opacity: 0, filter: "blur(10px)", duration: 0.25, ease: "power3.in", stagger: 0.03 }, 4.2);
""")

# ---------------- S8: on s'occupe de tout ----------------
files["s8"] = scene("s8", 4.4, """
#s8-t1 { top: 210px; } #s8-t2 { top: 280px; font-size: 124px; font-weight: 800; }
#root .bx .lb { position: absolute; left: 40px; top: 34px; font-family: 'Syne'; font-weight: 700; font-size: 36px; color: #CFCFD6; line-height: 1.15; }
#root .bx .sm { position: absolute; font-size: 28px; color: #9A9AA0; }
#root .bx .big { position: absolute; font-family: 'Syne'; font-weight: 800; line-height: 1; }
#root .pg { background: linear-gradient(90deg, #fff 30%, #B9B4FF 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
#s8-a { left: 70px; top: 470px; width: 940px; height: 326px; }
#s8-b { left: 70px; top: 812px; width: 460px; height: 250px; }
#s8-c { left: 550px; top: 812px; width: 460px; height: 250px; }
#s8-d { left: 70px; top: 1078px; width: 460px; height: 242px; }
#s8-e { left: 550px; top: 1078px; width: 460px; height: 242px; }
#s8-new { position: absolute; left: 40px; top: 170px; padding: 6px 20px; border-radius: 22px; background: linear-gradient(90deg, #38A8F5, #B98AF5); color: #000; font-size: 28px; font-weight: 600; letter-spacing: 0.1em; }
#s8-d .tile { position: absolute; left: 40px; top: 110px; width: 96px; height: 96px; border-radius: 26px; }
""", f"""
    <div class="arc" style="top:1580px"></div>
    <div id="s8-t1" class="abs center q">{words("On s'occupe")}</div>
    <div id="s8-t2" class="abs center syne">{words("de tout.", cls="w g")}</div>
    <div id="s8-a" class="card bx"><div class="lb">Site vitrine</div><div class="sm" style="left:40px;top:92px">à partir de</div>
      <div class="big pg" style="left:40px;top:132px;font-size:120px"><span id="s8-num">599</span> €</div><div class="sm" style="left:40px;top:262px">TTC, hébergement et domaine inclus 1 an</div></div>
    <div id="s8-b" class="card bx"><div class="lb">Maintenance</div><div class="big pg" style="left:40px;top:100px;font-size:96px">49 €</div><div class="sm" style="left:40px;top:196px">par mois</div></div>
    <div id="s8-c" class="card bx"><div class="lb">Domaine et<br>hébergement</div><div class="big pg" style="left:40px;top:128px;font-size:72px">Inclus</div><div class="sm" style="left:40px;top:200px">1 an</div></div>
    <div id="s8-d" class="card bx"><div class="lb">Référencement</div><div class="tile">{ICONS["search"].replace('stroke="currentColor"', 'stroke="#000"')}</div><div class="sm" style="left:160px;top:120px;width:270px">Google, Maps<br>et IA</div></div>
    <div id="s8-e" class="card bx"><div class="lb">Création<br>d'application</div><div id="s8-new">NOUVEAU</div></div>
""", """
    W_IN("#s8-t1 .w", 0.05, 0.08);
    tl.fromTo("#s8-t2 .w", { opacity: 0, filter: "blur(10px)", scale: 1.06 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.5, ease: "expo.out", stagger: 0.1 }, 0.3);
    const from = [[-140, 60, -4], [-200, 120, 5], [200, 120, -5], [-200, 160, 4], [200, 160, -3]];
    ["#s8-a", "#s8-b", "#s8-c", "#s8-d", "#s8-e"].forEach((s, i) => {
      tl.fromTo(s, { x: from[i][0], y: from[i][1], rotation: from[i][2], scale: 0.88, opacity: 0, filter: "blur(10px)" },
        { x: 0, y: 0, rotation: 0, scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.7, ease: "expo.out" }, 0.55 + i * 0.12);
    });
    const n = { v: 0 }; const el = document.getElementById("s8-num");
    tl.fromTo(n, { v: 0 }, { v: 599, duration: 1.1, ease: "power2.out", onUpdate: () => { el.textContent = Math.round(n.v); } }, 0.75);
    tl.fromTo("#s8-new", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.7)" }, 1.6);
    OUT(["#s8-t1", "#s8-t2"], 4.0);
    tl.to(".bx", { scale: 0.9, opacity: 0, filter: "blur(12px)", duration: 0.3, ease: "power3.in", stagger: 0.03 }, 4.0);
""")

# ---------------- S9: CTA ----------------
days = [("JEU.", "29", "OCT."), ("VEN.", "30", "OCT."), ("LUN.", "2", "NOV."), ("MAR.", "3", "NOV.")]
chips = "".join(f'<div id="s9-d{i}" class="day"><div class="dw">{a}</div><div class="dn syne">{b}</div><div class="dw">{c}</div></div>' for i, (a, b, c) in enumerate(days))
hours = "".join(f'<div id="s9-h{i}" class="hr">{h}</div>' for i, h in enumerate(["09:30", "10:00", "14:00", "16:30"]))
files["s9"] = scene("s9", 4.8, """
#s9-e1 { top: 580px; } #s9-e2 { top: 650px; font-size: 124px; font-weight: 800; }
#s9-r1 { top: 220px; } #s9-r2 { top: 290px; font-size: 100px; font-weight: 800; }
#s9-card { left: 70px; top: 470px; width: 940px; height: 830px; }
#root .lbl { position: absolute; left: 0; right: 0; text-align: center; font-family: 'Syne'; font-weight: 700; font-size: 36px; }
#s9-days { position: absolute; left: 40px; top: 120px; display: flex; gap: 20px; }
#root .day { width: 200px; height: 200px; border-radius: 28px; background: #18181D; border: 2px solid #2A2A31; text-align: center; padding-top: 26px; }
#root .dw { font-size: 28px; color: #9A9AA0; letter-spacing: 0.06em; }
#root .dn { font-size: 72px; font-weight: 800; margin: 4px 0 2px; }
#s9-hours { position: absolute; left: 40px; top: 448px; display: flex; gap: 20px; }
#root .hr { width: 200px; height: 90px; border-radius: 22px; background: #18181D; border: 2px solid #2A2A31; font-size: 34px; display: flex; align-items: center; justify-content: center; }
#s9-btn { position: absolute; left: 90px; top: 600px; width: 760px; height: 116px; border-radius: 24px; background: #fff; color: #000;
  font-size: 38px; font-weight: 500; display: flex; align-items: center; justify-content: center; }
#s9-btn .ok { position: absolute; inset: 0; border-radius: 24px; background: linear-gradient(90deg, #38A8F5, #8E8CF6 55%, #B98AF5);
  display: flex; align-items: center; justify-content: center; gap: 16px; font-weight: 600; opacity: 0; }
#s9-btn .ok svg { width: 44px; height: 44px; }
#s9-sub { position: absolute; left: 0; right: 0; top: 744px; text-align: center; font-size: 28px; color: #9A9AA0; }
""", f"""
    <div class="arc" style="top:1580px"></div>
    <div id="s9-e1" class="abs center q">{words("Envie d'en faire")}</div>
    <div id="s9-e2" class="abs center syne">{words("autant ?", cls="w g")}</div>
    <div id="s9-r1" class="abs center q">{words("Réservez votre")}</div>
    <div id="s9-r2" class="abs center syne">{words("rendez-vous.", cls="w g")}</div>
    <div id="s9-card" class="card">
      <div class="lbl" style="top:50px">1. Le jour</div>
      <div id="s9-days">{chips}</div>
      <div class="lbl" style="top:376px">2. L'horaire</div>
      <div id="s9-hours">{hours}</div>
      <div id="s9-btn"><span>Réserver un rendez-vous</span><div class="ok">{ICONS["check"]}<span>Rendez-vous confirmé</span></div></div>
      <div id="s9-sub">Je vous appelle à l'heure choisie.</div>
    </div>
    <div id="s9-cursor" class="cursor" style="left:0;top:0">{CURSOR}</div>
""", """
    tl.fromTo("#s9-e1 .w", { opacity: 0, color: "#3A3A40" }, { opacity: 1, color: "#ffffff", duration: 0.3, ease: "power2.out", stagger: 0.08 }, 0.05);
    tl.fromTo("#s9-e2 .w", { opacity: 0, filter: "blur(10px)", scale: 1.08 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.5, ease: "expo.out", stagger: 0.1 }, 0.35);
    OUT(["#s9-e1", "#s9-e2"], 1.3, 0.04);
    W_IN("#s9-r1 .w", 1.5, 0.08);
    tl.fromTo("#s9-r2 .w", { opacity: 0, filter: "blur(10px)", scale: 1.06 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.5, ease: "expo.out" }, 1.7);
    tl.fromTo("#s9-card", { y: 120, opacity: 0, filter: "blur(10px)" }, { y: 0, opacity: 1, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, 1.6);
    // cursor: day -> hour -> button
    const C = "#s9-cursor"; const click = (t, target) => {
      tl.to(C, { scale: 0.85, duration: 0.07, ease: "power2.in" }, t); tl.to(C, { scale: 1, duration: 0.1, ease: "power2.out" }, t + 0.07);
      tl.to(target, { scale: 0.94, duration: 0.07, ease: "power2.in" }, t); tl.to(target, { scale: 1, duration: 0.12, ease: "power2.out" }, t + 0.07);
    };
    tl.fromTo(C, { x: 1150, y: 1600 }, { x: 430, y: 720, duration: 0.55, ease: "expo.out" }, 2.0);
    click(2.55, "#s9-d1");
    tl.to("#s9-d1", { backgroundColor: "#24233A", borderColor: "#8E8CF6", duration: 0.15 }, 2.56);
    tl.to(C, { x: 410, y: 1000, duration: 0.35, ease: "expo.out" }, 2.7);
    click(3.05, "#s9-h1");
    tl.to("#s9-h1", { backgroundColor: "#24233A", borderColor: "#8E8CF6", duration: 0.15 }, 3.06);
    tl.to(C, { x: 600, y: 1140, duration: 0.35, ease: "expo.out" }, 3.2);
    click(3.55, "#s9-btn");
    tl.to("#s9-btn .ok", { opacity: 1, duration: 0.2, ease: "power2.out" }, 3.6);
    tl.to("#s9-btn > span", { opacity: 0, duration: 0.15 }, 3.6);
    tl.fromTo("#s9-btn .ok svg", { scale: 0.4 }, { scale: 1, duration: 0.35, ease: "back.out(2)" }, 3.6);
    tl.to(C, { opacity: 0, duration: 0.2 }, 3.95);
    OUT(["#s9-r1", "#s9-r2", "#s9-card"], 4.52, 0.03);
""")

# ---------------- S10: end card ----------------
marq = "  ›  ".join(["Sites vitrines", "Boutiques en ligne", "Portfolios", "Applications", "Référencement", "Identité visuelle"]) + "  ›  "
files["s10"] = scene("s10", 4.5, LOCK_CSS.replace("{p}","s10") + """
#s10-lock { top: 470px; }
#s10-tag { top: 950px; font-size: 56px; font-weight: 800; }
#s10-ct { top: 1110px; font-size: 32px; color: #9A9AA0; letter-spacing: 0.04em; }
#s10-band { position: absolute; left: 0; right: 0; top: 1200px; height: 110px; overflow: hidden; }
#s10-band .ln { position: absolute; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #38A8F5, #B98AF5); transform-origin: 0 50%; }
#s10-mq { position: absolute; left: 0; top: 24px; white-space: pre; font-family: 'Syne'; font-weight: 700; font-size: 48px; }
""", f"""
    <div class="arc" style="top:1560px"></div>
    {lockup("s10")}
    <div id="s10-tag" class="abs center syne">{words("Un site qui vous")}<br>{words("ressemble.", cls="w g")}</div>
    <div id="s10-ct" class="abs center">ckwebdesigner.fr  ·  06 34 36 61 70</div>
    <div id="s10-band" data-layout-allow-overflow><div class="ln" style="top:0"></div><div class="ln" style="bottom:0"></div>
      <div id="s10-mq" class="g">{marq * 4}</div></div>
""", """
    tl.fromTo("#s10-logo .dash", { x: -260, opacity: 0 }, { x: 0, opacity: 1, duration: 0.55, ease: "expo.out", stagger: 0.05 }, 0.05);
    tl.fromTo("#s10-logo .mark", { x: -70, opacity: 0 }, { x: 0, opacity: 1, duration: 0.6, ease: "expo.out", stagger: 0.08 }, 0.15);
    tl.fromTo("#s10-lock .l", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power2.out", stagger: 0.035 }, 0.5);
    tl.fromTo("#s10-tag .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.35, ease: "power4.out", stagger: 0.08 }, 1.1);
    tl.fromTo("#s10-ct", { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power2.out" }, 1.6);
    tl.fromTo("#s10-band .ln", { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "power2.inOut" }, 1.0);
    tl.fromTo("#s10-mq", { opacity: 0 }, { opacity: 1, duration: 0.4 }, 1.3);
    tl.fromTo("#s10-mq", { x: 0 }, { x: -1400, duration: 4.5, ease: "none" }, 0);
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
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #bg {{ position: absolute; inset: 0; background: #000; }}
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
