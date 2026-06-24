---
name: quiver-diagram
description: Build q.uiver.app commutative diagrams and return shareable URLs (with optional SVG previews). Use this skill whenever the user asks for a commutative diagram, pullback/pushout square, adjunction, natural transformation, pasting diagram, n-cell, or tikz-cd-style diagram — any objects-and-arrows diagram in category theory, algebra, or topology. Triggers on phrases like "draw a commutative diagram", "I need a quiver diagram", "give me a q.uiver URL", or any time the user wants to visualise a categorical structure even without saying "quiver".
license: MIT
metadata:
  author: rinse <rinse418@gmail.com>
  source: https://github.com/rinse/skills
---

# Quiver diagram skill

Build URLs for **q.uiver.app**, the web-based commutative diagram editor. The
URL embeds a base64-encoded JSON description of the diagram, so the recipient
can both view and edit it.

This skill produces:

1. A `https://q.uiver.app/#q=...` URL the user can open immediately.
2. (Optional) A structural SVG preview, so the diagram can be sanity-checked
   before sharing the URL.

## Decision tree — pick a workflow

For **simple diagrams** (≤6 vertices, no 2-cells, no curves, no special
styles), build the JSON inline and base64-encode it directly. Read
`references/format-spec.md` first if you're not familiar with the format.

For **anything else** — pullbacks, pushouts, adjunctions, natural
transformations, pasting diagrams, anything with curves or colours — use the
Python encoder in `scripts/`. It handles all the truncation rules and style
constants for you.

For **standard patterns** — commutative square, triangle, pullback, pushout,
adjunction, natural transformation, parallel arrows, equaliser, coequaliser,
short exact sequence — start from `scripts/templates.py` and customise the
labels.

## Workflow

### Step 1: Identify the diagram structure

Before writing any code, sketch the diagram in plain text:

- What objects (vertices) are there? Where do they sit on a 2D grid?
- What morphisms (1-cells)? What are their labels?
- Are there any 2-cells (natural transformations, modifications)?
- Special shapes: pullback corner, pushout corner, adjunction symbol?
- Special styles: dashed (universal map), mono ↣, epi ↠, etc.?

### Step 2: Pick the right entry point

Match the user's request against the templates first. If one fits with minor
relabelling, use it. Otherwise, build from scratch with `Quiver()`.

### Step 3: Build and verify

Write a small Python script that imports from `quiver_encoder` and prints
`q.to_url()`. Run it. If the diagram is non-trivial, also generate a preview
SVG with `quiver_preview.render_svg_file()` and inspect it.

### Step 4: Return both URL and preview

Present the URL inline so the user can click it. If you generated an SVG
preview, save it via `present_files` or similar so the user can verify the
structure without opening the URL.

## Inline-build cheatsheet (for simple diagrams)

The format is `[0, n_vertices, ...vertices, ...edges]`, base64-encoded:

```python
import base64, json

# A --f--> B
data = [0, 2,           # version=0, 2 vertices
        [0, 0, "A"],    # vertex at (0, 0) labelled A
        [1, 0, "B"],    # vertex at (1, 0) labelled B
        [0, 1, "f"]]    # edge from cell 0 to cell 1, label "f"
b64 = base64.b64encode(json.dumps(data, separators=(",",":"),
                                  ensure_ascii=False).encode()).decode()
print(f"https://q.uiver.app/#q={b64}")
```

Coordinates: `x` grows right, `y` grows **DOWN**. The top-left occupied cell
must be at `(0, 0)`. Labels use KaTeX/LaTeX (e.g. `r"\\pi_1"`).

## Encoder API quick reference

```python
from quiver_encoder import (
    Quiver, ALIGN_LEFT, ALIGN_CENTRE, ALIGN_RIGHT, ALIGN_OVER,
    SHAPE_PULLBACK, SHAPE_PULLBACK_INV, SHAPE_ADJUNCTION,
    BODY_DASHED, BODY_DOTTED, BODY_SQUIGGLY, BODY_BARRED,
    HEAD_ARROWHEAD, HEAD_NONE, HEAD_EPI, HEAD_HARPOON_TOP, HEAD_HARPOON_BOTTOM,
    TAIL_NONE, TAIL_MONO, TAIL_MAPS_TO, TAIL_HOOK_TOP, TAIL_HOOK_BOTTOM,
)

q = Quiver()
v = q.vertex(x, y, label, colour=None)               # returns vertex index
e = q.edge(src, tgt, label="", alignment=ALIGN_LEFT, # returns edge index
           *, curve=0, offset=0, level=1,
           label_position=50,
           shorten_source=0, shorten_target=0,
           tail=None, body=None, head=None, shape=None,
           colour=None, label_colour=None)

q.to_url()       # → "https://q.uiver.app/#q=..."
q.to_base64()    # → just the base64 string
q.to_json()      # → the raw JSON-array structure
```

