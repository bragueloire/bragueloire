"""Genera los SVG del perfil de GitHub con el estilo de danielflores.cl.

Requiere fonttools + brotli (para medir texto):  pip install fonttools brotli
Edita los textos más abajo y corre:            python3 build.py
"""
import base64, math, random
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).parent
OUT, FONTS, SRC = ROOT / "assets", ROOT / "fonts", ROOT / "src"
W = 1200

# ─────────────────────────── tokens del sitio ───────────────────────────
BG, CARD, CARD2 = "#030303", "#0c0c0f", "#111116"
BORDER = "rgba(255,255,255,.07)"
V, V2, BLUE = "#4425fe", "#7c3aed", "#3b82f6"
WHITE, MUTED = "#ffffff", "#94a3b8"
GRAD = [(0, "#4425fe"), (.5, "#818cf8"), (1, "#c084fc")]

FAMS = {"SG7": "sg700", "SG5": "sg500", "PJ4": "pj400", "PJ6": "pj600", "PJ7": "pj700"}
_fonts = {k: TTFont(FONTS / f"{v}.woff2") for k, v in FAMS.items()}
_cmaps = {k: f.getBestCmap() for k, f in _fonts.items()}


def tw(text, fam, size, ls=0):
    """Ancho real del texto en px."""
    f, cmap = _fonts[fam], _cmaps[fam]
    upm, hmtx = f["head"].unitsPerEm, f["hmtx"]
    adv = sum(hmtx[cmap.get(ord(c), cmap[ord(" ")])][0] for c in text)
    return adv / upm * size + ls * max(len(text) - 1, 0)


def wrap(text, fam, size, maxw):
    lines, cur = [], ""
    for word in text.split():
        cand = f"{cur} {word}".strip()
        if tw(cand, fam, size) <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    return lines + [cur] if cur else lines


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def T(x, y, s, fam, size, fill=WHITE, ls=0, anchor="start", extra=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{fam}" font-size="{size}" fill="{fill}"{l}{a}{extra}>{esc(s)}</text>'


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def grad(id_, x1, x2, y=0, units=True):
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in GRAD)
    u = f' gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"' if units else ' x1="0" y1="0" x2="1" y2="1"'
    return f'<linearGradient id="{id_}"{u}>{stops}</linearGradient>'


def frame(H, body, fams, defs="", label="", extra_css=""):
    faces = "".join(
        f"@font-face{{font-family:'{k}';src:url({b64(FONTS / (FAMS[k] + '.woff2'), 'font/woff2')}) format('woff2')}}"
        f".{k}{{font-family:'{k}',{'\"Space Grotesk\"' if k.startswith('SG') else '\"Plus Jakarta Sans\"'},system-ui,sans-serif}}"
        for k in fams)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}">
