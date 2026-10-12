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


def backdrop():
    parts = ['<rect width="480" height="360" fill="#8fd3ff"/>',
             '<rect y="%s" width="480" height="%s" fill="#6b7a8f"/>' % (sy(GROUND_Y), 360 - sy(GROUND_Y))]
    for _, l, r, top in PLATFORMS:
        parts.append('<rect x="%s" y="%s" width="%s" height="10" fill="#b5651d"/>' % (sx(l), sy(top), r - l))
    return svg_doc(480, 360, "".join(parts))


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
            '<circle cx="%s" cy="%s" r="27" fill="url(#gl)"/>%s' % (glow, k, k, crate(k - w / 2, k - h / 2 + 1, sc)))
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
        + pips)
    return svg_doc(480, 360, inner)


def water():
    return svg_doc(500, 400, '<rect y="14" width="500" height="386" fill="#1c8ef0" fill-opacity="0.75"/>'), 250, 14


def screen(title, sub):
    inner = ('<rect x="60" y="80" width="360" height="200" rx="16" fill="#12315a" fill-opacity="0.9"/>'
             '<text x="240" y="150" font-family="Sans Serif" font-size="34" font-weight="bold" fill="#ffd23f" text-anchor="middle">%s</text>'
             '<text x="240" y="200" font-family="Sans Serif" font-size="16" fill="#fff" text-anchor="middle">%s</text>' % (title, sub))
    return svg_doc(480, 360, inner), 240, 180
