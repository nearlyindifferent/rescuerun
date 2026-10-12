"""SVG artwork for Rescue Runner (Loop 1: simple placeholder shapes)."""
from layout import *


def svg_doc(w, h, inner):
    # The invisible full-size rectangle pins the costume bounds, so the
    # rotation centre is always measured from the top-left of the drawing.
    return ('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="%s" height="%s" '
            'viewBox="0 0 %s %s"><rect width="%s" height="%s" fill="#000" fill-opacity="0"/>%s</svg>'
            % (w, h, w, h, w, h, inner)).encode()


def sx(x):   # stage x -> svg x
    return x + STAGE_W / 2


def sy(y):   # stage y -> svg y
    return STAGE_H / 2 - y


def _cloud(x, y, k=1.0):
    return ('<g transform="translate(%.1f %.1f) scale(%.2f)" fill="#fff">'
            '<ellipse cx="0" cy="0" rx="34" ry="13" fill-opacity="0.95"/><circle cx="-14" cy="-9" r="14" fill-opacity="0.95"/>'
            '<circle cx="8" cy="-13" r="17" fill-opacity="0.95"/><circle cx="24" cy="-4" r="11" fill-opacity="0.95"/>'
            '<ellipse cx="2" cy="6" rx="38" ry="6" fill="#d6ecfb" fill-opacity="0.6"/></g>' % (x, y, k))


def _windows(x, y, cols, rows, w=13, h=17, gx=11, gy=12, lit=(), color="#9fd6f5", frame="#ffffff", shutter=None):
    out = []
    for r in range(rows):
        for c in range(cols):
            wx, wy = x + c * (w + gx), y + r * (h + gy)
            fill = "#ffe9a6" if (r * cols + c) in lit else color
            out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="2.5" fill="%s" stroke="%s" stroke-width="2"/>' % (wx, wy, w, h, fill, frame))
            out.append('<rect x="%.1f" y="%.1f" width="%d" height="2" fill="%s" fill-opacity="0.9"/>' % (wx + w / 2 - 1, wy, 2, frame))
            if shutter:
                out.append('<rect x="%.1f" y="%.1f" width="4" height="%d" fill="%s"/><rect x="%.1f" y="%.1f" width="4" height="%d" fill="%s"/>'
                           % (wx - 5, wy, h, shutter, wx + w + 1, wy, h, shutter))
    return "".join(out)


def _plank(left, right, top):
    """A wooden balcony drawn exactly where the code lets the runner stand."""
    x, y, w = sx(left), sy(top), right - left
    br = ""
    for bx in (x + 16, x + w - 16):
        br += '<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#6b4220" stroke="#432610" stroke-width="1.2" stroke-linejoin="round"/>' % (bx - 9, y + 10, bx + 9, y + 10, bx, y + 26)
    return (br +
            '<rect x="%.1f" y="%.1f" width="%d" height="10" rx="2.5" fill="#8f5a2a" stroke="#4a2c12" stroke-width="1.6"/>'
            '<rect x="%.1f" y="%.1f" width="%d" height="3.5" rx="1.7" fill="#e2b06c"/>'
            '<rect x="%.1f" y="%.1f" width="%d" height="1.6" fill="#4a2c12" fill-opacity="0.35"/>'
            % (x, y, w, x + 1.5, y + 0.8, w - 3, x + 2, y + 6.6, w - 4))


