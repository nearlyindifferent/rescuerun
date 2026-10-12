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


def player():
    inner = ('<rect x="14" y="26" width="20" height="30" rx="4" fill="#ff7a1a"/>'
             '<circle cx="24" cy="16" r="11" fill="#ffd2a8"/>'
             '<rect x="14" y="52" width="20" height="12" fill="#2a4d9b"/>')
    return svg_doc(48, 64, inner), 24, 64


def supply():
    inner = '<rect x="4" y="4" width="32" height="32" rx="4" fill="#e63946"/><rect x="17" y="9" width="6" height="22" fill="#fff"/><rect x="9" y="17" width="22" height="6" fill="#fff"/>'
    return svg_doc(40, 40, inner), 20, 20


def water():
    return svg_doc(500, 400, '<rect y="14" width="500" height="386" fill="#1c8ef0" fill-opacity="0.75"/>'), 250, 14


def screen(title, sub):
    inner = ('<rect x="60" y="80" width="360" height="200" rx="16" fill="#12315a" fill-opacity="0.9"/>'
             '<text x="240" y="150" font-family="Sans Serif" font-size="34" font-weight="bold" fill="#ffd23f" text-anchor="middle">%s</text>'
             '<text x="240" y="200" font-family="Sans Serif" font-size="16" fill="#fff" text-anchor="middle">%s</text>' % (title, sub))
    return svg_doc(480, 360, inner), 240, 180
