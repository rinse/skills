"""
templates.py — Pre-built `Quiver` factories for common diagram patterns.

Each function returns a fresh ``Quiver`` instance with placeholder labels you
can either keep or override afterwards by mutating the underlying cells.
The intended workflow is:

    >>> q = templates.commutative_square(("A", "B", "C", "D"),
    ...                                  ("f", "g", "h", "k"))
    >>> print(q.to_url())

For more elaborate diagrams, copy a template's source as a starting point
rather than calling the factory.
"""

from __future__ import annotations

from quiver_encoder import (
    Quiver, ALIGN_LEFT, ALIGN_CENTRE, ALIGN_RIGHT,
    SHAPE_PULLBACK, SHAPE_PULLBACK_INV, SHAPE_ADJUNCTION,
    BODY_DASHED, HEAD_EPI, TAIL_MONO, TAIL_HOOK_TOP,
)
from typing import Optional


def commutative_square(
    vertices: tuple[str, str, str, str] = ("A", "B", "C", "D"),
    edges: tuple[str, str, str, str] = ("f", "g", "h", "k"),
) -> Quiver:
    """A 2×2 commutative square.

    Vertices, in (top-left, top-right, bottom-left, bottom-right) order::

        A --f--> B
        |        |
        h        k
        v        v
        C --g--> D

    Edges are (top, bottom, left, right) = (f, g, h, k).
    """
    q = Quiver()
    a = q.vertex(0, 0, vertices[0])
    b = q.vertex(1, 0, vertices[1])
    c = q.vertex(0, 1, vertices[2])
    d = q.vertex(1, 1, vertices[3])
    q.edge(a, b, edges[0])               # top
    q.edge(c, d, edges[1])               # bottom
    q.edge(a, c, edges[2], ALIGN_RIGHT)  # left (label on the right of the arrow)
    q.edge(b, d, edges[3])               # right
    return q


def triangle(
    vertices: tuple[str, str, str] = ("A", "B", "C"),
    edges: tuple[str, str, str] = ("f", "g", "h"),
) -> Quiver:
    """A commutative triangle with the apex at the top.

    ::

            A
           / \\
          f   g
         /     \\
        B---h--->C

    Edges in declaration order: A→B (f), A→C (g), B→C (h).
    """
    q = Quiver()
    a = q.vertex(1, 0, vertices[0])
    b = q.vertex(0, 1, vertices[1])
    c = q.vertex(2, 1, vertices[2])
    q.edge(a, b, edges[0], ALIGN_RIGHT)
    q.edge(a, c, edges[1])
    q.edge(b, c, edges[2])
    return q


def pullback(
    vertices: tuple[str, str, str, str] = (r"A \times_C B", "B", "A", "C"),
    edges: tuple[str, str, str, str] = (r"\pi_2", "g", r"\pi_1", "f"),
    *,
    universal_property: bool = False,
    apex_label: str = "X",
    universal_edges: tuple[str, str, str] = ("a", "b", r"\langle a, b \rangle"),
) -> Quiver:
    """A pullback square with the corner mark.

    Vertices are (apex P, top-right, bottom-left, bottom-right):

        P --π₂--> B
        |         |
        π₁        g
        v         v
        A ---f--> C  with corner mark at P pointing into C.

    If ``universal_property=True`` an additional vertex (default name "X") is
    added above-left of the apex, with curved arrows ``a`` to A and ``b`` to B
    and a dashed mediating arrow into the apex labelled ``⟨a, b⟩``.
    """
    q = Quiver()
    P = q.vertex(1, 1, vertices[0])
    B = q.vertex(2, 1, vertices[1])
    A = q.vertex(1, 2, vertices[2])
    C = q.vertex(2, 2, vertices[3])
    q.edge(P, B, edges[0])                       # π₂ (top)
    q.edge(B, C, edges[1])                       # g (right)
    q.edge(P, A, edges[2], ALIGN_RIGHT)          # π₁ (left)
    q.edge(A, C, edges[3], ALIGN_RIGHT)          # f (bottom)
    q.edge(P, C, "", ALIGN_CENTRE,
           shape=SHAPE_PULLBACK)                 # corner mark

    if universal_property:
        X = q.vertex(0, 0, apex_label)
        q.edge(X, A, universal_edges[0], ALIGN_RIGHT, curve=3)
        q.edge(X, B, universal_edges[1], ALIGN_LEFT, curve=-3)
        q.edge(X, P, universal_edges[2], ALIGN_CENTRE, body=BODY_DASHED)
    return q


def pushout(
    vertices: tuple[str, str, str, str] = ("A", "B", "C", r"B \sqcup_A C"),
    edges: tuple[str, str, str, str] = ("f", "g", r"\iota_1", r"\iota_2"),
) -> Quiver:
    """A pushout square with the inverse corner mark.

    ::

        A --f--> B
        |        |
        g        ι₁
        v        v
        C --ι₂-> P    with corner mark at P pointing back to A.
    """
    q = Quiver()
    A = q.vertex(0, 0, vertices[0])
    B = q.vertex(1, 0, vertices[1])
    C = q.vertex(0, 1, vertices[2])
    P = q.vertex(1, 1, vertices[3])
    q.edge(A, B, edges[0])
    q.edge(A, C, edges[1], ALIGN_RIGHT)
    q.edge(B, P, edges[2])
    q.edge(C, P, edges[3])
    q.edge(A, P, "", ALIGN_CENTRE, shape=SHAPE_PULLBACK_INV)
    return q


