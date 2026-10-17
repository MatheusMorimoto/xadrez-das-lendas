"""Modelo de uma peça, sem dependência da interface gráfica."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

Color = Literal["branca", "preta"]
PieceType = Literal["rei", "rainha", "torre", "bispo", "cavalo", "peao"]
Square = tuple[int, int]


@dataclass(slots=True)
class Piece:
    tipo: PieceType
    cor: Color
    row: int
    col: int
    asset_name: str
    moved: bool = False

    @property
    def square(self) -> Square:
        return self.row, self.col

    def copy(self) -> Piece:
        return replace(self)
