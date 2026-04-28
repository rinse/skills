"""
quiver_preview.py — Render a structural SVG preview of a Quiver diagram.

This is NOT a faithful reproduction of how q.uiver.app renders the diagram —
quiver uses KaTeX for labels and has sophisticated arrow rendering. This
preview is a sanity-check tool: it shows you where the vertices sit, which
arrows connect what, and approximately how the curves and 2-cells are laid
out. Use it to verify the diagram structure before sharing the URL.

Labels are drawn as raw LaTeX source (e.g. ``\\pi_1`` rather than π₁) so you
can spot typos.
"""

from __future__ import annotations

import html
import math
import xml.sax.saxutils as sax
from typing import Optional

# Importing internal types — this script lives next to quiver_encoder.py.
from quiver_encoder import Quiver, _Vertex, _Edge


# Layout constants
GRID_SPACING = 110     # pixels between adjacent grid cells
PADDING      = 60      # pixels of padding around the diagram
VERTEX_FONT  = 16      # px
LABEL_FONT   = 12      # px
ARROW_HEAD   = 8       # arrowhead length in px


def render_svg(quiver: Quiver, *, show_grid: bool = False) -> str:
    """Render the diagram to an SVG string.

    The SVG is a structural preview: vertex labels are shown as raw LaTeX
    source, arrows show their style/curve, and 2-cells (edges between edges)
    are drawn between the midpoints of their source and target arrows.
    """
    cells = quiver._cells
    if not cells:
        return _empty_svg()

    # Step 1: compute pixel positions for every cell.
    #   - Vertices: from their grid (x, y).
    #   - Edges: midpoint of source and target (recursively for n-cells),
    #     offset perpendicular by the edge's `curve` and `offset` parameters.
    positions = _compute_positions(cells)

    # Step 2: figure out the SVG viewport.
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width  = max_x - min_x + 2 * PADDING
    height = max_y - min_y + 2 * PADDING

    def shift(p):
        return (p[0] - min_x + PADDING, p[1] - min_y + PADDING)

    # Step 3: emit SVG.
    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width:.1f} {height:.1f}" '
        f'width="{width:.0f}" height="{height:.0f}" '
        f'font-family="serif">'
    )
    parts.append(_defs())

    if show_grid:
        parts.append(_grid(width, height))

    # Edges first (under vertices). Within edges, draw lower-level first so
    # that 2-cells are drawn on top of the 1-cells they connect.
    edge_indices = [i for i, c in enumerate(cells) if isinstance(c, _Edge)]
    edge_indices.sort(key=lambda i: _edge_level(cells, i))
    for i in edge_indices:
        parts.append(_render_edge(i, cells, positions, shift))

    # Vertices on top.
    for i, c in enumerate(cells):
        if isinstance(c, _Vertex):
            parts.append(_render_vertex(c, shift(positions[i])))

    parts.append('</svg>')
    return "".join(parts)


