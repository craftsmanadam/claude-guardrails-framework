from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def _normalize_subitems(items):
    if not items:
        return []
    normalized = []
    for sub in items:
        if isinstance(sub, str):
            normalized.append(sub)
            continue
        if isinstance(sub, dict) and "text" in sub:
            normalized.append(sub["text"])
            continue
        if isinstance(sub, dict) and len(sub) == 1:
            key, value = next(iter(sub.items()))
            if isinstance(key, str) and isinstance(value, list):
                normalized.append(key)
                normalized.extend(_normalize_subitems(value))
                continue
        raise ValueError(f"Invalid subitem: {sub}")
    return normalized


def normalize_item(item):
    if isinstance(item, str):
        return {"text": item, "when": None, "exclude_when": None, "subitems": []}
    if isinstance(item, dict) and "text" in item:
        when = item.get("when")
        exclude_when = item.get("exclude_when")
        subitems = _normalize_subitems(item.get("items") or item.get("subitems"))
        return {
            "text": item["text"],
            "when": when,
            "exclude_when": exclude_when,
            "subitems": subitems,
        }
    if isinstance(item, dict) and len(item) == 1:
        key, value = next(iter(item.items()))
        if isinstance(key, str) and isinstance(value, list):
            return {
                "text": key,
                "when": None,
                "exclude_when": None,
                "subitems": _normalize_subitems(value),
            }
    raise ValueError(f"Invalid rule item: {item}")


def condition_matches(cond, active_profile, active_targets, active_packs):
    if not cond:
        return True
    profiles = cond.get("profiles")
    if profiles and active_profile not in profiles:
        return False
    targets = cond.get("targets")
    if targets and not all(t in active_targets for t in targets):
        return False
    packs = cond.get("packs")
    if packs and not all(p in active_packs for p in packs):
        return False
    return True


def exclude_matches(cond, active_profile, active_targets, active_packs):
    if not cond:
        return False
    profiles = cond.get("profiles")
    if profiles and active_profile in profiles:
        return True
    targets = cond.get("targets")
    if targets and any(t in active_targets for t in targets):
        return True
    packs = cond.get("packs")
    if packs and any(p in active_packs for p in packs):
        return True
    return False


def merge_sections(units, active_profile: str, active_targets, active_packs):
    merged = {}
    seen = set()
    for unit in units:
        for heading, items in (unit.get("sections") or {}).items():
            bucket = merged.setdefault(heading, [])
            for item in items:
                normalized = normalize_item(item)
                if not condition_matches(
                    normalized.get("when"), active_profile, active_targets, active_packs
                ):
                    continue
                if exclude_matches(
                    normalized.get("exclude_when"), active_profile, active_targets, active_packs
                ):
                    continue
                text = normalized["text"]
                subitems = normalized.get("subitems") or []
                key = (heading, text, tuple(subitems))
                if key in seen:
                    continue
                seen.add(key)
                bucket.append({"text": text, "subitems": subitems})
    return merged


def render_sections(merged):
    lines = []
    for heading in merged:
        lines.append(f"## {heading}")
        for item in merged[heading]:
            text = item["text"]
            lines.append(f"- {text}")
            subitems = item.get("subitems") or []
            for sub in subitems:
                lines.append(f"  - {sub}")
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


def read_template():
    template_path = BASE_DIR / "templates" / "claude.md.tmpl"
    return template_path.read_text(encoding="utf-8")


def write_output(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
