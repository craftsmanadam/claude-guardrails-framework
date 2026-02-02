from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def _normalize_nodes(items):
    if not items:
        return []
    normalized = []
    for sub in items:
        normalized.append(_normalize_node(sub))
    return normalized


def _normalize_node(item):
    if isinstance(item, str):
        return {"text": item, "children": []}
    if isinstance(item, dict) and "text" in item:
        children = _normalize_nodes(item.get("items") or item.get("subitems"))
        return {"text": item["text"], "children": children}
    if isinstance(item, dict) and len(item) == 1:
        key, value = next(iter(item.items()))
        if isinstance(key, str) and isinstance(value, list):
            return {"text": key, "children": _normalize_nodes(value)}
    raise ValueError(f"Invalid node: {item}")


def normalize_item(item):
    if isinstance(item, str):
        return {"text": item, "when": None, "exclude_when": None, "children": []}
    if isinstance(item, dict) and "text" in item:
        when = item.get("when")
        exclude_when = item.get("exclude_when")
        children = _normalize_nodes(item.get("items") or item.get("subitems"))
        return {
            "text": item["text"],
            "when": when,
            "exclude_when": exclude_when,
            "children": children,
        }
    if isinstance(item, dict) and len(item) == 1:
        key, value = next(iter(item.items()))
        if isinstance(key, str) and isinstance(value, list):
            return {
                "text": key,
                "when": None,
                "exclude_when": None,
                "children": _normalize_nodes(value),
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


def _node_key(node):
    return (node["text"], tuple(_node_key(child) for child in node.get("children", [])))


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
                children = normalized.get("children") or []
                key = (heading, text, tuple(_node_key(child) for child in children))
                if key in seen:
                    continue
                seen.add(key)
                bucket.append({"text": text, "children": children})
    return merged


def _render_node(node, indent):
    lines = [f"{indent}- {node['text']}"]
    child_indent = indent + "  "
    for child in node.get("children", []):
        lines.extend(_render_node(child, child_indent))
    return lines


def render_sections(merged):
    lines = []
    for heading in merged:
        lines.append(f"## {heading}")
        for item in merged[heading]:
            lines.extend(_render_node(item, ""))
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
