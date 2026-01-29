#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import LiteralString

try:
    import yaml
except Exception as exc:
    print("Missing dependency: pyyaml. Install with 'poetry install'.")
    raise SystemExit(1) from exc

from loader import load_unit, read_yaml
from renderer import merge_sections, read_template, render_sections, render_template, write_output


def main(argv):
    if len(argv) != 3:
        print("Usage: compose.py <composition.yml> <output.md>")
        return 1

    spec_path = Path(argv[1])
    out_path = Path(argv[2])
    spec = read_yaml(spec_path)

    profile_name = spec.get("profile")
    targets = spec.get("targets", [])
    packs = spec.get("packs", [])

    if not profile_name:
        raise ValueError("composition is missing 'profile'")

    sections = _sections(packs, profile_name, targets)
    template = read_template()
    output = render_template(template, profile_name, targets, packs, sections)

    write_output(out_path, output)

    print(f"Wrote {out_path}")
    return 0


def _sections(packs, profile_name, targets) -> LiteralString:
    units = [load_unit("profile", profile_name)]
    units.extend(load_unit("target", t) for t in targets)
    units.extend(load_unit("pack", p) for p in packs)

    merged = merge_sections(units, profile_name, targets, packs)
    sections = render_sections(merged)
    return sections


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
