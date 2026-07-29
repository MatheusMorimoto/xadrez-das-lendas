"""Catálogo central dos recursos visuais usados pelas peças."""

from __future__ import annotations

from .piece import Color, PieceType

PieceAssetKey = tuple[PieceType, Color, int]

PIECE_ASSETS: dict[PieceAssetKey, str] = {
    ("rei", "branca", 1): "rei_branco.jpeg",
    ("rei", "preta", 1): "rei_preto.jpeg",
    ("rainha", "branca", 1): "rainha_branca.jpeg",
    ("rainha", "preta", 1): "rainha_preta.jpeg",
    ("torre", "branca", 1): "torre branca.jpeg",
    ("torre", "branca", 2): "torre branca_2.jpeg",
    ("torre", "preta", 1): "torre_preta.jpeg",
    ("torre", "preta", 2): "torre_preta_2.jpeg",
    ("bispo", "branca", 1): "bispo_branco 1.jpeg",
    ("bispo", "branca", 2): "bispo_branco_2.jpeg",
    ("bispo", "preta", 1): "bispo_preta.jpeg",
    ("bispo", "preta", 2): "bispo_preta_2.jpeg",
    ("cavalo", "branca", 1): "cavalo_branco.jpeg",
    ("cavalo", "branca", 2): "cavalo_branco_2.jpeg",
    ("cavalo", "preta", 1): "cavalo_preto.jpeg",
    ("cavalo", "preta", 2): "cavalo_preto_2.jpeg",
    **{("peao", "branca", number): f"peao_branco {number}.jpeg" for number in range(1, 9)},
    **{("peao", "preta", number): f"peão_preto {number}.jpeg" for number in range(1, 9)},
}


def piece_asset(piece_type: PieceType, color: Color, variant: int = 1) -> str:
    """Retorna o nome exato do arquivo correspondente à peça."""
    try:
        return PIECE_ASSETS[piece_type, color, variant]
    except KeyError as exc:
        raise ValueError(f"Visual de peça inexistente: {piece_type}/{color}/{variant}") from exc