Key parameter notes:

- **`curve`**: integer; ±2 small bend, ±5 large. Positive curves to the
  right of the src→tgt direction.
- **`offset`**: separates parallel arrows. Use `offset=-2` and `offset=+2`
  on two arrows between the same endpoints.
- **`level`**: 1 for normal arrow, 2 for double `⇒` (natural transformations),
  3 for triple, etc.
- **`shorten_source` / `shorten_target`**: 0..100 percent. Use when a 2-cell
  shouldn't touch the curved arrows it connects.
- **`shape`**: when set to anything other than `SHAPE_ARROW`, replaces the
  whole tail/body/head with a fixed glyph. `SHAPE_PULLBACK` and
  `SHAPE_PULLBACK_INV` make the right-angle marker; `SHAPE_ADJUNCTION` makes
  the `⊣` symbol.

## Templates available

In `scripts/templates.py`:

| function | what it draws |
|---|---|
| `commutative_square((A,B,C,D), (f,g,h,k))` | 2×2 square with f top, g bottom, h left, k right |
| `triangle((A,B,C), (f,g,h))` | A at top, B and C at bottom |
| `pullback(...)` | full pullback with corner mark; `universal_property=True` adds the X with curved a, b, dashed mediator |
| `pushout(...)` | dual of pullback |
| `adjunction((C,D), (F,G))` | F ⊣ G with the ⊣ glyph |
| `natural_transformation((C,D), (F,G), name)` | α : F ⇒ G with `level=2` |
| `parallel_arrows(A, B, (f,g))` | two arrows A ⇉ B |
| `equaliser((E,A,B), (e,f,g))` | E ↣ A ⇉ B |
| `coequaliser((A,B,Q), (f,g,q))` | A ⇉ B ↠ Q |
| `short_exact_sequence((A,B,C), (f,g))` | 0 → A ↣ B ↠ C → 0 |

Each returns a `Quiver` instance you can mutate further (add more cells with
`q.vertex()` / `q.edge()`) before serialising.

## Preview generation

The preview is a structural SVG — it shows where vertices sit and how arrows
connect, but is **not** a faithful render of how q.uiver.app will display the
diagram (no KaTeX, simplified curves, approximate n-cell rendering). Use it
to verify the structure before sharing the URL.

```python
from quiver_preview import render_svg_file
render_svg_file(q, "/tmp/preview.svg", show_grid=False)
```

To convert SVG → PNG so you can view it inline (requires `cairosvg`, install
with `pip install cairosvg --break-system-packages` if missing):

```python
import cairosvg
cairosvg.svg2png(url="/tmp/preview.svg", write_to="/tmp/preview.png",
                 output_width=800)
```

If `cairosvg` isn't available, just produce the SVG file — modern browsers
and most editors render SVG natively, so the user can still inspect it.

## When the diagram has many decisions

Some patterns warrant deeper reading:

- **Higher cells, edges-into-edges, level≥3, exotic shapes** → read
  `references/format-spec.md` for the underlying JSON schema.
- **Style decisions** (which `tail`/`body`/`head` to use for which kind of
  morphism) → see `references/style-reference.md`.

## Worked example

User: "Make me a pullback square showing the universal property,
with X mapping to A and B, and the unique map into the apex."

```python
import sys
sys.path.insert(0, "<skill-path>/scripts")
from templates import pullback

q = pullback(universal_property=True)
print(q.to_url())

# Optional preview
from quiver_preview import render_svg_file
render_svg_file(q, "/mnt/user-data/outputs/pullback_universal.svg")
```

Then surface the URL in the reply and present the SVG file.

## What this skill does NOT cover

- **Self-loops** (edges from a vertex to itself with `shape: "arc"`). The
  encoder doesn't expose `radius`/`angle`; you'd need to set `options["shape"]
  = "arc"` and `options["radius"]`/`options["angle"]` directly via the JSON
  format. See `references/format-spec.md`.
- **Macro definitions** (`\newcommand`s loaded into the diagram). q.uiver.app
  supports `&macro_url=...` query params; you can append this to the URL
  manually.
- **Embedded HTML iframes**. Use `to_url()` and let the user copy.
- **TikZ-cd or Typst export**. Open the URL in q.uiver.app and use its
  built-in export buttons.
