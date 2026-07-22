"""Resolução centralizada de recursos em desenvolvimento e executáveis."""

from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "assets").is_dir():
            return parent
    return Path(getattr(sys, "_MEIPASS", Path.cwd()))


def assets_dir() -> Path:
    bundled = Path(getattr(sys, "_MEIPASS", project_root())) / "assets"
    return bundled if bundled.is_dir() else project_root() / "assets"


def asset_path(name: str, *, required: bool = True) -> Path:
    path = assets_dir() / name
    if required and not path.is_file():
        raise FileNotFoundError(f"Asset obrigatório não encontrado: {path}")
    return path


def validate_assets(names: set[str]) -> list[str]:
    return sorted(name for name in names if not asset_path(name, required=False).is_file())
