#!/usr/bin/env python3
"""Generate the HUB application icon as a real PNG, in pure python.

No PIL: an RGBA buffer is built pixel-by-pixel, then encoded manually into a
PNG (struct + zlib): IHDR / IDAT / IEND chunks, CRC-32 via zlib.crc32.

Icon design: dark blue vertical gradient background + white 2x2 grid of
rounded squares ("hub" logo) centered.
"""

import struct
import sys
import zlib

W = H = 512

# --- palette -------------------------------------------------------------
TOP = (24, 52, 118)      # dark blue, top of gradient
BOTTOM = (7, 13, 36)     # near-black blue, bottom of gradient
WHITE = (255, 255, 255)

# --- 2x2 white tile grid geometry ----------------------------------------
TILE = 112               # tile side, px
GAP = 26                 # gap between tiles, px
GRID = 2 * TILE + GAP    # 250
X0 = (W - GRID) // 2     # 131
Y0 = (H - GRID) // 2
R = 24                   # corner radius of each tile

CORNERS = (
    (X0, Y0), (X0 + TILE, Y0),
    (X0, Y0 + TILE), (X0 + TILE, Y0 + TILE),
)


def tile_inside(px, py, x0, y0, r):
    """True if point (px, py) is inside the rounded square at (x0, y0)."""
    x1, y1 = x0 + TILE, y0 + TILE
    if px < x0 or px >= x1 or py < y0 or py >= y1:
        return False
    # corner regions -> circle test
    cx = r if px < x0 + r else (TILE - r if px >= x1 - r else None)
    cy = r if py < y0 + r else (TILE - r if py >= y1 - r else None)
    if cx is None or cy is None:
        return True
    dx, dy = px - (x0 + cx), py - (y0 + cy)
    return dx * dx + dy * dy <= r * r


def coverage(px, py, subs=3):
    """Anti-aliased coverage of pixel (px, py) by the white grid (0..1)."""
    hits = 0
    for sy in range(subs):
        for sx in range(subs):
            sxp = px + (sx + 0.5) / subs
            syp = py + (sy + 0.5) / subs
            for x0, y0 in CORNERS:
                if tile_inside(sxp, syp, x0, y0, R):
                    hits += 1
                    break
    return hits / (subs * subs)


def render(path):
    rows = []
    for y in range(H):
        t = y / (H - 1)  # 0 top -> 1 bottom
        br = TOP[0] + (BOTTOM[0] - TOP[0]) * t
        bg = TOP[1] + (BOTTOM[1] - TOP[1]) * t
        bb = TOP[2] + (BOTTOM[2] - TOP[2]) * t
        row = bytearray()
        for x in range(W):
            a = coverage(x, y)
            if a == 0.0:
                row += bytes((int(br), int(bg), int(bb), 255))
            elif a == 1.0:
                row += bytes(WHITE + (255,))
            else:
                row += bytes((
                    int(WHITE[0] * a + br * (1 - a)),
                    int(WHITE[1] * a + bg * (1 - a)),
                    int(WHITE[2] * a + bb * (1 - a)),
                    255,
                ))
        rows.append(bytes(row))

    # --- PNG encoding (manual, struct + zlib) ----------------------------
    def chunk(ctype, data):
        crc = zlib.crc32(ctype + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + ctype + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0)  # 8-bit RGBA
    raw = b"".join(b"\x00" + r for r in rows)            # filter 0 per scanline
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(png)
    print(f"wrote {path}: {len(png)} bytes ({W}x{H} RGBA)")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "hub.png"
    render(out)
