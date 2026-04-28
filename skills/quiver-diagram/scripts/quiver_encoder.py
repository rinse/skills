"""
quiver_encoder.py — Build q.uiver.app commutative-diagram URLs.

High-level Python API on top of the q.uiver.app base64 URL format
(version 0, documented in `quiver/src/quiver.mjs:1227-1267` upstream).

Quick example:
    from quiver_encoder import Quiver
    q = Quiver()
    a = q.vertex(0, 0, "A")
    b = q.vertex(1, 0, "B")
    q.edge(a, b, "f")
    print(q.to_url())
    # -> https://q.uiver.app/#q=WzAsMixbMCwwLCJBIl0sWzEsMCwiQiJdLFswLDEsImYiXV0=
"""

import base64
import json
from dataclasses import dataclass, field
from typing import Optional

# =========================================================================
# Style constants — these are the exact strings quiver expects.
# =========================================================================

# --- tail (source-end decoration) ---
TAIL_NONE        = {"name": "none"}
TAIL_MONO        = {"name": "mono"}              # ↣
TAIL_MAPS_TO     = {"name": "maps to"}           # ↦
TAIL_HOOK_TOP    = {"name": "hook", "side": "top"}
TAIL_HOOK_BOTTOM = {"name": "hook", "side": "bottom"}
TAIL_ARROWHEAD   = {"name": "arrowhead"}         # double tail (rare)

# --- body (line style) ---
BODY_SOLID         = {"name": "cell"}            # default
BODY_NONE          = {"name": "none"}
BODY_DASHED        = {"name": "dashed"}
BODY_DOTTED        = {"name": "dotted"}
BODY_SQUIGGLY      = {"name": "squiggly"}
BODY_BARRED        = {"name": "barred"}
BODY_DOUBLE_BARRED = {"name": "double barred"}
BODY_BULLET_SOLID  = {"name": "bullet solid"}
BODY_BULLET_HOLLOW = {"name": "bullet hollow"}

# --- head (target-end arrowhead) ---
HEAD_ARROWHEAD      = {"name": "arrowhead"}      # default
HEAD_NONE           = {"name": "none"}
HEAD_EPI            = {"name": "epi"}            # ↠
HEAD_HARPOON_TOP    = {"name": "harpoon", "side": "top"}
HEAD_HARPOON_BOTTOM = {"name": "harpoon", "side": "bottom"}

# --- shape: replaces tail/body/head with a fixed glyph ---
SHAPE_ARROW        = {"name": "arrow"}           # default — uses tail/body/head
SHAPE_ADJUNCTION   = {"name": "adjunction"}      # ⊣
SHAPE_PULLBACK     = {"name": "corner"}          # ⌟ (pullback / pushout marker)
SHAPE_PULLBACK_INV = {"name": "corner-inverse"}  # ⌜

# --- label alignment enum ---
ALIGN_LEFT   = 0
ALIGN_CENTRE = 1
ALIGN_RIGHT  = 2
ALIGN_OVER   = 3

# =========================================================================
# Internal data classes
# =========================================================================

@dataclass
class _Vertex:
    x: int
    y: int
    label: str = ""
    colour: Optional[tuple] = None  # (h, s, l, a)

@dataclass
class _Edge:
    src: int
    tgt: int
    label: str = ""
    alignment: int = ALIGN_LEFT
    options: dict = field(default_factory=dict)
    label_colour: Optional[tuple] = None

# =========================================================================
# Builder
# =========================================================================

