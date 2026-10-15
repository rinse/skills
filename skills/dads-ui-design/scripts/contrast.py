#!/usr/bin/env python3
"""WCAG 2.x contrast ratio judged against the DADS thresholds.

Usage:
    python3 contrast.py FG BG          one pair, e.g. python3 contrast.py '#0017c1' '#ffffff'
    python3 contrast.py --key C50 C100 ... C1200
                                       a 13-step key color scale (50, 100, 200, ..., 1200),
                                       checked on every pair the DADS code snippets use
    python3 contrast.py                run the self-check

DADS requires 4.5:1 for all text (no large-text exception) and 3:1 for non-text.
Colors are opaque #rrggbb only; Opacity Gray (rgba) must be flattened onto its background first.
"""

import sys

STEPS = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "1000", "1100", "1200"]
WHITE = "#ffffff"

# (foreground step, background step, threshold). "W" is white.
# Collected from --color-key-* usages in digital-go-jp/design-system-example-components-html (src/components/*.css).
KEY_PAIRS = [
    ("900", "W", 4.5),  # outline/text button label, date-picker, search-box, menu-list
    ("W", "900", 4.5),  # solid button label, calendar selected date
    ("W", "1000", 4.5),  # solid button hover
    ("W", "1200", 4.5),  # solid button active
    ("1000", "W", 4.5),  # accordion, disclosure, horizontal-menu, page-navigation, carousel
    ("1000", "50", 4.5),  # text button hover, menu-list
    ("1000", "100", 4.5),  # menu-list current, search-box checked option
    ("1000", "200", 4.5),  # outline button hover, page-navigation hover
    ("1200", "100", 4.5),  # text button active
    ("1200", "300", 4.5),  # outline button active, page-navigation active, carousel active
    ("900", "50", 4.5),  # menu-list hover, search-box option hover
    ("900", "200", 4.5),  # date-picker calendar button hover
    ("900", "300", 4.5),  # date-picker calendar button active
    ("900", "W", 3.0),  # checkbox/radio accent, switch, tab indicator, heading rule (non-text)
    ("1100", "W", 3.0),  # checkbox/radio hover accent, switch (non-text)
]


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"not a #rrggbb color: {hex_color}")
    channels = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check_key(scale: list[str]) -> list[str]:
    """Return a failure line per KEY_PAIRS entry the scale misses."""
    color = dict(zip(STEPS, scale), W=WHITE)
    fails = []
    for fg, bg, need in KEY_PAIRS:
        r = ratio(color[fg], color[bg])
        if r < need:
            fails.append(f"key-{fg} on key-{bg}: {r:.2f}:1 < {need}:1".replace("key-W", "white"))
    return fails


DADS_BLUE = ["#e8f1fe", "#d9e6ff", "#c5d7fb", "#9db7f9", "#7096f8", "#4979f5", "#3460fb",
             "#264af4", "#0031d8", "#0017c1", "#00118f", "#000071", "#000060"]


def _self_check() -> None:
    assert round(ratio("#000000", "#ffffff"), 2) == 21.0
    assert ratio("#767676", "#ffffff") >= 4.5 > ratio("#7f7f7f", "#ffffff")  # Gray-536 is the text boundary
    assert ratio("#949494", "#ffffff") >= 3.0 > ratio("#999999", "#ffffff")  # Gray-420 is the non-text boundary
    assert ratio("#fff", "#000") == ratio("#000000", "#ffffff")
    assert check_key(DADS_BLUE) == []  # the default key color passes every pair
    assert check_key(["#ffffff"] * 13)  # an all-white scale fails
    print("self-check passed")


def main(argv: list[str]) -> int:
    if not argv:
        _self_check()
        return 0
    if argv[0] == "--key":
        if len(argv) != 14:
            print(f"--key needs 13 colors ({', '.join(STEPS)}), got {len(argv) - 1}", file=sys.stderr)
            return 2
        fails = check_key(argv[1:])
        print("\n".join(fails) if fails else f"all {len(KEY_PAIRS)} pairs pass")
        return 1 if fails else 0
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    r = ratio(*argv)
    text = "pass" if r >= 4.5 else "FAIL"
    non_text = "pass" if r >= 3.0 else "FAIL"
    print(f"{r:.2f}:1  text(4.5) {text}  non-text(3) {non_text}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