def backdrop():
    p = ['<defs>'
         '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f9df5"/><stop offset="0.55" stop-color="#8fd4ff"/><stop offset="1" stop-color="#e3f6ff"/></linearGradient>'
         '<radialGradient id="sun"><stop offset="0" stop-color="#fff9c9"/><stop offset="0.3" stop-color="#ffe98a" stop-opacity="0.75"/><stop offset="1" stop-color="#ffe98a" stop-opacity="0"/></radialGradient>'
         '<linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#697686"/><stop offset="1" stop-color="#4a5666"/></linearGradient>'
         '</defs>',
         '<rect width="480" height="360" fill="url(#sky)"/>',
         '<circle cx="415" cy="64" r="78" fill="url(#sun)"/><circle cx="415" cy="64" r="24" fill="#fff6b0"/>',
         _cloud(70, 58, 1.1), _cloud(318, 84, 0.8), _cloud(200, 36, 0.7), _cloud(452, 142, 0.9), _cloud(26, 150, 0.7)]
    ground = sy(GROUND_Y)                                   # 295
    # distant hills + skyline
    p.append('<path d="M0 %.0f C60 %.0f 120 %.0f 200 %.0f S360 %.0f 480 %.0f L480 %.0f L0 %.0f Z" fill="#9fd4c4" fill-opacity="0.8"/>'
             % (ground - 62, ground - 92, ground - 52, ground - 74, ground - 98, ground - 66, ground, ground))
    far = [(118, 30, 74), (142, 22, 52), (296, 28, 66), (326, 20, 90), (352, 26, 58)]
    for x, w, h in far:
        p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#a4c6e4" fill-opacity="0.85"/>' % (x, ground - h, w, h))
        p.append(_windows(x + 5, ground - h + 8, max(1, (w - 8) // 12), max(1, (h - 14) // 22), 7, 9, 5, 12, color="#c8e2f4", frame="#d8ecf8"))
    p.append('<path d="M326 %d l10 -22 l10 22 z" fill="#8fb4d6"/>' % (ground - 90))          # steeple roof
    p.append('<rect x="233" y="%d" width="10" height="30" fill="#8fb4d6"/><ellipse cx="238" cy="%d" rx="17" ry="10" fill="#8fb4d6"/>' % (ground - 120, ground - 120))   # water tower
    # --- left tower (balconies at -45 and 95)
    lx, lw = 0, 130
    p.append('<rect x="%d" y="58" width="%d" height="%d" fill="#ff9d84" stroke="#c4604b" stroke-width="2"/>' % (lx, lw, ground - 58))
    p.append('<rect x="-4" y="48" width="%d" height="14" rx="3" fill="#b5483a"/><rect x="-4" y="44" width="%d" height="6" rx="3" fill="#d8665a"/>' % (lw + 8, lw + 8))
    p.append(_windows(18, 78, 4, 1, lit=(1,), shutter="#7a2e25") + _windows(18, 132, 4, 1, shutter="#7a2e25"))
    p.append(_windows(18, 218, 2, 1, lit=(0,), shutter="#7a2e25"))
    p.append('<rect x="82" y="%d" width="26" height="%d" rx="12" fill="#6b3a2a"/><rect x="85" y="%d" width="20" height="%d" rx="9" fill="#8a5240"/>' % (ground - 40, 40, ground - 37, 37))
    # --- right tower (balconies at -45 and 95)
    rx, rw = 330, 150
    p.append('<rect x="%d" y="58" width="%d" height="%d" fill="#ffd36a" stroke="#c99a2a" stroke-width="2"/>' % (rx, rw, ground - 58))
    p.append('<rect x="%d" y="48" width="%d" height="14" rx="3" fill="#2f9b95"/><rect x="%d" y="44" width="%d" height="6" rx="3" fill="#48bdb5"/>' % (rx - 4, rw + 8, rx - 4, rw + 8))
    p.append(_windows(rx + 52, 80, 3, 1, lit=(0, 2), shutter="#1f6e69") + _windows(rx + 52, 132, 3, 1, shutter="#1f6e69"))
    p.append(_windows(rx + 52, 218, 3, 1, shutter="#1f6e69", lit=(2,)))
    p.append('<rect x="%d" y="%d" width="26" height="40" rx="12" fill="#2a6f6a"/><rect x="%d" y="%d" width="20" height="37" rx="9" fill="#3f8f89"/>' % (rx + 12, ground - 40, rx + 15, ground - 37))
    # --- central building: its flat roof is the middle platform (top = 25)
    mx, mw = sx(-80), 130
    mt = sy(25)
    p.append('<rect x="%.1f" y="%.1f" width="%d" height="%.1f" fill="#9ad9b8" stroke="#4f9d7d" stroke-width="2"/>' % (mx, mt, mw, ground - mt))
    p.append('<rect x="%.1f" y="%.1f" width="12" height="22" fill="#b0583e"/><rect x="%.1f" y="%.1f" width="16" height="5" fill="#7a3a28"/>' % (mx + 18, mt - 22, mx + 16, mt - 26))   # chimney
    p.append('<rect x="%.1f" y="%.1f" width="2" height="34" fill="#555"/><rect x="%.1f" y="%.1f" width="16" height="2" fill="#555"/>' % (mx + mw - 30, mt - 34, mx + mw - 37, mt - 26))   # antenna
    p.append(_windows(mx + 14, mt + 24, 4, 2, gy=14, lit=(2, 5), shutter="#3e8667"))
    p.append('<rect x="%.1f" y="%.0f" width="36" height="46" rx="3" fill="#5a3b72"/><rect x="%.1f" y="%.0f" width="30" height="40" rx="2" fill="#7a56a0"/><circle cx="%.1f" cy="%.0f" r="2" fill="#ffd23f"/>' % (mx + 47, ground - 46, mx + 50, ground - 43, mx + 76, ground - 22))
    # shop awning
    for i in range(6):
        p.append('<path d="M%.1f %.0f h13 l-3 14 h-13 z" fill="%s"/>' % (mx + 10 + i * 18, ground - 62, "#ff5d6c" if i % 2 == 0 else "#ffffff"))
    # platforms (roof edge + balconies) -- exact positions used by the scripts
    for nm, l, r, top in PLATFORMS:
        if nm == "Middle roof":
            x0, wid = sx(l), r - l
            p.append('<rect x="%.1f" y="%.1f" width="%d" height="10" rx="2.5" fill="#6f8f80" stroke="#3b5a4c" stroke-width="1.6"/>'
                     '<rect x="%.1f" y="%.1f" width="%d" height="3.5" rx="1.7" fill="#d5ecdd"/>' % (mx - 4, mt, mw + 8, mx - 2, mt + 0.8, mw + 4))
        else:
            p.append(_plank(l, r, top))
    # street: sidewalk, curb, road, markings
    p.append('<rect y="%.0f" width="480" height="12" fill="#cfd8e0"/><rect y="%.0f" width="480" height="3" fill="#f2f6f9"/>' % (ground, ground))
    p.append('<rect y="%.0f" width="480" height="3" fill="#9aa7b5"/>' % (ground + 12))
    p.append('<rect y="%.0f" width="480" height="%.0f" fill="url(#road)"/>' % (ground + 15, 360 - ground - 15))
    for x in range(8, 480, 56):
        p.append('<rect x="%d" y="%.0f" width="30" height="4" rx="2" fill="#ffd23f" fill-opacity="0.9"/>' % (x, ground + 36))
    # street furniture: lamp posts, hydrant, flood-warning sign, bush
    for lxp in (148, 304):
        p.append('<rect x="%d" y="%.0f" width="4" height="70" fill="#3b4656"/><path d="M%d %.0f q10 -4 18 4" stroke="#3b4656" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
                 '<ellipse cx="%d" cy="%.0f" rx="7" ry="4" fill="#ffe27a"/>' % (lxp, ground - 70, lxp + 2, ground - 72, lxp + 20, ground - 66))
    p.append('<rect x="272" y="%.0f" width="12" height="17" rx="4" fill="#e63946"/><rect x="269" y="%.0f" width="18" height="5" rx="2" fill="#c42a38"/><circle cx="278" cy="%.0f" r="2.5" fill="#ffd23f"/>' % (ground - 17, ground - 14, ground - 9))
    p.append('<rect x="109" y="%.0f" width="4" height="60" fill="#555"/><path d="M111 %.0f l22 22 l-22 22 l-22 -22 z" fill="#ffd23f" stroke="#2b2b2b" stroke-width="2.4" stroke-linejoin="round"/>'
             '<path d="M99 %.0f q4 -5 8 0 t8 0 t8 0" stroke="#2b2b2b" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
             '<path d="M99 %.0f q4 -5 8 0 t8 0 t8 0" stroke="#2b2b2b" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
             % (ground - 60, ground - 76, ground - 55, ground - 47))
    p.append('<ellipse cx="236" cy="%.0f" rx="22" ry="12" fill="#58b368"/><ellipse cx="224" cy="%.0f" rx="14" ry="9" fill="#6cc87c"/>' % (ground - 8, ground - 6))
    return svg_doc(480, 360, "".join(p))


# ---------------------------------------------------------------------------
# Rescue Runner character (faces right; Scratch flips it when walking left)
# ---------------------------------------------------------------------------
import math

RW, RH = 64, 80            # costume canvas; rotation centre = feet (32, 80)
LEG, ARM = 24, 17
SKIN, HELMET, VEST, PANTS, BOOT = "#f7c59f", "#ffd23f", "#ff8a1f", "#2b4c9b", "#4b3426"
SLEEVE, GLOVE, PACK, REFLECT = "#5db7ff", "#ffd23f", "#e63946", "#eef3f7"


def _limb(px, py, ang, length, width, color, tip):
    """A limb hanging from pivot (px,py), rotated by ang degrees (0 = straight down)."""
    return ('<g transform="rotate(%.1f %.1f %.1f)">'
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s" stroke-linecap="round"/>%s</g>'
            % (ang, px, py, px, py, px, py + length, color, width, tip))


def _leg(px, py, ang, back=False):
    boot = '<ellipse cx="%.1f" cy="%.1f" rx="8.5" ry="4.6" fill="%s"/>' % (px + 3, py + LEG + 0.4, BOOT)
    return _limb(px, py, ang, LEG, 9, "#233f86" if back else PANTS, boot)


def _arm(px, py, ang, back=False):
    hand = '<circle cx="%.1f" cy="%.1f" r="4.6" fill="%s"/>' % (px, py + ARM, GLOVE)
    return _limb(px, py, ang, ARM, 7.5, "#3d97e0" if back else SLEEVE, hand)


def runner_svg(front_leg=0, back_leg=0, front_arm=0, back_arm=0, face="smile", lean=0, lift=0):
    cosl = max(math.cos(math.radians(front_leg)), math.cos(math.radians(back_leg)))
    hip_y = RH - 4.6 - LEG * cosl - lift
    hx = 33
    sh_y = hip_y - 24                      # shoulder height
    head_y = sh_y - 12
    body = []
    body.append(_arm(hx - 1, sh_y + 3, back_arm, back=True))
    body.append(_leg(hx - 3, hip_y, back_leg, back=True))
    # backpack
    body.append('<rect x="15" y="%.1f" width="11" height="18" rx="4" fill="%s"/>'
                '<rect x="19.5" y="%.1f" width="2.4" height="9" fill="#fff"/><rect x="16.2" y="%.1f" width="9" height="2.4" fill="#fff"/>'
                % (sh_y + 2, PACK, sh_y + 6, sh_y + 9.3))
    # torso: orange vest over blue shirt, reflective stripes
    tx = "rotate(%.1f %.1f %.1f)" % (lean, hx, hip_y)
    body.append('<g transform="%s">' % tx)
    body.append('<rect x="22" y="%.1f" width="22" height="%.1f" rx="7" fill="%s"/>' % (sh_y - 2, hip_y - sh_y + 7, VEST))
    body.append('<rect x="22" y="%.1f" width="22" height="3" fill="%s"/>' % (sh_y + 7, REFLECT))
    body.append('<rect x="22" y="%.1f" width="22" height="3" fill="%s"/>' % (sh_y + 15, REFLECT))
    body.append('<rect x="32" y="%.1f" width="2" height="%.1f" fill="#d96a0a"/>' % (sh_y - 1, hip_y - sh_y + 5))
    body.append('<rect x="21" y="%.1f" width="24" height="5" rx="2" fill="%s"/>' % (hip_y + 1, PANTS))
    # head
    cx, cy = 34, head_y
    body.append('<circle cx="%.1f" cy="%.1f" r="11.5" fill="%s"/>' % (cx, cy, SKIN))
    body.append('<path d="M%.1f %.1f a11.8 11.8 0 0 1 23.6 0 z" fill="%s"/>' % (cx - 11.8, cy - 1.5, HELMET))
    body.append('<rect x="%.1f" y="%.1f" width="25" height="3.2" rx="1.6" fill="#f0b400"/>' % (cx - 12.5, cy - 2.6))
    body.append('<rect x="%.1f" y="%.1f" width="3.4" height="9" fill="#fff" fill-opacity="0.85"/>' % (cx - 1.7, cy - 12.6))
    body.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#fff"/>'
                '<rect x="%.1f" y="%.1f" width="2" height="5.4" fill="%s"/><rect x="%.1f" y="%.1f" width="5.4" height="2" fill="%s"/>'
                % (cx + 3, cy - 8.2, cx + 2, cy - 10.9, PACK, cx + 0.3, cy - 9.2, PACK))
    ex = cx + 4.5
    if face == "open":      # cheering
        body.append('<circle cx="%.1f" cy="%.1f" r="1.9" fill="#222"/><circle cx="%.1f" cy="%.1f" r="1.9" fill="#222"/>' % (ex - 1, cy + 2, ex + 6, cy + 2))
        body.append('<path d="M%.1f %.1f q4 8 8 0 z" fill="#7a1f1f"/>' % (ex - 1, cy + 6))
    elif face == "worry":
        body.append('<circle cx="%.1f" cy="%.1f" r="2.1" fill="#222"/><circle cx="%.1f" cy="%.1f" r="2.1" fill="#222"/>' % (ex - 1, cy + 2.4, ex + 6, cy + 2.4))
        body.append('<path d="M%.1f %.1f l4 -2 M%.1f %.1f l-4 -2" stroke="#4b3426" stroke-width="1.6" fill="none"/>' % (ex - 3, cy - 1.6, ex + 8, cy - 1.6))
        body.append('<ellipse cx="%.1f" cy="%.1f" rx="2.2" ry="2.8" fill="#7a1f1f"/>' % (ex + 3, cy + 8))
    else:
        body.append('<circle cx="%.1f" cy="%.1f" r="1.9" fill="#222"/><circle cx="%.1f" cy="%.1f" r="1.9" fill="#222"/>' % (ex - 1, cy + 2, ex + 6, cy + 2))
        body.append('<path d="M%.1f %.1f q3.5 4 7 0" stroke="#7a1f1f" stroke-width="1.7" fill="none" stroke-linecap="round"/>' % (ex - 0.5, cy + 6.5))
    body.append('<circle cx="%.1f" cy="%.1f" r="2.4" fill="#ff9a8a" fill-opacity="0.7"/>' % (ex + 8.5, cy + 6))
    body.append('</g>')
    body.append(_leg(hx + 3, hip_y, front_leg))
    body.append(_arm(hx + 1, sh_y + 3, front_arm))
    return svg_doc(RW, RH, "".join(body))


def runner_costumes():
    """name -> svg bytes.  Walk cycle = 6 frames of a sine swing."""
    frames = {}
    frames["idle"] = runner_svg(front_leg=3, back_leg=-3, front_arm=4, back_arm=-4)
    for k in range(6):
        ph = 2 * math.pi * k / 6
        a = 36 * math.sin(ph)
        frames["walk %d" % (k + 1)] = runner_svg(front_leg=a, back_leg=-a, front_arm=-a * 1.1, back_arm=a * 1.1,
                                                 lean=4, lift=0)
    frames["jump"] = runner_svg(front_leg=-38, back_leg=22, front_arm=150, back_arm=165, face="open", lean=6, lift=3)
    frames["fall"] = runner_svg(front_leg=-14, back_leg=14, front_arm=-80, back_arm=80, lean=-3, lift=3)
    frames["cheer"] = runner_svg(front_leg=6, back_leg=-6, front_arm=172, back_arm=-172, face="open", lift=0)
    frames["oops"] = runner_svg(front_leg=8, back_leg=-8, front_arm=-130, back_arm=130, face="worry", lift=0)
    return frames


# ---------------------------------------------------------------------------
# Emergency supply crate
# ---------------------------------------------------------------------------
def crate(x, y, scale=1.0):
    """The red first-aid supply crate, drawn in a 40 x 36 box at (x, y)."""
    return (
        '<g transform="translate(%.2f %.2f) scale(%.3f)">'
        '<defs><linearGradient id="cr" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#ff5d6c"/><stop offset="1" stop-color="#c42a38"/></linearGradient></defs>'
        '<rect x="12.5" y="1.5" width="15" height="9" rx="4.5" fill="none" stroke="#5b3a1e" stroke-width="3"/>'
        '<rect x="2" y="8" width="36" height="27" rx="5.5" fill="url(#cr)" stroke="#8f1f2a" stroke-width="1.6"/>'
        '<rect x="5" y="8.8" width="4.2" height="25.4" fill="#ffd23f"/><rect x="30.8" y="8.8" width="4.2" height="25.4" fill="#ffd23f"/>'
        '<rect x="3.2" y="9.2" width="14" height="4" rx="2" fill="#fff" fill-opacity="0.35"/>'
        '<circle cx="20" cy="21.5" r="9.2" fill="#fff"/>'
        '<rect x="17.6" y="15.2" width="4.8" height="12.6" rx="1" fill="#e63946"/>'
        '<rect x="13.7" y="19.1" width="12.6" height="4.8" rx="1" fill="#e63946"/>'
        '<circle cx="7.1" cy="30.5" r="1.1" fill="#8f1f2a"/><circle cx="32.9" cy="30.5" r="1.1" fill="#8f1f2a"/>'
        '</g>' % (x, y, scale))


SW = 56   # supply costume canvas (square); rotation centre = middle


def supply_costumes():
    out = {}
    for i, (glow, sc) in enumerate([(0.30, 1.0), (0.50, 1.04), (0.65, 1.08), (0.50, 1.04)]):
        k = SW / 2
        w, h = 40 * 1.0 * sc, 36 * sc
        out["supply %d" % (i + 1)] = svg_doc(SW, SW,
            '<defs><radialGradient id="gl"><stop offset="0.45" stop-color="#fff6a8" stop-opacity="%.2f"/>'
            '<stop offset="1" stop-color="#fff6a8" stop-opacity="0"/></radialGradient></defs>'
            '<circle cx="%s" cy="%s" r="22" fill="url(#gl)"/>%s' % (glow, k, k, crate(k - w / 2, k - h / 2 + 1, sc)))
    pts = []
    for j in range(16):
        r = 26 if j % 2 == 0 else 11
        ang = math.pi * j / 8 - math.pi / 2
        pts.append("%.1f,%.1f" % (28 + r * math.cos(ang), 28 + r * math.sin(ang)))
    inner = []
    for j in range(16):
        r = 15 if j % 2 == 0 else 6
        ang = math.pi * j / 8 - math.pi / 2
        inner.append("%.1f,%.1f" % (28 + r * math.cos(ang), 28 + r * math.sin(ang)))
    out["burst"] = svg_doc(SW, SW,
        '<polygon points="%s" fill="#ffd23f" stroke="#ff9f1c" stroke-width="2" stroke-linejoin="round"/>'
        '<polygon points="%s" fill="#fff" fill-opacity="0.9"/>' % (" ".join(pts), " ".join(inner)))
    return out


# ---------------------------------------------------------------------------
# Heads-up display (one costume per score, drawn on a transparent full-stage canvas)
# ---------------------------------------------------------------------------
def hud(n):
    """Scoreboard pill, top-centre (no supply spot or platform is hidden behind it)."""
    ox = 135
    pips = "".join('<rect x="%d" y="45" width="11" height="6" rx="3" fill="%s" fill-opacity="%s"/>'
                   % (ox + 52 + i * 14, "#ffd23f" if i < n else "#ffffff", 1 if i < n else 0.28) for i in range(SUPPLIES_TO_WIN))
    inner = (
        '<rect x="%d" y="7" width="210" height="52" rx="15" fill="#0f2f57" fill-opacity="0.88" stroke="#ffffff" stroke-opacity="0.9" stroke-width="2"/>' % ox
        + crate(ox + 8, 15, 1.0) +
        '<text x="%d" y="32" font-family="Sans Serif" font-size="12" font-weight="bold" fill="#9fd8ff">SUPPLIES</text>' % (ox + 54)
        + '<text x="%d" y="36" font-family="Marker" font-size="25" fill="%s" text-anchor="end">%d/%d</text>' % (ox + 202, "#ffd23f" if n < SUPPLIES_TO_WIN else "#7dff9a", n, SUPPLIES_TO_WIN)
        + pips
        + '<rect x="352" y="6" width="124" height="22" rx="11" fill="#0f2f57" fill-opacity="0.8"/>'
        + '<text x="414" y="21" font-family="Sans Serif" font-size="9.5" font-weight="bold" fill="#ffffff" text-anchor="middle">ARROWS move - SPACE jump</text>')
    return svg_doc(480, 360, inner)


# ---------------------------------------------------------------------------
# Floodwater: 6 wave frames.  Rotation centre (WCX, WCY) is the water surface,
# so "go to x: 0 y: Water Level" puts the surface exactly at Water Level.
# ---------------------------------------------------------------------------
WW, WH, WCX, WCY = 520, 420, 260, 16
WAVE_FRAMES = 6


def _wave_path(phase, amp, wavelength, y0, close_to=WH):
    pts = []
    x = 0
    while x <= WW + 1:
        y = y0 + amp * math.sin(2 * math.pi * x / wavelength + phase)
        pts.append("%.1f %.1f" % (x, y))
        x += 4
    return "M" + " L".join(pts), pts


def water_costumes():
    out = {}
    for k in range(WAVE_FRAMES):
        ph = 2 * math.pi * k / WAVE_FRAMES
        back, _ = _wave_path(ph + 1.9, 6.5, 78, WCY - 4)
        front, pts = _wave_path(-ph, 5, 52, WCY)
        parts = ['<defs><linearGradient id="wb" x1="0" y1="0" x2="0" y2="1">'
                 '<stop offset="0" stop-color="#58c4ff" stop-opacity="0.72"/>'
                 '<stop offset="0.35" stop-color="#2a9bf5" stop-opacity="0.78"/>'
                 '<stop offset="1" stop-color="#0b4fb8" stop-opacity="0.88"/></linearGradient></defs>']
        parts.append('<path d="%s L%d %d L0 %d Z" fill="#9fe0ff" fill-opacity="0.55"/>' % (back, WW, WH, WH))
        parts.append('<path d="%s L%d %d L0 %d Z" fill="url(#wb)"/>' % (front, WW, WH, WH))
        parts.append('<path d="%s" fill="none" stroke="#ffffff" stroke-opacity="0.85" stroke-width="2.6" stroke-linejoin="round"/>' % front)
        # light streaks and bubbles that slide with the wave so the surface seems to flow
        for j in range(7):
            sx = (j * 83 + k * 14) % WW
            parts.append('<rect x="%d" y="%d" width="%d" height="2.4" rx="1.2" fill="#fff" fill-opacity="0.32"/>' % (sx, WCY + 22 + (j % 3) * 15, 26 + (j % 2) * 14))
        for j in range(5):
            bx = (j * 107 + 30 + k * 9) % WW
            parts.append('<circle cx="%d" cy="%d" r="%s" fill="none" stroke="#fff" stroke-opacity="0.45" stroke-width="1.4"/>' % (bx, WCY + 58 + (j * 23) % 70, 2.5 + j % 3))
        out["wave %d" % (k + 1)] = svg_doc(WW, WH, "".join(parts))
    return out


def _key(x, y, label, w=30):
    return ('<rect x="%.1f" y="%.1f" width="%d" height="26" rx="6" fill="#e9f1f8" stroke="#8fa6bd" stroke-width="2"/>'
            '<rect x="%.1f" y="%.1f" width="%d" height="20" rx="4" fill="#ffffff"/>%s' % (x, y, w, x + 2, y + 2, w - 4, label))


def _arrow(x, y, direction):
    cx, cy = x + 15, y + 13
    d = -1 if direction == "left" else 1
    return '<path d="M%.1f %.1f l%.1f -7 v14 z" fill="#0f2f57"/>' % (cx + d * 6, cy, -d * 11)


def _stars(cx, cy, n=5, r=13, gap=34):
    out = []
    x0 = cx - (n - 1) * gap / 2
    for i in range(n):
        pts = []
        for j in range(10):
            rr = r if j % 2 == 0 else r * 0.45
            ang = math.pi * j / 5 - math.pi / 2
            pts.append("%.1f,%.1f" % (x0 + i * gap + rr * math.cos(ang), cy + (-6 if i in (0, 4) else 0) + (-4 if i in (1, 3) else 0) + rr * math.sin(ang)))
        out.append('<polygon points="%s" fill="#ffd23f" stroke="#c98a00" stroke-width="2" stroke-linejoin="round"/>' % " ".join(pts))
    return "".join(out)


def _confetti(seed=3):
    cols = ["#ff5d6c", "#ffd23f", "#48bdb5", "#7dff9a", "#9d7bff", "#ff9d3f"]
    out = []
    for i in range(46):
        x = (i * 97 + seed * 31) % 470 + 5
        y = (i * 53 + seed * 17) % 340 + 8
        if 60 < x < 420 and 30 < y < 330 and i % 3:
            continue
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="1.5" fill="%s" transform="rotate(%d %d %d)"/>'
                   % (x, y, 7, 11, cols[i % 6], (i * 37) % 180, x, y))
    return "".join(out)


def _card(color):
    return ('<rect x="70" y="30" width="340" height="300" rx="24" fill="#0f2f57" fill-opacity="0.95" stroke="%s" stroke-width="4"/>'
            '<rect x="78" y="38" width="324" height="284" rx="18" fill="none" stroke="#ffffff" stroke-opacity="0.18" stroke-width="2"/>' % color)


def _button(text, y=272, fill="#ffd23f"):
    return ('<rect x="110" y="%d" width="260" height="38" rx="19" fill="%s" stroke="#b97d00" stroke-width="2.5"/>'
            '<text x="240" y="%d" font-family="Sans Serif" font-size="18" font-weight="bold" fill="#0f2f57" text-anchor="middle">%s</text>'
            % (y, fill, y + 25, text))


def _title_text(text, y, size, fill, stroke):
    return ('<text x="240" y="%d" font-family="Marker" font-size="%d" fill="%s" stroke="%s" stroke-width="7" stroke-linejoin="round" '
            'text-anchor="middle" paint-order="stroke">%s</text>' % (y, size, fill, stroke, text))


def title_card():
    inner = (_card("#ffd23f") +
             crate(92, 54, 1.0) + crate(348, 54, 1.0) +
             _title_text("RESCUE", 108, 50, "#ffd23f", "#8a4b00") +
             _title_text("RUNNER", 160, 50, "#ff8a1f", "#6b2a00") +
             '<text x="240" y="190" font-family="Sans Serif" font-size="15" font-weight="bold" fill="#cfeaff" text-anchor="middle">Collect 10 emergency supplies</text>'
             '<text x="240" y="210" font-family="Sans Serif" font-size="15" font-weight="bold" fill="#cfeaff" text-anchor="middle">before the flood reaches the top!</text>' +
             _key(110, 226, _arrow(110, 226, "left")) + _key(144, 226, _arrow(144, 226, "right")) +
             '<text x="184" y="245" font-family="Sans Serif" font-size="14" font-weight="bold" fill="#ffffff">move</text>' +
             _key(240, 226, '<text x="%d" y="%d" font-family="Sans Serif" font-size="12" font-weight="bold" fill="#0f2f57" text-anchor="middle">SPACE</text>' % (240 + 29, 226 + 17), w=58) +
             '<text x="308" y="245" font-family="Sans Serif" font-size="14" font-weight="bold" fill="#ffffff">jump</text>' +
             _button("Press SPACE to start"))
    return svg_doc(480, 360, inner)


def win_card():
    inner = (_confetti() + _card("#7dff9a") + _stars(240, 82) +
             _title_text("YOU DID IT!", 150, 48, "#7dff9a", "#0b5a25") +
             '<text x="240" y="186" font-family="Sans Serif" font-size="16" font-weight="bold" fill="#ffffff" text-anchor="middle">All 10 supplies delivered.</text>'
             '<text x="240" y="208" font-family="Sans Serif" font-size="16" font-weight="bold" fill="#cfeaff" text-anchor="middle">The village is safe!</text>' +
             crate(100, 218, 0.9) + crate(344, 218, 0.9) +
             _button("Press SPACE to play again", fill="#7dff9a"))
    return svg_doc(480, 360, inner)


def lose_card():
    waves = "".join('<path d="M%d 250 q10 -9 20 0 t20 0 t20 0" stroke="#58c4ff" stroke-width="3" fill="none" stroke-linecap="round"/>' % (x) for x in (96, 316))
    drops = ('<path d="M240 52 c-14 22 -22 32 -22 44 a22 22 0 0 0 44 0 c0 -12 -8 -22 -22 -44 z" fill="#58c4ff" stroke="#ffffff" stroke-width="3" stroke-linejoin="round"/>'
             '<path d="M229 90 a11 11 0 0 0 9 11" stroke="#ffffff" stroke-width="3" fill="none" stroke-linecap="round" stroke-opacity="0.8"/>')
    inner = (_card("#ff7a6b") + drops + waves +
             _title_text("FLOODED!", 156, 50, "#ff8f80", "#7a1a12") +
             '<text x="240" y="188" font-family="Sans Serif" font-size="16" font-weight="bold" fill="#ffffff" text-anchor="middle">The water reached the top.</text>'
             '<text x="240" y="210" font-family="Sans Serif" font-size="16" font-weight="bold" fill="#cfeaff" text-anchor="middle">Don\'t give up - try again!</text>' +
             _button("Press SPACE to try again", fill="#ffd23f"))
    return svg_doc(480, 360, inner)


