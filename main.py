#!/usr/bin/env python3
"""The picture that tastes of one ingredient: one ripe strawberry.

Pure Python 3 stdlib only (zlib + struct for the PNG encoder).
Deterministic: fixed seed / fixed geometry, no timestamps, no network.
Writes one 1024x1024 PNG to /output/entry.png (or $ENTRY_OUTPUT).
"""
import math
import os
import struct
import zlib

W = 1024
H = 1024
OUT = os.environ.get("ENTRY_OUTPUT", "/output/entry.png")

# Deterministic pseudo-random (LCG) for the faint skin speckle.
_seed = [1234567]


def rnd():
    _seed[0] = (_seed[0] * 1103515245 + 12345) & 0x7FFFFFFF
    return _seed[0] / 2147483648.0


# ---------------------------------------------------------------- buffer
buf = bytearray(W * H * 3)


def blend(x, y, r, g, b, a):
    """Alpha-blend one pixel (a in 0..1)."""
    if x < 0 or x >= W or y < 0 or y >= H:
        return
    i = (y * W + x) * 3
    ia = 1.0 - a
    buf[i] = int(buf[i] * ia + r * a + 0.5)
    buf[i + 1] = int(buf[i + 1] * ia + g * a + 0.5)
    buf[i + 2] = int(buf[i + 2] * ia + b * a + 0.5)