class Quiver:
    """A commutative diagram builder.

    Add all vertices first with ``vertex(x, y, label)``, then add edges with
    ``edge(src, tgt, label, ...)``. Both methods return the new cell's index;
    edges may target other edges (use the index returned by ``edge()``) to
    create 2-cells, 3-cells, etc.
    """

    def __init__(self):
        self._cells: list = []          # mixed _Vertex / _Edge in insertion order
        self._n_vertices: int = 0

    # ---------- vertices ----------

    def vertex(self, x: int, y: int, label: str = "",
               colour: Optional[tuple] = None) -> int:
        """Add a vertex at integer grid position (x, y).

        Coordinates: x grows right, y grows DOWN (screen coordinates).
        The encoder will normalise to keep the top-left occupied cell at (0, 0).

        ``label`` is a KaTeX/LaTeX string (e.g. ``r"\\mathscr C"``).
        ``colour`` is ``(hue 0-360, sat 0-100, light 0-100[, alpha 0-1])``.

        Returns the new vertex's cell index, for use as src/tgt of edges.

        Note: the JSON format requires all vertices to come before all edges
        in the encoded output. The encoder enforces this by reordering at
        ``to_json()`` time, so you may add vertices and edges in any order.
        """
        self._cells.append(_Vertex(x=x, y=y, label=label,
                                   colour=_normalise_colour(colour)))
        self._n_vertices += 1
        return len(self._cells) - 1

    # ---------- edges ----------

    def edge(self, src: int, tgt: int, label: str = "",
             alignment: int = ALIGN_LEFT,
             *,
             curve: int = 0,
             offset: int = 0,
             level: int = 1,
             label_position: int = 50,
             shorten_source: int = 0,
             shorten_target: int = 0,
             tail: Optional[dict] = None,
             body: Optional[dict] = None,
             head: Optional[dict] = None,
             shape: Optional[dict] = None,
             colour: Optional[tuple] = None,
             label_colour: Optional[tuple] = None) -> int:
        """Add an edge from cell ``src`` to cell ``tgt``.

        Returns the new edge's cell index. Edges may be used as src/tgt of
        other edges to form n-cells (e.g. natural transformations).

        Parameters
        ----------
        label
            KaTeX/LaTeX string; default empty (an unlabelled edge).
        alignment
            Where the label sits relative to the arrow:
            ``ALIGN_LEFT`` (0, default), ``ALIGN_CENTRE`` (1),
            ``ALIGN_RIGHT`` (2), ``ALIGN_OVER`` (3, label sits on the line).
        curve
            Bend the arrow. Integer; ±2 is a small visible curve, ±5 is large.
            Positive curves to the right of the source→target direction.
        offset
            Perpendicular displacement of the entire edge. Use ``offset=±2`` on
            two parallel arrows between the same endpoints to separate them.
        level
            Number of parallel lines: 1=normal arrow, 2=double (⇒, used for
            natural transformations between parallel functors), 3=triple, etc.
        label_position
            0..100, percent along the edge from src (0) to tgt (100).
        shorten_source, shorten_target
            0..100 each, percent of edge length clipped from each end. Useful
            when one edge runs between two curved edges (a 2-cell) and you
            don't want it touching the curves.
        tail, body, head
            One of the ``TAIL_*`` / ``BODY_*`` / ``HEAD_*`` dict constants.
        shape
            ``SHAPE_ADJUNCTION``, ``SHAPE_PULLBACK``, or ``SHAPE_PULLBACK_INV``.
            When set (other than ``SHAPE_ARROW``), the tail/body/head are
            replaced by the fixed glyph and become irrelevant.
        colour
            Arrow colour as ``(h, s, l[, a])``.
        label_colour
            Same format, applies only to the label text.
        """
        if not (0 <= src < len(self._cells)):
            raise ValueError(f"src index {src} out of range "
                             f"(only {len(self._cells)} cells declared)")
        if not (0 <= tgt < len(self._cells)):
            raise ValueError(f"tgt index {tgt} out of range "
                             f"(only {len(self._cells)} cells declared)")

        opts: dict = {}
        if curve != 0:           opts["curve"] = curve
        if offset != 0:          opts["offset"] = offset
        if level != 1:           opts["level"] = level
        if label_position != 50: opts["label_position"] = label_position
        if shorten_source or shorten_target:
            shorten = {}
            if shorten_source: shorten["source"] = shorten_source
            if shorten_target: shorten["target"] = shorten_target
            opts["shorten"] = shorten

        # Style sub-object — `shape` (corner/adjunction) replaces the entire
        # style, so it's mutually exclusive with tail/body/head.
        style: dict = {}
        if shape is not None and shape.get("name", "arrow") != "arrow":
            style = dict(shape)
        else:
            if tail is not None: style["tail"] = dict(tail)
            if body is not None: style["body"] = dict(body)
            if head is not None: style["head"] = dict(head)
        if style:
            opts["style"] = style

        if colour is not None:
            opts["colour"] = list(_normalise_colour(colour))

        self._cells.append(_Edge(
            src=src, tgt=tgt, label=label, alignment=alignment,
            options=opts,
            label_colour=_normalise_colour(label_colour),
        ))
        return len(self._cells) - 1

    # ---------- output ----------

    def to_json(self) -> list:
        """Build the raw JSON-array representation.

        Vertices and edges may have been added in any order; this method
        emits all vertices before all edges (as required by the format) and
        rewrites edge ``src``/``tgt`` indices accordingly.
        """
        if not self._cells:
            return []

        # Build a remap: old index → new index, where vertices come first
        # in declaration order, then edges in declaration order.
        new_indices: dict[int, int] = {}
        ordered: list = []
        for i, c in enumerate(self._cells):
            if isinstance(c, _Vertex):
                new_indices[i] = len(ordered)
                ordered.append(c)
        for i, c in enumerate(self._cells):
            if isinstance(c, _Edge):
                new_indices[i] = len(ordered)
                ordered.append(c)

        # Normalise so the top-left vertex sits at (0, 0).
        verts = [c for c in ordered if isinstance(c, _Vertex)]
        if verts:
            min_x = min(v.x for v in verts)
            min_y = min(v.y for v in verts)
        else:
            min_x = min_y = 0

        out: list = [0, self._n_vertices]
        for cell in ordered:
            if isinstance(cell, _Vertex):
                arr: list = [cell.x - min_x, cell.y - min_y]
                if cell.label != "":
                    arr.append(cell.label)
                if cell.label != "" and cell.colour is not None:
                    arr.append(list(cell.colour))
                out.append(arr)
            else:
                arr = [new_indices[cell.src], new_indices[cell.tgt]]
                # Build the trailing fields back-to-front (mirrors the JS
                # encoder at quiver.mjs:1398-1413). Each is included iff
                # something later was already included OR it's not the default.
                end: list = []
                if cell.label_colour is not None and cell.label != "":
                    end.append(list(cell.label_colour))
                if end or cell.options:
                    end.append(cell.options)
                if end or (cell.alignment != 0 and cell.label != ""):
                    end.append(cell.alignment)
                if end or cell.label != "":
                    end.append(cell.label)
                arr.extend(reversed(end))
                out.append(arr)
        return out

    def to_base64(self) -> str:
        """Compact JSON, then base64-encoded."""
        if not self._cells:
            return ""
        js = json.dumps(self.to_json(), separators=(",", ":"),
                        ensure_ascii=False)
        return base64.b64encode(js.encode("utf-8")).decode("ascii")

    def to_url(self, base: str = "https://q.uiver.app/") -> str:
        """The full shareable q.uiver.app URL."""
        b64 = self.to_base64()
        if not b64:
            return base
        sep = "" if base.endswith("#") else "#"
        return f"{base}{sep}q={b64}"


# =========================================================================
# Helpers
# =========================================================================

def _normalise_colour(c) -> Optional[tuple]:
    """Accept (h, s, l) or (h, s, l, a); return a 4-tuple or None."""
    if c is None:
        return None
    if len(c) == 3:
        return (int(c[0]), int(c[1]), int(c[2]), 1)
    if len(c) == 4:
        return (int(c[0]), int(c[1]), int(c[2]), float(c[3]))
    raise ValueError(f"colour must have 3 or 4 components, got: {c!r}")
