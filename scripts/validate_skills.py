#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["skills-ref"]
# ///
"""Validate SKILL.md frontmatter and check best-practice guidelines.

Validity (hard errors, fail CI):
    Delegates to the `skills-ref` reference library (Agent Skills spec):
    required fields, name/description length & charset, name/dir match, etc.

Best practices (warnings, do not fail CI unless --strict):
    - Combined `name` + `description` should stay roughly within the ~100
      token budget that gets loaded into every prompt (Level 1 of progressive
      disclosure). Token count is estimated as len(text) / 4 (chars-per-token
      rule of thumb), since no exact tokenizer is bundled here.

Usage:
    python3 scripts/validate_skills.py [--strict] [path ...]

    With no path arguments, validates every skills/*/ directory.
"""

import argparse
import sys
from pathlib import Path

try:
    from skills_ref.parser import read_properties
    from skills_ref.validator import validate
except ImportError:
    print(
        "error: the 'skills-ref' package is required.\n"
        "  run via: uv run scripts/validate_skills.py\n"
        "  or install manually: pip install skills-ref",
        file=sys.stderr,
    )
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
TOKEN_BUDGET = 100
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / CHARS_PER_TOKEN))


def discover_skill_dirs() -> list[Path]:
    skills_dir = REPO_ROOT / "skills"
    return sorted(p.parent for p in skills_dir.glob("*/SKILL.md"))


def check_best_practices(skill_dir: Path) -> list[str]:
    warnings = []
    try:
        props = read_properties(skill_dir)
    except Exception:
        # Frontmatter is broken; the validity check already reports this.
        return warnings

    combined = f"{props.name} {props.description}".strip()
    tokens = estimate_tokens(combined)
    if tokens > TOKEN_BUDGET:
        warnings.append(
            f"name + description is ~{tokens} tokens (estimated), "
            f"exceeding the recommended {TOKEN_BUDGET}-token budget for "
            "always-loaded metadata"
        )
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="skill directories to check")
    parser.add_argument(
        "--strict", action="store_true", help="treat best-practice warnings as errors"
    )
    args = parser.parse_args()

    skill_dirs = [p.resolve() for p in args.paths] if args.paths else discover_skill_dirs()
    if not skill_dirs:
        print("no skills found to validate")
        return 0

    had_error = False
    had_warning = False

    for skill_dir in skill_dirs:
        errors = validate(skill_dir)
        warnings = check_best_practices(skill_dir)

        if not errors and not warnings:
            print(f"OK    {skill_dir.relative_to(REPO_ROOT) if skill_dir.is_relative_to(REPO_ROOT) else skill_dir}")
            continue

        print(f"---   {skill_dir.relative_to(REPO_ROOT) if skill_dir.is_relative_to(REPO_ROOT) else skill_dir}")
        for error in errors:
            print(f"  ERROR   {error}")
            had_error = True
        for warning in warnings:
            print(f"  WARNING {warning}")
            had_warning = True

    print()
    if had_error or (had_warning and args.strict):
        print("validation failed")
        return 1

    if had_warning:
        print("validation passed with warnings")
    else:
        print("validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