def set_px(x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b


# ------------------------------------------------------- background
# Warm cream radial gradient, lighter near top-centre, deeper at edges.
BCX, BCY = 512.0, 360.0
L_R, L_G, L_B = 253, 246, 228
E_R, E_G, E_B = 231, 208, 172
DR, DG, DB = E_R - L_R, E_G - L_G, E_B - L_B
INV_R = 1.0 / (760.0 * 760.0)
dx2 = [(x - BCX) * (x - BCX) for x in range(W)]
for y in range(H):
    dy = y - BCY
    dy2 = dy * dy
    row = y * W * 3
    for x in range(W):
        t = (dx2[x] + dy2) * INV_R
        if t > 1.0:
            t = 1.0
        t = t * t * (3.0 - 2.0 * t)  # smoothstep
        buf[row] = int(L_R + DR * t + 0.5)
        buf[row + 1] = int(L_G + DG * t + 0.5)
        buf[row + 2] = int(L_B + DB * t + 0.5)
        row += 3

# ------------------------------------------------------- drop shadow
# Soft elliptical shadow beneath the berry.
SH_CX, SH_CY, SH_RX, SH_RY = 512.0, 912.0, 300.0, 44.0
for y in range(862, 962):
    ny = (y - SH_CY) / SH_RY
    ny2 = ny * ny
    if ny2 >= 1.0:
        continue
    half = SH_RX * math.sqrt(1.0 - ny2)
    for x in range(int(SH_CX - half), int(SH_CX + half) + 1):
        nx = (x - SH_CX) / SH_RX
        d2 = nx * nx + ny2
        if d2 >= 1.0:
            continue
        a = 0.30 * (1.0 - d2) * (1.0 - d2)
        blend(x, y, 120, 70, 40, a)

# ------------------------------------------------------- berry body
CX = 512.0
TOP, BOT = 235.0, 905.0
SPAN = BOT - TOP


def half_width(y):
    """Half-width of the berry at row y (classic heart/cone profile)."""
    v = (y - TOP) / SPAN
    if v < 0.0:
        v = 0.0
    elif v > 1.0:
        v = 1.0
    f = (1.0 - v ** 2.2) ** 0.55
    # Rounded shoulders: much narrower at the very top, swelling quickly
    # to full width so the top is a dome, not a flat edge.
    f *= 0.55 + 0.45 * min(1.0, v / 0.18)
    return 312.0 * f


for y in range(235, 906):
    hw = half_width(y)
    if hw < 1.0:
        continue
    ny = (y - 545.0) / 345.0
    x0 = int(CX - hw)
    x1 = int(CX + hw)
    row = y * W * 3
    for x in range(x0, x1 + 1):
        nx = (x - CX) / hw
        if nx * nx > 1.0:
            continue
        # Light from upper-left.
        lum = 0.60 - 0.36 * nx - 0.17 * ny
        if lum < 0.0:
            lum = 0.0
        elif lum > 1.0:
            lum = 1.0
        # Darken toward the rim for roundness.
        ed = nx * nx * 0.85 + ny * ny * 0.55
        if ed > 0.55:
            lum *= 1.0 - 0.30 * (ed - 0.55) / 0.45
        r = int(148 + 108 * lum)
        g = int(16 + 48 * lum)
        b = int(10 + 34 * lum)
        # Fine darker-red speckle (deterministic, sparse, subtle).
        h = (x * 73 + y * 149) % 97
        if h < 6:
            r -= 14
            g -= 4
            b -= 2
            if r < 0:
                r = 0
        i = row + x * 3
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b

# ------------------------------------------------------- seeds (achenes)
# Diagonal rows following the berry curve; dimple + pale-yellow seed.
seeds = []
row_y = 330
row_i = 0
while row_y <= 830:
    hw = half_width(row_y)
    shift = 31 if (row_i % 2) else 0
    x = CX - hw * 0.82 + shift
    while x <= CX + hw * 0.82:
        nx = (x - CX) / hw
        if abs(nx) < 0.85:
            seeds.append((int(x), row_y))
        x += 68
    row_y += 56
    row_i += 1

for (sx, sy) in seeds:
    # Shallow dimple: darker red ellipse, offset slightly down.
    for dy in range(-14, 15):
        for dx in range(-11, 12):
            if (dx / 11.0) ** 2 + (dy / 14.0) ** 2 <= 1.0:
                blend(sx + dx, sy + dy + 3, 110, 12, 8, 0.55)
    # Pale-yellow seed ellipse.
    for dy in range(-11, 12):
        for dx in range(-8, 9):
            if (dx / 8.0) ** 2 + (dy / 11.0) ** 2 <= 1.0:
                a = 0.95
                # Tiny bright tip on the upper-left of the seed.
                if dx < -3 and dy < -4:
                    blend(sx + dx, sy + dy, 255, 244, 180, 1.0)
                else:
                    blend(sx + dx, sy + dy, 244, 226, 138, a)

# ------------------------------------------------------- gloss highlights
for (hx, hy, hr, ha) in ((395, 365, 135, 0.34), (455, 305, 85, 0.26),
                         (355, 480, 62, 0.17), (600, 330, 55, 0.12)):
    for y in range(hy - hr, hy + hr + 1):
        for x in range(hx - hr, hx + hr + 1):
            d2 = ((x - hx) / hr) ** 2 + ((y - hy) / hr) ** 2
            if d2 >= 1.0:
                continue
            # Only gloss where the berry actually is.
            if y < 235 or y > 905:
                continue
            if abs(x - CX) > half_width(y):
                continue
            a = ha * (1.0 - d2) * (1.0 - d2)
            blend(x, y, 255, 235, 225, a)

# ------------------------------------------------------- water droplets
for (dx0, dy0, dr) in ((432, 482, 14), (592, 422, 11), (522, 622, 12),
                       (382, 602, 9), (642, 562, 10), (470, 700, 8)):
    for y in range(dy0 - dr, dy0 + dr + 1):
        for x in range(dx0 - dr, dx0 + dr + 1):
            d2 = ((x - dx0) / dr) ** 2 + ((y - dy0) / dr) ** 2
            if d2 >= 1.0:
                continue
            blend(x, y, 205, 232, 244, 0.50 * (1.0 - d2 * 0.6))
    # White specular dot, upper-left of each droplet.
    for y in range(dy0 - dr // 2 - 2, dy0 - dr // 2 + 3):
        for x in range(dx0 - dr // 2 - 2, dx0 - dr // 2 + 3):
            if (x - (dx0 - dr // 2)) ** 2 + (y - (dy0 - dr // 2)) ** 2 <= 9:
                blend(x, y, 255, 255, 255, 0.9)

# ------------------------------------------------------- calyx leaves
# 6 pointed leaves fanning from the top of the berry, layered greens.
LEAVES = [
    (-0.98, -0.30, 185, 62, (46, 96, 32)),
    (-0.72, -0.72, 195, 66, (58, 112, 38)),
    (-0.30, -0.96, 185, 60, (70, 128, 44)),
    (0.18, -0.99, 180, 60, (58, 112, 38)),
    (0.62, -0.80, 185, 62, (46, 96, 32)),
    (0.95, -0.38, 175, 58, (62, 122, 46)),
]
BASE_X, BASE_Y = 512.0, 268.0
for (dx_, dy_, ln, wd, col) in LEAVES:
    n = math.hypot(dx_, dy_)
    ux, uy = dx_ / n, dy_ / n
    px, py = -uy, ux  # perpendicular
    ccx, ccy = BASE_X + ux * ln * 0.45, BASE_Y + uy * ln * 0.45
    hl, hw2 = ln * 0.55, wd * 0.5
    for y in range(int(ccy - hl), int(ccy + hl) + 1):
        for x in range(int(ccx - hl), int(ccx + hl) + 1):
            du = (x - ccx) * ux + (y - ccy) * uy
            dv = (x - ccx) * px + (y - ccy) * py
            e = (du / hl) ** 2 + (dv / hw2) ** 2
            if e >= 1.0:
                continue
            # Taper to a point at the tip.
            if du > hl * 0.55:
                if abs(dv) > hw2 * (1.0 - (du - hl * 0.55) / (hl * 0.45)) * 0.9:
                    continue
            r, g, b = col
            # Lighter centre vein.
            if abs(dv) < 3.5 and du > -hl * 0.5:
                r, g, b = min(255, r + 45), min(255, g + 55), min(255, b + 30)
            # Shade the leaf edges slightly.
            edge = 1.0 - 0.25 * e
            blend(x, y, int(r * edge), int(g * edge), int(b * edge), 0.98)
# Green cap blending the leaf bases into the berry top.
for y in range(238, 296):
    for x in range(432, 593):
        e = ((x - 512) / 82.0) ** 2 + ((y - 268) / 30.0) ** 2
        if e <= 1.0:
            blend(x, y, 56, 108, 38, 0.97)

# Stem: short, slightly tilted, brown-green.
for y in range(178, 252):
    for x in range(504, 524):
        e = ((x - 514) / 9.0) ** 2 + ((y - 215) / 38.0) ** 2
        if e <= 1.0:
            blend(x, y, 96, 116, 52, 0.98)
blend(510, 200, 150, 165, 90, 0.7)

# ------------------------------------------------------- PNG encoder
def chunk(ctype, data):
    c = struct.pack(">I", len(data)) + ctype + data
    c += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return c


raw = bytearray()
for y in range(H):
    raw.append(0)  # filter: none
    raw += buf[y * W * 3:(y + 1) * W * 3]
png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
png += chunk(b"IEND", b"")

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
with open(OUT, "wb") as f:
    f.write(png)
print("wrote %s (%d bytes)" % (OUT, len(png)))
