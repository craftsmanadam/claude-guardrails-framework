#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:
    print("Missing dependency: pyyaml. Install with 'pip install -r requirements.txt'.")
    raise SystemExit(1) from exc

BASE_DIR = Path(__file__).resolve().parents[1]


def read_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_unit(kind: str, name: str):
    folder = BASE_DIR / f"{kind}s"
    path = folder / f"{name}.yml"
    if not path.exists():
        raise FileNotFoundError(f"Missing {kind}: {path}")
    data = read_yaml(path)
    if data.get("kind") != kind:
        raise ValueError(f"Expected kind '{kind}' in {path}")
    return data


def normalize_item(item):
    if isinstance(item, str):
        return {"text": item, "profiles": None}
    if isinstance(item, dict) and "text" in item:
        profiles = item.get("profiles")
        return {"text": item["text"], "profiles": profiles}
    raise ValueError(f"Invalid rule item: {item}")


def include_item(item, active_profile: str):
    profiles = item.get("profiles")
    if not profiles:
        return True
    return active_profile in profiles


def merge_sections(units, active_profile: str):
    merged = {}
    seen = set()
    for unit in units:
        for heading, items in (unit.get("sections") or {}).items():
            bucket = merged.setdefault(heading, [])
            for item in items:
                normalized = normalize_item(item)
                if not include_item(normalized, active_profile):
                    continue
                text = normalized["text"]
                key = (heading, text)
                if key in seen:
                    continue
                seen.add(key)
                bucket.append(text)
    return merged


def render_sections(merged):
    lines = []
    for heading in merged:
        lines.append(f"## {heading}")
        for item in merged[heading]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_template(template: str, profile: str, targets: list, packs: list, sections: str):
    return (
        template
        .replace("{{ profile }}", profile)
        .replace("{{ targets }}", ", ".join(targets) if targets else "none")
        .replace("{{ packs }}", ", ".join(packs) if packs else "none")
        .replace("{{ sections }}", sections)
    )


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

    units = [load_unit("profile", profile_name)]
    units.extend(load_unit("target", t) for t in targets)
    units.extend(load_unit("pack", p) for p in packs)

    merged = merge_sections(units, profile_name)
    sections = render_sections(merged)

    template_path = BASE_DIR / "templates" / "claude.md.tmpl"
    template = template_path.read_text(encoding="utf-8")

    output = render_template(template, profile_name, targets, packs, sections)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")

    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
