# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project_root = Path(SPECPATH)

analysis = Analysis(
    [str(project_root / "src" / "xadrez_das_lendas" / "__main__.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=[(str(project_root / "assets"), "assets")],
    hiddenimports=["cv2"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="XadrezDasLendas",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(project_root / "assets" / "tela jogo.ico"),
)

