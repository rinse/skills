# Style reference — which arrow style for which morphism?

A practical guide to picking `tail` / `body` / `head` / `shape` for common
mathematical conventions. All values listed here are the constants exported
from `quiver_encoder` (e.g. `TAIL_MONO`, `BODY_DASHED`, `SHAPE_PULLBACK`).

## Mono-/epi-/iso-morphisms

| morphism | typical notation | style |
|---|---|---|
| monomorphism (mono / injection) | `↣` | `tail=TAIL_MONO` |
| monomorphism (Bourbaki style) | hook | `tail=TAIL_HOOK_TOP` (or `_BOTTOM`) |
| epimorphism (epi / surjection) | `↠` | `head=HEAD_EPI` |
| isomorphism | `≅` arrow | usually a normal arrow with label `\cong`; quiver has no built-in iso style |

Subobject inclusions are conventionally drawn as `↣` (mono) or as a hook;
the hook is more common in topology and algebraic geometry.

## Set-theoretic / type-theoretic notation

| concept | style |
|---|---|
| function `f: A → B` | normal arrow (default) |
| element-wise mapping `a ↦ f(a)` | `tail=TAIL_MAPS_TO` |
| partial function | usually `head=HEAD_HARPOON_TOP` (less standard) |

## Universal-property dashed arrows

The unique map factoring through a (co)limit is conventionally drawn dashed:

```python
q.edge(src, apex, r"\langle a, b \rangle", body=BODY_DASHED)
```

This applies to:

- pullback / pushout mediating maps,
- product / coproduct universal arrows,
- equaliser / coequaliser mediators,
- the unique map from an initial object,
- the unique map to a terminal object,
- exponential transposes (curry/uncurry).

## Pullback / pushout marker

A right-angle in the inner corner of a pullback or pushout square. Add it as
a separate (invisible) edge from the apex to the diagonally opposite vertex:

```python
# pullback (apex top-left, diagonally opposite is bottom-right)
q.edge(P, C, "", ALIGN_CENTRE, shape=SHAPE_PULLBACK)

# pushout (apex bottom-right, diagonally opposite is top-left)
q.edge(A, P, "", ALIGN_CENTRE, shape=SHAPE_PULLBACK_INV)
```

The corner draws nothing else; the body, tail, and head are ignored.

## Adjunctions

Convention: left adjoint `F` on top pointing one way, right adjoint `G` on
the bottom pointing the other way, with `⊣` between them.

```python
c = q.vertex(0, 0, r"\mathcal C")
d = q.vertex(2, 0, r"\mathcal D")
f = q.edge(c, d, "F", curve=-2)   # top arrow, curves up
g = q.edge(d, c, "G", curve=-2)   # bottom arrow (still curve=-2 because direction flipped)
q.edge(f, g, shape=SHAPE_ADJUNCTION)
```

The `⊣` glyph faces the right adjoint; quiver picks orientation automatically
based on the direction of `f` and `g`.

## Natural transformations and 2-cells

A natural transformation `α: F ⇒ G` between parallel functors `F, G : C → D`:

1. Curve F upward (`curve=-2`) and G downward (`curve=+2`) so they're visible.
2. Add a 2-cell from F to G with `level=2` (the double-line body).
3. Use `shorten_source`/`shorten_target` so the 2-cell doesn't touch the
   curved functors.

```python
f = q.edge(C, D, "F", curve=-2)
g = q.edge(C, D, "G", ALIGN_RIGHT, curve=2)
q.edge(f, g, r"\alpha", ALIGN_CENTRE, level=2,
       shorten_source=20, shorten_target=20)
```

For higher cells (modifications between natural transformations), repeat the
pattern: a 3-cell has a 2-cell as src/tgt and `level=3`.

## Other body styles

| body | when to use |
|---|---|
| `BODY_SOLID` (default) | normal morphism |
| `BODY_DASHED` | universal map, sometimes also "definitional" arrows |
| `BODY_DOTTED` | hypothetical/conditional arrow, sometimes natural-transformation components |
| `BODY_SQUIGGLY` | rewriting / reduction (`⤳`), sometimes nat. trans. between profunctors |
| `BODY_BARRED` | corestriction or "marked" map; also sometimes used for proarrows in double categories |
| `BODY_DOUBLE_BARRED` | two-cell in some pasting-diagram conventions |
| `BODY_BULLET_SOLID` / `BULLET_HOLLOW` | rare; specific 2-categorical notations |

## Head styles

| head | when to use |
|---|---|
| `HEAD_ARROWHEAD` (default) | normal arrow |
| `HEAD_NONE` | line without an arrowhead — useful for "shape=none" segments or when you'll add a custom marker |
| `HEAD_EPI` | epimorphism `↠` |
| `HEAD_HARPOON_TOP` / `HEAD_HARPOON_BOTTOM` | one-sided arrowhead — sometimes used for partial functions, or in quiver representation theory |

## Tail styles

| tail | when to use |
|---|---|
| `TAIL_NONE` (default) | most arrows |
| `TAIL_MONO` | monomorphism `↣` |
| `TAIL_MAPS_TO` | element map `↦` |
| `TAIL_HOOK_TOP` / `TAIL_HOOK_BOTTOM` | hook tail; common in subobject inclusions especially in topology |
| `TAIL_ARROWHEAD` | rare; "arrow with two arrowheads" |

## Combining styles

Each of `tail` / `body` / `head` is independent — combine freely:

```python
# A "quasi-isomorphism" arrow: normal mono with a tilde overlay isn't
# directly supported, but ≃ in label achieves the same:
q.edge(a, b, r"\sim", body=BODY_SQUIGGLY)

# A dashed mono (e.g. a hypothesised injection):
q.edge(a, b, "i", tail=TAIL_MONO, body=BODY_DASHED)

# An epi with no tail:
q.edge(a, b, "p", head=HEAD_EPI)
```

## When labels need positioning help

- `alignment` controls which side of the arrow the label goes:
  `ALIGN_LEFT` (default) puts it on the left of the source→target direction;
  `ALIGN_RIGHT` on the right; `ALIGN_CENTRE` covers the line (with white
  background); `ALIGN_OVER` sits on the line transparently.

- `label_position` (0..100) shifts the label along the arrow. Use 30 or 70
  to nudge a label away from a crowded midpoint.

- For two parallel arrows with labels, put one label on the left
  (`ALIGN_LEFT`) and the other on the right (`ALIGN_RIGHT`) so they don't
  collide:

  ```python
  q.edge(a, b, "f", offset=-2)                    # default ALIGN_LEFT
  q.edge(a, b, "g", ALIGN_RIGHT, offset=2)
  ```

## Colour cheatsheet

Colours are HSL: `(hue 0-360, sat 0-100, light 0-100, alpha 0-1)`.

| use | suggested HSL |
|---|---|
| red (highlight) | `(0, 60, 60)` |
| yellow | `(60, 60, 60)` |
| green | `(120, 60, 60)` |
| cyan | `(180, 60, 60)` |
| blue | `(240, 60, 60)` |
| magenta | `(300, 60, 60)` |

`saturation=60, lightness=60` gives readable colours that pair well with
black labels. For label colours pass `label_colour=`; for arrow colours pass
`colour=`.