<style>{faces}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes tw{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
@keyframes drift{{0%{{transform:translate(0,0)}}100%{{transform:translate(-40px,18px)}}}}
@keyframes pulse{{0%,100%{{opacity:.45}}50%{{opacity:.9}}}}
@keyframes slide{{to{{transform:translateX(var(--d))}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
{extra_css}</style>
<defs>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#fff" fill-opacity=".045"/></pattern>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<filter id="blur60" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
<filter id="blur24" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="24"/></filter>
{defs}
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#dots)"/>
{body}
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" fill="none" stroke="{BORDER}"/>
</svg>"""


def glow(cx, cy, r, color, op):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{op}" filter="url(#blur60)"/>'


def button(x, y, label, primary=True, h=54):
    w = tw(label, "PJ7", 16) + 56
    if primary:
        return w, f"""<rect x="{x}" y="{y+6}" width="{w:.0f}" height="{h}" rx="12" fill="{V}" opacity=".55" filter="url(#blur24)"/>
<rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="12" fill="{V}"/>
{T(x + 28, y + h/2 + 6, label, "PJ7", 16)}"""
    return w, f"""<rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="12" fill="{CARD2}" stroke="rgba(255,255,255,.12)"/>
{T(x + 28, y + h/2 + 6, label, "PJ7", 16)}"""


def pill(x, y, label, fam="PJ7", size=11, ls=1.4, fill="rgba(68,37,254,.18)", stroke="rgba(129,140,248,.35)", color="#a5b4fc", anchor="start"):
    w = tw(label, fam, size, ls) + 22
    x0 = x - w if anchor == "end" else x
    return w, f"""<rect x="{x0:.1f}" y="{y}" width="{w:.1f}" height="24" rx="12" fill="{fill}" stroke="{stroke}"/>
{T(x0 + 11, y + 16.2, label, fam, size, color, ls)}"""


# ───────────────────────────── 1 · hero ─────────────────────────────
def hero():
    H = 740
    rnd = random.Random(11)
    nodes = [(rnd.uniform(-40, W + 40), rnd.uniform(-20, H + 20)) for _ in range(95)]
    lines = []
    for i, (x1, y1) in enumerate(nodes):
        for x2, y2 in nodes[i + 1:]:
            d = math.hypot(x2 - x1, y2 - y1)
            if d < 150:
                lines.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#fff" stroke-opacity="{.11 * (1 - d/150):.3f}"/>')
    dots = []
    for i, (x, y) in enumerate(nodes):
        if i % 9 == 0:
            dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2.6" fill="#818cf8" style="animation:tw {3 + i % 5}s ease-in-out {i % 4}s infinite"/>')
        else:
            dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{1.1 + (i % 3) * .4:.1f}" fill="#fff" fill-opacity=".35"/>')

    # titular
    h1a, h1b = "Sin fórmulas.", "Solo soluciones."
    size, ls = 82, -4.1
    wb = tw(h1b, "SG7", size, ls)
    x0 = 58

    # párrafo con negrita y chip ROAS (como en el sitio)
    tokens = [("Anuncios que no venden, procesos a mano y datos que no cuadran. Lo resuelvo con tecnología, creatividad y datos para", "n"),
              ("quitarte un peso de encima.", "b"),
              ("Mientras tú duermes, yo me aseguro de que tu", "n"),
              ("ROAS", "pill"), ("siga creciendo.", "n")]
    fs, lh, maxw = 19, 32, 590
    words = [(w, k) for text, k in tokens for w in ([text] if k == "pill" else text.split())]
    sp = tw(" ", "PJ4", fs)

    def wwidth(w, k):
        return tw(w, "PJ7", fs * .9) + 22 if k == "pill" else tw(w, "PJ7" if k == "b" else "PJ4", fs)

    para, cx, cy = [], x0, 352
    for w, k in words:
        ww = wwidth(w, k)
        if cx > x0 and cx + ww > x0 + maxw:
            cx, cy = x0, cy + lh
        if k == "pill":
            para.append(f'<rect x="{cx:.1f}" y="{cy-21}" width="{ww:.1f}" height="30" rx="8" fill="{V}"/>'
                        + T(cx + 11, cy, w, "PJ7", fs * .9, WHITE))
        else:
            para.append(T(cx, cy, w, "PJ7" if k == "b" else "PJ4", fs, WHITE if k == "b" else MUTED))
        cx += ww + sp

    by = cy + 44
    w1, b1 = button(x0, by, "Hablemos de tu proyecto  →")
    _, b2 = button(x0 + w1 + 14, by, "Ver soluciones", primary=False)

    # foto con anillo
    px, py, pr = 952, 290, 168
    photo = f"""
<circle cx="{px}" cy="{py}" r="{pr+30}" fill="{V}" filter="url(#blur60)" style="animation:pulse 5s ease-in-out infinite"/>
<circle cx="{px}" cy="{py}" r="{pr+30}" fill="none" stroke="#fff" stroke-opacity=".07"/>
<g transform="translate({px},{py})"><g style="animation:spin 14s linear infinite">
  <circle r="{pr+30}" fill="none" stroke="url(#gArc)" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="190 1100"/>
  <circle cx="{pr+30}" cy="0" r="4" fill="#c084fc"/></g></g>
<circle cx="{px}" cy="{py}" r="{pr+9}" fill="{BG}" stroke="url(#gRing)" stroke-width="8"/>
<image href="{b64(SRC / 'me.jpg', 'image/jpeg')}" x="{px-pr}" y="{py-pr}" width="{pr*2}" height="{pr*2}" preserveAspectRatio="xMidYMid slice" clip-path="url(#photoClip)"/>"""

    # stats
    stats = [("12+ Años", "RESOLVIENDO EN DIGITAL"), ("Partner", "NO PROVEEDOR"),
             ("Arte + Datos", "EN UNA SOLA PERSONA"), ("20+ Empresas", "CONFÍAN EN MÍ HOY")]
    sw, sy = (W - 2 * x0 - 3 * 16) / 4, H - 140
    st = []
    for i, (big, small) in enumerate(stats):
        sx = x0 + i * (sw + 16)
        st.append(f"""<rect x="{sx:.1f}" y="{sy}" width="{sw:.1f}" height="96" rx="18" fill="{CARD}" fill-opacity=".85" stroke="{BORDER}"/>
{T(sx + 24, sy + 47, big, "SG7", 28, WHITE, -1)}
{T(sx + 24, sy + 74, small, "PJ6", 11.5, MUTED, 1.6)}""")

    defs = f"""<linearGradient id="gH1s" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x0 + wb:.0f}" y2="0" spreadMethod="reflect">
  {''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in GRAD)}
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;{2*wb:.0f} 0" dur="9s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="gRing" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{V}"/><stop offset=".6" stop-color="{V2}"/><stop offset="1" stop-color="#818cf8"/></linearGradient>
<linearGradient id="gArc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c084fc" stop-opacity="0"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
<clipPath id="photoClip"><circle cx="{px}" cy="{py}" r="{pr}"/></clipPath>
<linearGradient id="veil" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BG}" stop-opacity=".75"/><stop offset=".55" stop-color="{BG}" stop-opacity=".2"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>"""

    body = f"""
{glow(120, -40, 380, V, .55)}{glow(1050, 360, 300, V2, .35)}{glow(520, 760, 260, BLUE, .18)}
<g style="animation:drift 26s ease-in-out infinite alternate">{''.join(lines)}{''.join(dots)}</g>
<rect width="{W}" height="{H}" fill="url(#veil)"/>
<image href="{b64(SRC / 'logo.svg', 'image/svg+xml')}" x="{x0}" y="54" width="{310.2*.88:.1f}" height="{50.4*.88:.1f}"/>
{T(x0 - 4, 192, h1a, "SG7", size, WHITE, ls)}
{T(x0 - 4, 280, h1b, "SG7", size, "url(#gH1s)", ls)}
{''.join(para)}
{b1}{b2}
{photo}
{''.join(st)}"""
    return frame(H, body, ["SG7", "PJ4", "PJ6", "PJ7"], defs,
                 "Daniel Flores Osses — Sin fórmulas. Solo soluciones.")


# ───────────────────────────── 2 · marquee ─────────────────────────────
def marquee():
    H = 78
    items = ["Growth Partner", "Meta Ads", "E-commerce", "Shopify", "Automatización", "IA Flows",
             "Webflow", "JavaScript", "Tailwind CSS", "Google Analytics 4", "Cinema 4D", "After Effects"]
    fs, ls, gap = 15, 3, 34
    parts, x = [], 0
    for it in items:
        s = it.upper()
        parts.append(T(x, 45, s, "SG5", fs, MUTED, ls))
        x += tw(s, "SG5", fs, ls) + gap
        parts.append(f'<path transform="translate({x - gap/2:.1f},40)" d="M0,-6 L1.4,-1.4 L6,0 L1.4,1.4 L0,6 L-1.4,1.4 L-6,0 L-1.4,-1.4Z" fill="#818cf8"/>')
    cycle = x
    row = "".join(parts)
    copies = "".join(f'<g transform="translate({cycle*i:.1f},0)">{row}</g>' for i in range(3))
    defs = f"""<linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
<linearGradient id="fadeR" x1="0" x2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>"""
    body = f"""{glow(600, 120, 200, V, .25)}
<g style="--d:-{cycle:.1f}px;animation:slide {cycle/32:.1f}s linear infinite">{copies}</g>
<rect width="160" height="{H}" fill="url(#fadeL)"/><rect x="{W-160}" width="160" height="{H}" fill="url(#fadeR)"/>"""
    return frame(H, body, ["SG5"], defs, "Meta Ads, E-commerce, Shopify, Automatización, IA Flows, Webflow, JavaScript, Tailwind CSS, GA4, Cinema 4D, After Effects")


# ───────────────────────────── 3 · soluciones ─────────────────────────────
SOLUTIONS = [
    ("Desarrollo", None, None, "Planillas, sistemas que no conversan y procesos a mano frenan tu negocio. Desarrollo web, apps y plataformas a medida que trabajan por ti."),
    ("Media Buyer", "media-buyer", "100", "¿Gastas en anuncios y no sabes qué te está vendiendo? Invierto tu presupuesto como si fuera mío y lo muevo a lo que da retorno."),
    ("Gestión E-Commerce", "ecommerce", "FULL SERVICE", "Visitas que no compran y carritos abandonados son plata perdida. Hago que comprar en tu tienda sea tan fácil que quieran volver."),
    ("Chatbots con IA", "chatbots", "NUEVO", "Clientes sin respuesta son ventas perdidas. Un asistente con IA entrenado con tu material atiende en tu web 24/7 sin equivocarse."),
    ("Landing Pages", "landing-pages", None, "¿Mandas tus anuncios a la home? Estás quemando presupuesto. Creo landings sin distracciones que convierten clics en clientes."),
    ("Analítica & Datos", "analytics", None, "¿Cada área tiene sus propios números? Conecto tu CRM, ERP y todos tus datos en un solo lugar para decidir con la foto completa."),
    ("Animación Digital", "animation", None, "Nadie lee textos largos. Animaciones que explican tu producto en segundos, detienen el scroll y hacen que tu marca se recuerde."),
]


def solutions():
    pad, gap, cols = 48, 16, 4
    cw = (W - 2 * pad - (cols - 1) * gap) / cols
    ih = cw * 500 / 800
    dfs, dlh = 14, 21.5
    desc_lines = [wrap(d, "PJ4", dfs, cw - 44) for *_, d in SOLUTIONS]
    ch = ih + 22 + 30 + max(len(l) for l in desc_lines) * dlh + 26
    top = 210
    H = int(top + 2 * ch + gap + pad)

    title = "¿Cómo te alivio la carga?"
    sub = wrap("Elige el problema que te quita el sueño. Cada solución parte por entender tu negocio y termina en resultados que puedes medir.", "PJ4", 18, 700)
    _, kp = pill(pad, 50, "SOLUCIONES")
    head = kp + T(pad - 2, 122, title, "SG7", 48, WHITE, -2.2) + "".join(
        T(pad, 160 + i * 28, l, "PJ4", 18, MUTED) for i, l in enumerate(sub))

    cards, clips = [], []
    for i, ((name, art, tag, _), lines) in enumerate(zip(SOLUTIONS, desc_lines)):
        c, r = i % cols, i // cols
        x, y = pad + c * (cw + gap), top + r * (ch + gap)
        clips.append(f'<clipPath id="art{i}"><rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ih:.1f}" rx="20"/></clipPath>')
        if art:
            visual = f'<image href="{b64(SRC / (art + ".svg"), "image/svg+xml")}" x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ih:.1f}" preserveAspectRatio="xMidYMid slice" clip-path="url(#art{i})" opacity=".9"/>'
        else:
            visual = (f'<g clip-path="url(#art{i})">{glow(x + cw/2, y + ih/2, 70, V, .6)}</g>'
                      + T(x + cw/2, y + ih/2 + 22, "</>", "SG7", 64, "url(#gCode)", -2, "middle"))
        tagsvg = pill(x + cw - 14, y + 14, tag, anchor="end", fill="rgba(3,3,3,.75)")[1] if tag else ""
        cards.append(f"""<g>
<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ch:.1f}" rx="20" fill="{CARD}" stroke="{BORDER}"/>
<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ih:.1f}" rx="20" fill="{CARD2}"/>
{visual}{tagsvg}
<line x1="{x:.1f}" y1="{y+ih:.1f}" x2="{x+cw:.1f}" y2="{y+ih:.1f}" stroke="{BORDER}"/>
{T(x + 22, y + ih + 40, name, "SG7", 21, WHITE, -.6)}
{''.join(T(x + 22, y + ih + 70 + j * dlh, l, "PJ4", dfs, MUTED) for j, l in enumerate(lines))}
</g>""")

    # 8ª tarjeta: ver todas
    x, y = pad + 3 * (cw + gap), top + ch + gap
    more_lines = wrap("IA, consultoría, contenido, influencers, mapping y más. Encuentra la que resuelve tu problema.", "PJ4", 15, cw - 48)
    cards.append(f"""<g>
<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ch:.1f}" rx="20" fill="url(#gMore)"/>
<g clip-path="url(#moreClip)">{glow(x + cw, y, 140, "#c084fc", .55)}</g>
<circle cx="{x + 46:.1f}" cy="{y + 50:.1f}" r="24" fill="rgba(255,255,255,.16)"/>
{T(x + 46, y + 58, "→", "PJ7", 22, WHITE, 0, "middle")}
{T(x + 24, y + ch - 150, "Ver todas las", "SG7", 28, WHITE, -1)}
{T(x + 24, y + ch - 118, "soluciones", "SG7", 28, WHITE, -1)}
{''.join(T(x + 24, y + ch - 82 + j * 22, l, "PJ4", 15, "rgba(255,255,255,.82)") for j, l in enumerate(more_lines))}
</g>""")
    clips.append(f'<clipPath id="moreClip"><rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ch:.1f}" rx="20"/></clipPath>')

    defs = "".join(clips) + grad("gCode", 0, 1, units=False) + f"""
<linearGradient id="gMore" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{V}"/><stop offset="1" stop-color="{V2}"/></linearGradient>"""
    body = glow(W - 100, 40, 260, V, .35) + head + "".join(cards)
    return frame(H, body, ["SG7", "PJ4", "PJ7"], defs, "Soluciones: Desarrollo, Media Buyer, Gestión E-Commerce, Chatbots con IA, Landing Pages, Analítica & Datos, Animación Digital")


# ───────────────────────────── 4 · trayectoria ─────────────────────────────
EXPERIENCE = [
    ("2026 — PRESENTE", "Crecimiento Multi-Industria", "Performance & Media Buying",
     "Mantengo de forma activa y simultánea más de 20 campañas de distintas empresas: hoteles, restaurantes, parques de diversiones, clínicas, minimarkets y más. Modelos de negocio diferentes, un solo norte: adquisición de clientes rentable y predecible."),
    ("2025 — PRESENTE", "Mercado Automotriz en Miami", "Estrategia Global (USA)",
     "Conectando inventario con compradores sin fricción. Simplifiqué la gestión interna con una plataforma propia y optimicé la inversión publicitaria para que cada dólar traiga retorno real."),
    ("2024 — PRESENTE", "Impulso al Retail", "Marketing & E-commerce",
     "Hice que comprar online dejara de ser un dolor de cabeza. Mejoré la experiencia de usuario y lancé campañas que conectan visualmente para potenciar las ventas sin forzarlas."),
    ("2023", "Liderazgo de Equipos", "Dirección Creativa",
     "Guié a un equipo de 15 talentos, buscando siempre ese punto medio perfecto donde la creatividad brilla pero el negocio también gana."),
]
AWARDS = [
    ("Premio Eikon", "A la Excelencia en la Comunicación Empresarial (2021). Campaña “Prevenir está en tus Manos”."),
    ("Experiencia Internacional", "Ibiza, España (2019–2020). Agencia Zitrica — Hoteles de Lujo."),
    ("Docencia Universitaria", "Pregrado en Arquitectura de la Información y Desarrollo Web. Post-grado en Animación Digital."),
]


def journey():
    pad, top = 48, 196
    lx, lw = pad, 640
    rx = 760
    rw = W - pad - rx

    left, y = [], top
    for when, kicker, role, desc in EXPERIENCE:
        lines = wrap(desc, "PJ4", 15, lw - 44)
        h = 30 + 34 + 30 + len(lines) * 23 + 34
        _, yp = pill(lx + 36, y - 4, when)
        left.append(f"""<circle cx="{lx + 10}" cy="{y + 8}" r="12" fill="{V}" opacity=".35" filter="url(#blur24)"/>
<circle cx="{lx + 10}" cy="{y + 8}" r="6" fill="{BG}" stroke="#818cf8" stroke-width="2.5"/>
{yp}
{T(lx + 36, y + 58, role, "SG7", 24, WHITE, -.8)}
{T(lx + 36, y + 86, kicker.upper(), "PJ6", 12, "#a5b4fc", 1.6)}
{''.join(T(lx + 36, y + 116 + j * 23, l, "PJ4", 15, MUTED) for j, l in enumerate(lines))}""")
        y += h
    left_end = y - 34
    rail = f'<line x1="{lx + 10}" y1="{top + 8}" x2="{lx + 10}" y2="{left_end - 20}" stroke="url(#gRail)" stroke-width="2"/>'

    right, ry = [T(rx, top + 12, "Reconocimientos y trayectoria", "SG7", 22, WHITE, -.6)], top + 34
    for name, desc in AWARDS:
        lines = wrap(desc, "PJ4", 14, rw - 44)
        h = 58 + len(lines) * 21 + 10
        right.append(f"""<rect x="{rx}" y="{ry}" width="{rw}" height="{h}" rx="18" fill="{CARD}" stroke="{BORDER}"/>
<rect x="{rx}" y="{ry + 18}" width="3" height="24" rx="1.5" fill="url(#gRailH)"/>
{T(rx + 22, ry + 36, name, "SG7", 18, WHITE, -.4)}
{''.join(T(rx + 22, ry + 62 + j * 21, l, "PJ4", 14, MUTED) for j, l in enumerate(lines))}""")
        ry += h + 14

    # MenuTap
    mt_lines = wrap("Cartas digitales para restaurantes: menús con tu marca y dominio, pedidos por WhatsApp y código QR — sin comisión por venta.", "PJ4", 14, rw - 48)
    mh = 74 + len(mt_lines) * 21 + 82
    chips, cxp, cyp = [], rx + 24, ry + 74 + len(mt_lines) * 21 + 18
    for c in ["Sin comisión", "Pedidos por WhatsApp", "Tu marca y dominio"]:
        w = tw(c, "PJ6", 12) + 22
        if cxp + w > rx + rw - 20:
            cxp, cyp = rx + 24, cyp + 32
            mh += 32
        chips.append(f'<rect x="{cxp:.1f}" y="{cyp}" width="{w:.1f}" height="24" rx="12" fill="rgba(255,255,255,.14)"/>' + T(cxp + 11, cyp + 16.5, c, "PJ6", 12, WHITE))
        cxp += w + 8
    right.append(f"""<rect x="{rx}" y="{ry}" width="{rw}" height="{mh}" rx="18" fill="url(#gMt)"/>
<g clip-path="url(#mtClip)">{glow(rx + rw, ry, 120, "#c084fc", .5)}</g>
{T(rx + 24, ry + 32, "PROYECTO PROPIO · MENUTAP.CL", "PJ7", 11, "rgba(255,255,255,.75)", 1.6)}
{T(rx + 24, ry + 62, "Tu carta. Tu marca. Tu QR.", "SG7", 22, WHITE, -.6)}
{''.join(T(rx + 24, ry + 92 + j * 21, l, "PJ4", 14, "rgba(255,255,255,.85)") for j, l in enumerate(mt_lines))}
{''.join(chips)}""")
    right_end = ry + mh

    H = int(max(left_end, right_end) + pad)
    _, kp = pill(pad, 50, "TRAYECTORIA")
    head = kp + T(pad - 2, 124, "Donde he resuelto problemas", "SG7", 48, WHITE, -2.2)
    defs = f"""<linearGradient id="gRail" gradientUnits="userSpaceOnUse" x1="0" y1="{top}" x2="0" y2="{left_end}"><stop offset="0" stop-color="{V}"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
<linearGradient id="gRailH" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{V}"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
<linearGradient id="gMt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{V}"/><stop offset="1" stop-color="{V2}"/></linearGradient>
<clipPath id="mtClip"><rect x="{rx}" y="{ry}" width="{rw}" height="{mh}" rx="18"/></clipPath>"""
    body = glow(80, H - 60, 240, V, .3) + head + rail + "".join(left) + "".join(right)
    return frame(H, body, ["SG7", "PJ4", "PJ6", "PJ7"], defs, "Trayectoria y reconocimientos")


# ───────────────────────────── 5 · contacto ─────────────────────────────
def contact():
    H = 380
    title = "Hablemos de verdad."
    sub = wrap("Cuéntame qué te quita el sueño y te digo con honestidad por dónde partiría. Sin presentaciones eternas ni letra chica.", "PJ4", 18, 620)
    l1, l2 = "Escríbeme por WhatsApp  →", "danielflores.cl"
    w1, w2 = tw(l1, "PJ7", 16) + 56, tw(l2, "PJ7", 16) + 56
    bx = (W - (w1 + w2 + 14)) / 2
    _, b1 = button(bx, 236, l1)
    _, b2 = button(bx + w1 + 14, 236, l2, primary=False)
    tw_ = tw(title, "SG7", 64, -3)
    defs = grad("gCta", (W - tw_) / 2, (W + tw_) / 2)
    body = f"""{glow(600, 330, 320, V, .55)}{glow(220, 0, 200, V2, .3)}{glow(1000, 40, 200, BLUE, .2)}
{T(W/2, 120, title, "SG7", 64, "url(#gCta)", -3, "middle")}
{''.join(T(W/2, 166 + i * 28, l, "PJ4", 18, MUTED, 0, "middle") for i, l in enumerate(sub))}
{b1}{b2}
{T(W/2, H - 28, "© 2026 DANIEL FLORES OSSES · HECHO EN CHILE", "PJ6", 11, "rgba(148,163,184,.6)", 2, "middle")}"""
    return frame(H, body, ["SG7", "PJ4", "PJ6", "PJ7"], defs, "Hablemos de verdad.")


def main():
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*.svg"):
        f.unlink()
    for name, fn in [("hero", hero), ("stack", marquee), ("soluciones", solutions),
                     ("trayectoria", journey), ("contacto", contact)]:
        svg = fn()
        (OUT / f"{name}.svg").write_text(svg)
        print(f"{name:12s} {len(svg)/1024:6.0f} KB")


if __name__ == "__main__":
    main()