def render_svg_file(quiver: Quiver, path: str, *, show_grid: bool = False) -> None:
    """Write SVG to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(render_svg(quiver, show_grid=show_grid))


# -------------------------------------------------------------------------
# Position computation
# -------------------------------------------------------------------------

def _compute_positions(cells: list) -> dict[int, tuple[float, float]]:
    """Return {cell_index: (x_px, y_px)} for every cell."""
    positions: dict[int, tuple[float, float]] = {}

    # Vertices first.
    verts = [(i, c) for i, c in enumerate(cells) if isinstance(c, _Vertex)]
    if not verts:
        return positions

    min_gx = min(c.x for _, c in verts)
    min_gy = min(c.y for _, c in verts)
    for i, c in verts:
        positions[i] = ((c.x - min_gx) * GRID_SPACING,
                        (c.y - min_gy) * GRID_SPACING)

    # Edges: mid of (src, tgt), then bumped by the curve/offset.
    # Resolved in declaration order (so an edge's endpoints are always
    # already positioned before it is processed).
    for i, c in enumerate(cells):
        if isinstance(c, _Edge):
            sx, sy = positions[c.src]
            tx, ty = positions[c.tgt]
            mx, my = (sx + tx) / 2, (sy + ty) / 2

            # Offset perpendicular to the segment by curve magnitude.
            # We borrow ~10px per unit of curve, ~8px per unit of offset.
            dx, dy = tx - sx, ty - sy
            length = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / length, dx / length   # left-perpendicular
            curve = c.options.get("curve", 0)
            off   = c.options.get("offset", 0)
            mx += nx * (curve * 10 + off * 8)
            my += ny * (curve * 10 + off * 8)
            positions[i] = (mx, my)

    return positions


def _edge_level(cells: list, i: int) -> int:
    """Recursive level: 1 for an edge between vertices, +1 for each layer of
    edge-between-edges. Used so that we draw the underlying arrows first."""
    c = cells[i]
    if isinstance(c, _Vertex):
        return 0
    return max(_edge_level(cells, c.src), _edge_level(cells, c.tgt)) + 1


# -------------------------------------------------------------------------
# Rendering helpers
# -------------------------------------------------------------------------

def _empty_svg() -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 200 80" width="200" height="80" '
            'font-family="serif">'
            '<text x="100" y="44" text-anchor="middle" '
            'fill="#999">(empty diagram)</text></svg>')


def _defs() -> str:
    """Reusable arrowhead marker defs."""
    return (
        '<defs>'
        '<marker id="arrowhead" markerWidth="10" markerHeight="10" '
        'refX="9" refY="5" orient="auto" markerUnits="strokeWidth">'
        '<path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>'
        '</marker>'
        '<marker id="arrowhead-open" markerWidth="12" markerHeight="12" '
        'refX="11" refY="6" orient="auto" markerUnits="strokeWidth">'
        '<path d="M0,1 L11,6 L0,11" fill="none" stroke="currentColor" stroke-width="1.5"/>'
        '</marker>'
        '</defs>'
    )


def _grid(width: float, height: float) -> str:
    """Faint grid for reference."""
    lines: list[str] = []
    for x in range(0, int(width) + 1, GRID_SPACING):
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" '
                     f'stroke="#eee" stroke-width="1"/>')
    for y in range(0, int(height) + 1, GRID_SPACING):
        lines.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" '
                     f'stroke="#eee" stroke-width="1"/>')
    return "".join(lines)


def _render_vertex(v: _Vertex, pos: tuple[float, float]) -> str:
    x, y = pos
    label = v.label or "·"
    fill = _hsla_to_css(v.colour) if v.colour else "#000"
    # Background pill so arrows visually terminate at the label box.
    text_width = max(20, len(label) * VERTEX_FONT * 0.55)
    return (
        f'<rect x="{x - text_width/2 - 4}" y="{y - VERTEX_FONT/2 - 4}" '
        f'width="{text_width + 8}" height="{VERTEX_FONT + 8}" '
        f'fill="white" stroke="none"/>'
        f'<text x="{x}" y="{y + VERTEX_FONT/3}" text-anchor="middle" '
        f'font-size="{VERTEX_FONT}" fill="{sax.escape(fill)}">'
        f'{html.escape(label)}</text>'
    )


def _render_edge(idx: int, cells: list, positions: dict, shift) -> str:
    """Render one edge (which may itself be a 2-cell)."""
    c: _Edge = cells[idx]
    sx, sy = shift(positions[c.src])
    tx, ty = shift(positions[c.tgt])

    # Clip the endpoints away from any vertex-shaped endpoint, so the arrow
    # stops at the edge of the label box rather than running through it.
    sx, sy = _clip_endpoint(sx, sy, tx, ty, cells[c.src])
    tx, ty = _clip_endpoint(tx, ty, sx, sy, cells[c.tgt])

    curve = c.options.get("curve", 0)
    level = c.options.get("level", 1)
    style = c.options.get("style", {})

    colour = "#222"
    if "colour" in c.options:
        colour = _hsla_to_css(tuple(c.options["colour"]))

    # Path: straight line, or quadratic Bézier when curved.
    if curve == 0:
        d = f"M {sx:.1f} {sy:.1f} L {tx:.1f} {ty:.1f}"
        # Midpoint for label placement.
        mx, my = (sx + tx) / 2, (sy + ty) / 2
        # Arrow direction at endpoint
        end_angle = math.atan2(ty - sy, tx - sx)
    else:
        # Control point perpendicular to the chord.
        dx, dy = tx - sx, ty - sy
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length, dx / length
        bow = curve * 18  # px of perpendicular displacement
        cx = (sx + tx) / 2 + nx * bow
        cy = (sy + ty) / 2 + ny * bow
        d = f"M {sx:.1f} {sy:.1f} Q {cx:.1f} {cy:.1f} {tx:.1f} {ty:.1f}"
        mx, my = (sx + 2*cx + tx) / 4, (sy + 2*cy + ty) / 4
        # Tangent at t=1: 2*(P2 - P1) for quadratic Bézier
        end_angle = math.atan2(ty - cy, tx - cx)

    shape_name = style.get("name", "arrow")
    body_name  = style.get("body", {}).get("name", "cell") if shape_name == "arrow" else None
    head_name  = style.get("head", {}).get("name", "arrowhead") if shape_name == "arrow" else None
    tail_name  = style.get("tail", {}).get("name", "none") if shape_name == "arrow" else None

    parts: list[str] = []

    # Special shapes
    if shape_name == "corner" or shape_name == "corner-inverse":
        # A small right-angle marker near the target.
        parts.append(_corner_marker(sx, sy, tx, ty, inverse=(shape_name == "corner-inverse"),
                                    colour=colour))
        return "".join(parts)

    if shape_name == "adjunction":
        # ⊣ in the middle of the line between the two functor arrows.
        parts.append(
            f'<text x="{mx}" y="{my + 4}" text-anchor="middle" '
            f'font-size="18" fill="{sax.escape(colour)}">⊣</text>'
        )
        return "".join(parts)

    # Stroke dasharray based on body style
    dash = ""
    if body_name == "dashed":         dash = "stroke-dasharray=\"6 4\""
    elif body_name == "dotted":       dash = "stroke-dasharray=\"2 3\""
    elif body_name == "squiggly":     dash = "stroke-dasharray=\"2 2\""  # rough
    elif body_name == "barred":       dash = ""  # we draw the bar separately
    elif body_name == "double barred":dash = ""

    # Draw `level` parallel lines (for n-cells: =>, ≡, ...).
    # Implementation: offset the path perpendicular by ±2px per extra level.
    for i in range(level):
        offset = (i - (level - 1) / 2) * 3
        parts.append(_offset_path(d, offset, colour, dash))

    # Single arrowhead at the target (only on the centre line).
    if head_name == "arrowhead":
        parts.append(_arrowhead(tx, ty, end_angle, colour))
    elif head_name == "epi":
        # Two arrowheads close together.
        ax, ay = tx - 6 * math.cos(end_angle), ty - 6 * math.sin(end_angle)
        parts.append(_arrowhead(tx, ty, end_angle, colour))
        parts.append(_arrowhead(ax, ay, end_angle, colour))
    elif head_name == "harpoon":
        side = style.get("head", {}).get("side", "top")
        parts.append(_harpoon(tx, ty, end_angle, side, colour))
    # head_name == "none": no head

    # Tail (start-end decoration)
    start_angle = math.atan2(ty - sy, tx - sx) if curve == 0 else _start_angle(d)
    if tail_name == "mono":
        # extra inward arrowhead at source
        ax, ay = sx + 6 * math.cos(start_angle), sy + 6 * math.sin(start_angle)
        parts.append(_arrowhead(ax, ay, start_angle, colour))
    elif tail_name == "maps to":
        # short perpendicular tick at source
        nx, ny = -math.sin(start_angle), math.cos(start_angle)
        parts.append(
            f'<line x1="{sx + nx*5:.1f}" y1="{sy + ny*5:.1f}" '
            f'x2="{sx - nx*5:.1f}" y2="{sy - ny*5:.1f}" '
            f'stroke="{sax.escape(colour)}" stroke-width="1.4"/>'
        )
    elif tail_name == "hook":
        side = style.get("tail", {}).get("side", "top")
        parts.append(_hook(sx, sy, start_angle, side, colour))

    # Bar(s) for "barred" / "double barred" — draw a short perpendicular tick
    # at the midpoint.
    if body_name == "barred":
        parts.append(_bar(mx, my, end_angle, colour, count=1))
    elif body_name == "double barred":
        parts.append(_bar(mx, my, end_angle, colour, count=2))

    # Label
    if c.label:
        # Position the label: which side depends on `alignment`.
        # 0=left → above the line, 1=centre → on the line (white background),
        # 2=right → below the line, 3=over → on the line (no background).
        nx, ny = -math.sin(end_angle), math.cos(end_angle)
        offset_px = 14
        if c.alignment == 0:        # left
            lx, ly = mx + nx * offset_px, my + ny * offset_px
        elif c.alignment == 2:      # right
            lx, ly = mx - nx * offset_px, my - ny * offset_px
        else:
            lx, ly = mx, my + 4

        label_fill = "#000"
        if c.label_colour is not None:
            label_fill = _hsla_to_css(tuple(c.label_colour))

        # Centre/over alignments get a white box behind them.
        bg = ""
        if c.alignment in (1, 3):
            bw = max(20, len(c.label) * LABEL_FONT * 0.55)
            bg = (f'<rect x="{lx - bw/2 - 2}" y="{ly - LABEL_FONT - 2}" '
                  f'width="{bw + 4}" height="{LABEL_FONT + 6}" '
                  f'fill="white" stroke="none"/>')
        parts.append(bg)
        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'font-size="{LABEL_FONT}" fill="{sax.escape(label_fill)}" '
            f'font-style="italic">{html.escape(c.label)}</text>'
        )

    return "".join(parts)


# --- small SVG primitives ---

def _arrowhead(x: float, y: float, angle: float, colour: str) -> str:
    a1 = angle + math.pi - 0.4
    a2 = angle + math.pi + 0.4
    p1 = (x + ARROW_HEAD * math.cos(a1), y + ARROW_HEAD * math.sin(a1))
    p2 = (x + ARROW_HEAD * math.cos(a2), y + ARROW_HEAD * math.sin(a2))
    return (f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} '
            f'{p2[0]:.1f},{p2[1]:.1f}" fill="{sax.escape(colour)}"/>')


def _harpoon(x: float, y: float, angle: float, side: str, colour: str) -> str:
    sign = -1 if side == "top" else 1
    a = angle + math.pi + 0.4 * sign
    p = (x + ARROW_HEAD * math.cos(a), y + ARROW_HEAD * math.sin(a))
    return (f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{p[0]:.1f}" y2="{p[1]:.1f}" '
            f'stroke="{sax.escape(colour)}" stroke-width="1.4"/>')


def _hook(x: float, y: float, angle: float, side: str, colour: str) -> str:
    """A small semicircle perpendicular to the line at the source end."""
    sign = -1 if side == "top" else 1
    nx, ny = -math.sin(angle) * sign, math.cos(angle) * sign
    cx, cy = x + nx * 5, y + ny * 5
    return (f'<path d="M {x - math.cos(angle)*5:.1f} {y - math.sin(angle)*5:.1f} '
            f'A 5 5 0 0 {0 if side=="top" else 1} '
            f'{x + math.cos(angle)*0:.1f} {y + math.sin(angle)*0:.1f}" '
            f'fill="none" stroke="{sax.escape(colour)}" stroke-width="1.4"/>')


def _bar(x: float, y: float, angle: float, colour: str, count: int = 1) -> str:
    """Perpendicular tick(s) crossing the line."""
    nx, ny = -math.sin(angle), math.cos(angle)
    tx, ty = math.cos(angle), math.sin(angle)
    out: list[str] = []
    for i in range(count):
        sep = (i - (count - 1) / 2) * 3
        cx, cy = x + tx * sep, y + ty * sep
        out.append(
            f'<line x1="{cx + nx*5:.1f}" y1="{cy + ny*5:.1f}" '
            f'x2="{cx - nx*5:.1f}" y2="{cy - ny*5:.1f}" '
            f'stroke="{sax.escape(colour)}" stroke-width="1.4"/>'
        )
    return "".join(out)


def _corner_marker(sx: float, sy: float, tx: float, ty: float, *,
                   inverse: bool, colour: str) -> str:
    """Small right-angle near the target end (apex of pullback square)."""
    # Vector from src to tgt
    dx, dy = tx - sx, ty - sy
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    # Step backwards from target
    bx, by = tx - ux * 14, ty - uy * 14
    # Perpendicular
    nx, ny = -uy, ux
    if inverse:
        nx, ny = -nx, -ny
    p1 = (bx + nx * 12, by + ny * 12)
    p2 = (bx + ux * 12 + nx * 12, by + uy * 12 + ny * 12)
    return (f'<polyline points="{p1[0]:.1f},{p1[1]:.1f} '
            f'{p2[0]:.1f},{p2[1]:.1f} '
            f'{bx + ux * 12:.1f},{by + uy * 12:.1f}" '
            f'fill="none" stroke="{sax.escape(colour)}" stroke-width="1.4"/>')


def _offset_path(d: str, offset_px: float, colour: str, dash_attr: str) -> str:
    """Re-draw the path with a perpendicular offset (for n-cells = ⇒ etc).

    For simplicity we just thicken via stroke offset using a transform on a
    reused path. This is a coarse approximation but visually conveys 'n
    parallel lines'.
    """
    if abs(offset_px) < 0.5:
        return (f'<path d="{d}" fill="none" stroke="{sax.escape(colour)}" '
                f'stroke-width="1.4" {dash_attr}/>')
    # Quick hack: nudge the whole path. Doesn't handle curves precisely but
    # it's a preview.
    return (f'<g transform="translate(0, {offset_px})">'
            f'<path d="{d}" fill="none" stroke="{sax.escape(colour)}" '
            f'stroke-width="1.4" {dash_attr}/></g>')


def _start_angle(d: str) -> float:
    """Approximate tangent at the start of an SVG path (for curved paths)."""
    # We know our paths are either "M x y L x y" or "M x y Q cx cy tx ty";
    # parse the second control point.
    parts = d.split()
    sx, sy = float(parts[1]), float(parts[2])
    if parts[3] == "L":
        ex, ey = float(parts[4]), float(parts[5])
        return math.atan2(ey - sy, ex - sx)
    # Q cx cy tx ty
    cx, cy = float(parts[4]), float(parts[5])
    return math.atan2(cy - sy, cx - sx)


def _hsla_to_css(c: tuple) -> str:
    if c is None:
        return "#000"
    h, s, l, a = c if len(c) == 4 else (*c, 1)
    return f"hsla({h},{s}%,{l}%,{a})"


def _clip_endpoint(x: float, y: float, ox: float, oy: float, end_cell) -> tuple[float, float]:
    """Move (x, y) inward along the line toward (ox, oy) so it sits on the
    boundary of the endpoint's label box rather than at its centre.

    For vertices, we approximate a tight axis-aligned rectangle around the
    label; for edges (2-cells), we just retreat a small fixed distance.
    """
    dx, dy = ox - x, oy - y
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length

    if isinstance(end_cell, _Vertex):
        # Approximate label box (matches _render_vertex sizing).
        label = end_cell.label or "·"
        half_w = max(20, len(label) * VERTEX_FONT * 0.55) / 2 + 4
        half_h = VERTEX_FONT / 2 + 4
        # Find the smallest t ≥ 0 such that the point (x + t*ux, y + t*uy)
        # exits the box centred at (x, y) of half-extents (half_w, half_h).
        # Equivalently: t such that |t*ux| = half_w (t = half_w/|ux|) or
        # |t*uy| = half_h. Take the min of the active limits.
        ts = []
        if abs(ux) > 1e-6: ts.append(half_w / abs(ux))
        if abs(uy) > 1e-6: ts.append(half_h / abs(uy))
        t = min(ts) if ts else 0
        # Cap at half the segment length to avoid flipping past the midpoint.
        t = min(t, length / 2 - 4)
        if t < 0: t = 0
        return (x + ux * t, y + uy * t)
    else:
        # Edge endpoint (2-cell): retreat a small fixed distance.
        retreat = min(8, length / 3)
        return (x + ux * retreat, y + uy * retreat)


# =========================================================================
# CLI: feed it a Python file that builds and prints `quiver`.
# =========================================================================

if __name__ == "__main__":
    import sys
    # Demo: render a pullback square if invoked directly.
    q = Quiver()
    P = q.vertex(1, 0, r"A \times_C B")
    B = q.vertex(2, 0, "B")
    A = q.vertex(1, 1, "A")
    C = q.vertex(2, 1, "C")
    q.edge(A, C, "f", ALIGN_RIGHT := 2)
    q.edge(B, C, "g")
    q.edge(P, A, r"\pi_1", 2)
    q.edge(P, B, r"\pi_2")
    q.edge(P, C, "", 1, shape={"name": "corner"})
    out = sys.argv[1] if len(sys.argv) > 1 else "demo.svg"
    render_svg_file(q, out)
    print(f"wrote {out}")
    print(q.to_url())