def adjunction(
    categories: tuple[str, str] = (r"\mathcal C", r"\mathcal D"),
    functors:   tuple[str, str] = ("F", "G"),
) -> Quiver:
    """Two opposing curved arrows F: C ⇄ D :G with the ⊣ glyph between them.

    Convention: ``F`` is the left adjoint (drawn as the upper, leftward-pointing
    arrow) and ``G`` is the right adjoint.
    """
    q = Quiver()
    c = q.vertex(0, 0, categories[0])
    d = q.vertex(2, 0, categories[1])
    f = q.edge(c, d, functors[0], curve=-2)
    g = q.edge(d, c, functors[1], curve=-2)
    q.edge(f, g, shape=SHAPE_ADJUNCTION)
    return q


def natural_transformation(
    categories: tuple[str, str] = ("C", "D"),
    functors:   tuple[str, str] = ("F", "G"),
    name: str = r"\alpha",
) -> Quiver:
    """A natural transformation α: F ⇒ G between parallel functors.

    Both functors point C → D; F curves up, G curves down, and α is a
    double-arrow (level=2) between them.
    """
    q = Quiver()
    c = q.vertex(0, 0, categories[0])
    d = q.vertex(2, 0, categories[1])
    f = q.edge(c, d, functors[0], curve=-2)
    g = q.edge(c, d, functors[1], ALIGN_RIGHT, curve=2)
    q.edge(f, g, name, ALIGN_CENTRE, level=2,
           shorten_source=20, shorten_target=20)
    return q


def parallel_arrows(
    src_label: str = "A",
    tgt_label: str = "B",
    arrow_labels: tuple[str, str] = ("f", "g"),
) -> Quiver:
    """Two parallel arrows A ⇉ B (e.g. for an equaliser diagram)."""
    q = Quiver()
    a = q.vertex(0, 0, src_label)
    b = q.vertex(1, 0, tgt_label)
    q.edge(a, b, arrow_labels[0], offset=-2)
    q.edge(a, b, arrow_labels[1], ALIGN_RIGHT, offset=2)
    return q


def equaliser(
    vertices: tuple[str, str, str] = ("E", "A", "B"),
    edges: tuple[str, str, str] = ("e", "f", "g"),
) -> Quiver:
    """An equaliser E ↪ A ⇉ B with a mono tail on the inclusion.

    ::

        E ↪-e--> A ⇉(f, g) B
    """
    q = Quiver()
    e = q.vertex(0, 0, vertices[0])
    a = q.vertex(1, 0, vertices[1])
    b = q.vertex(2, 0, vertices[2])
    q.edge(e, a, edges[0], tail=TAIL_MONO)
    q.edge(a, b, edges[1], offset=-2)
    q.edge(a, b, edges[2], ALIGN_RIGHT, offset=2)
    return q


def coequaliser(
    vertices: tuple[str, str, str] = ("A", "B", "Q"),
    edges: tuple[str, str, str] = ("f", "g", "q"),
) -> Quiver:
    """A coequaliser A ⇉ B ↠ Q with an epi head on the projection."""
    q = Quiver()
    a = q.vertex(0, 0, vertices[0])
    b = q.vertex(1, 0, vertices[1])
    qv = q.vertex(2, 0, vertices[2])
    q.edge(a, b, edges[0], offset=-2)
    q.edge(a, b, edges[1], ALIGN_RIGHT, offset=2)
    q.edge(b, qv, edges[2], head=HEAD_EPI)
    return q


def short_exact_sequence(
    vertices: tuple[str, str, str] = ("A", "B", "C"),
    edges: tuple[str, str] = ("f", "g"),
    *,
    with_zeroes: bool = True,
) -> Quiver:
    """A short exact sequence ``0 → A ↪ B ↠ C → 0``.

    Set ``with_zeroes=False`` to get just ``A ↪ B ↠ C`` without the trailing
    zero objects.
    """
    q = Quiver()
    if with_zeroes:
        z1 = q.vertex(0, 0, "0")
        a  = q.vertex(1, 0, vertices[0])
        b  = q.vertex(2, 0, vertices[1])
        c  = q.vertex(3, 0, vertices[2])
        z2 = q.vertex(4, 0, "0")
        q.edge(z1, a)
        q.edge(a, b, edges[0], tail=TAIL_MONO)
        q.edge(b, c, edges[1], head=HEAD_EPI)
        q.edge(c, z2)
    else:
        a = q.vertex(0, 0, vertices[0])
        b = q.vertex(1, 0, vertices[1])
        c = q.vertex(2, 0, vertices[2])
        q.edge(a, b, edges[0], tail=TAIL_MONO)
        q.edge(b, c, edges[1], head=HEAD_EPI)
    return q
