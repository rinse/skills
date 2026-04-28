# q.uiver.app URL format — full specification

This is the complete specification of the q.uiver.app URL format, derived from
reading `quiver/src/quiver.mjs` (lines 1227–1670) and `ui.mjs` (line 7876)
in the upstream `varkor/quiver` repository. Read this when you need to do
something the high-level encoder doesn't expose, or when debugging a
hand-built URL.

## Table of contents

1. [URL anatomy](#url-anatomy)
2. [JSON payload](#json-payload)
3. [Vertex format](#vertex-format)
4. [Edge format](#edge-format)
5. [Edge `options` reference](#edge-options-reference)
6. [Style values (tail / body / head / shape)](#style-values)
7. [Higher cells](#higher-cells)
8. [Truncation rules (subtle)](#truncation-rules)
9. [Coordinate system](#coordinate-system)
10. [Common mistakes](#common-mistakes)

---

## URL anatomy

```
https://q.uiver.app/#q=<base64(JSON)>[&macro_url=<urlencoded>]
```

- The diagram lives in the URL **fragment** (after `#`), not the query string.
- `&r=<renderer>` may precede `q=` (default renderer is omitted).
- An empty diagram has no encoding — just the bare URL.

## JSON payload

A flat array, version-tagged:

```
[version=0, |vertices|, ...vertices, ...edges]
```

`version` is currently `0` and intended to remain stable.
`|vertices|` tells the parser how many of the trailing items are vertices —
the rest are treated as edges.

The combined index of any cell is its position in `[...vertices, ...edges]`,
i.e. position-2 in the JSON array minus 2.

## Vertex format

```
[x, y]
[x, y, label]
[x, y, label, [h, s, l, a]]
```

- `x`, `y`: non-negative integers. **The top-left occupied cell must be at `(0, 0)`.**
- `label`: a KaTeX/LaTeX string. Defaults to `""`.
- Colour: `[hue 0–360, sat 0–100, light 0–100, alpha 0–1]`. Defaults to black `[0,0,0,1]`.

## Edge format

```
[src, tgt]
[src, tgt, label]
[src, tgt, label, alignment]
[src, tgt, label, alignment, options]
[src, tgt, label, alignment, options, [h, s, l, a]]
```

- `src`, `tgt`: indices into the combined `[...vertices, ...edges]` array.
- `alignment`: integer enum; only meaningful when `label != ""`:
  - `0` = left of arrow
  - `1` = centre (label box covers the arrow)
  - `2` = right of arrow
  - `3` = over (label sits on the arrow line, no background)
- `options`: an object containing only fields that **differ from defaults**.
- The trailing `[h, s, l, a]` is the **label** colour, not the arrow colour
  (arrow colour goes inside `options`).

## Edge `options` reference

Defaults from `Edge.default_options` in `ui.mjs:7876`:

| field | default | type / range | meaning |
|---|---|---|---|
| `label_position` | `50` | natural 0..100 | percent along edge from src (0) to tgt (100) |
| `offset` | `0` | integer | perpendicular displacement of the entire edge in arbitrary units; use ±2 to separate parallel arrows |
| `curve` | `0` | integer | bend amount; ±2 small, ±5 large; positive curves to the right of src→tgt direction |
| `radius` | `3` | integer | for `shape: arc` (loops only) |
| `angle` | `0` | integer | for `shape: arc` (loops only) |
| `shorten` | `{source: 0, target: 0}` | each natural 0..100 | percent clipped from each end |
| `level` | `1` | natural ≥1 | `1`=single arrow, `2`=double (`⇒`), etc. — for n-cells |
| `colour` | `[0,0,0,1]` (black) | `[h,s,l]` or `[h,s,l,a]` | arrow colour |
| `edge_alignment` | `{source: true, target: true}` | bool each | for edges-into-edges, whether to align to midpoint of the target edge (`true`) or to the midpoint of its endpoints (`false`) |
| `style` | (object — see below) | object | tail/body/head, or a replacement shape |

### Legacy `length` field

Older diagrams used a single `length` parameter (0..100) instead of the
`shorten` object. The parser auto-converts it via
`shorten.source = shorten.target = (100 - length) / 2`.
You don't need to write `length`, but be aware that decoded older URLs may
contain it.

## Style values

The default style:

```js
{ name: "arrow", tail: {name: "none"}, body: {name: "cell"}, head: {name: "arrowhead"} }
```

There are two cases for `style`:

### Case A: `name: "arrow"` (default)

Override `tail`, `body`, `head` independently. Each is an object with a
`name` and sometimes a `side`:

| component | valid `name` values | extra fields | what it draws |
|---|---|---|---|
| `tail` | `none` | — | nothing at the source |
|         | `mono` | — | `↣` (mono / inclusion) |
|         | `maps to` | — | `↦` |
|         | `hook` | `side: "top"` or `"bottom"` | hooked tail (Bourbaki-style mono) |
|         | `arrowhead` | — | double-arrow tail (rare) |
| `body` | `cell` (default) | — | solid line |
|         | `none` | — | no line — useful with shape replacements |
|         | `dashed` / `dotted` / `squiggly` | — | various line styles |
|         | `barred` | — | line with one perpendicular bar in the middle |
|         | `double barred` | — | line with two bars |
|         | `bullet solid` / `bullet hollow` | — | line with a bullet at midpoint |
| `head` | `arrowhead` (default) | — | normal `→` arrowhead |
|         | `none` | — | no arrowhead |
|         | `epi` | — | `↠` (double arrowhead, epi / surjection) |
|         | `harpoon` | `side: "top"` or `"bottom"` | half-arrowhead |

### Case B: replacement shapes

When `style.name` is one of the values below, **`tail`/`body`/`head` are
ignored**:

| `name` | renders as | typical use |
|---|---|---|
| `adjunction` | `⊣` glyph | between two opposing functor arrows |
| `corner` | small right-angle `⌟` | pullback marker (apex on the upper-left) |
| `corner-inverse` | `⌜` (mirrored) | pushout marker (apex on the lower-right) |

Additionally, `shape: "arc"` exists for self-loops, with `radius` and `angle`
parameters; the high-level encoder doesn't expose this — see the JS source if
you need loops.

## Higher cells

To draw a 2-cell (e.g. a natural transformation), give an edge whose `src`
and/or `tgt` is the index of another **edge**, not a vertex.

Recipe for a natural transformation `α : F ⇒ G : C → D`:

1. vertex `C` at `(0, 0)`, vertex `D` at `(2, 0)`
2. edge `F : C → D` with `curve = -2` (curves up)
3. edge `G : C → D` with `curve = +2` (curves down)
4. edge `α : F → G` with `level = 2` (double-line body) and label `"\\alpha"`

The `level: 2` makes the body a double line — the standard notation for
natural transformations.

For 3-cells (modifications between natural transformations), the same
pattern applies recursively: an edge whose endpoints are themselves 2-cells.

## Truncation rules

The encoder shortens arrays by stripping trailing default values, but it
**cannot skip middle values** — only suffixes. So if a later parameter is
non-default, all earlier ones must be present even if defaulted. The
reference encoder mirrors this exactly.

For vertices:
- Omit `label` if it's `""`.
- Omit colour if `label == ""` or colour is black.
- (Note: a coloured label on an empty label is silently dropped.)

For edges (back-to-front, mirroring `quiver.mjs:1398-1413`):
- Append `label_colour` only if both `label != ""` and label_colour is non-black.
- Append `options` if anything later was already appended OR options is non-empty.
- Append `alignment` if anything later was appended OR (alignment != 0 AND label != "").
- Append `label` if anything later was appended OR label != "".

So for example `[0, 1, "f"]` is valid: alignment is implicitly 0.

## Coordinate system

- `x` grows **right**, `y` grows **DOWN** (standard screen coordinates, not
  mathematical).
- `(0, 0)` is the top-left.
- The grid stretches automatically based on label widths — neighbouring cells
  in `x` are not at a fixed pixel distance.

A useful sanity check: the README's pullback sample places the apex at
`(1, 1)`, with `B` at `(2, 1)` (right neighbour), `A` at `(1, 2)` (below),
`C` at `(2, 2)` (diagonal), and `X` at `(0, 0)` (further up-left).

## Common mistakes

1. **Confusing y-axis direction.** If your diagram looks vertically flipped,
   you've got the y-direction wrong.

2. **Forgetting that `src`/`tgt` index the **combined** array.** If you have
   3 vertices and you want the first edge to start at the first vertex, that's
   `src=0`. If you want a 2-cell whose source is the first edge (added after
   the 3 vertices), that's `src=3` — vertices first, then edges in declaration
   order.

3. **Missing `level: 2` on a 2-cell.** Without it, the natural transformation
   draws as a single arrow — visually identical to a 1-cell.

4. **Negative `curve` values.** `+curve` bends to the right of the source→
   target direction; `-curve` to the left. For a horizontal arrow, this
   means `+curve` bends down and `-curve` bends up — the opposite of what
   "positive y is down" might suggest.

5. **Default values that vary by context.** `level=1` is the default for any
   edge, but older quiver versions stored it inside `body.level` for legacy
   reasons. Decoders accept both.

6. **JSON whitespace.** The encoder uses `JSON.stringify` with no spacing,
   then UTF-8 encodes, then base64 encodes (with `=` padding). A pretty-
   printed JSON will not match the canonical bytes (though it will still
   decode correctly).
