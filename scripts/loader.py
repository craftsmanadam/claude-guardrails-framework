from pathlib import Path

import yaml

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
    if data.get("name") != name:
        raise ValueError(f"Name mismatch in {path}: expected '{name}'")
    if data.get("kind") != kind:
        raise ValueError(f"Expected kind '{kind}' in {path}")
    return data
