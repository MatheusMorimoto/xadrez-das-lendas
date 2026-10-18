"""Modelos imutáveis usados para configurar as fases da campanha."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .asset_catalog import piece_asset
from .board import Board
from .piece import Color, Piece, PieceType, Square

ObjectiveKind = Literal["checkmate", "target"]


@dataclass(frozen=True, slots=True)
class PieceSetup:
    row: int
    col: int
    tipo: PieceType
    cor: Color
    variant: int = 1

    @property
    def asset(self) -> str:
        return piece_asset(self.tipo, self.cor, self.variant)


@dataclass(frozen=True, slots=True)
class Phase:
    number: int
    turn: Color
    inverted: bool
    pieces: tuple[PieceSetup, ...]
    objective: ObjectiveKind = "checkmate"
    target_piece: PieceType | None = None
    target_square: Square | None = None
    videos: tuple[str, ...] = ()
    victory_image: str | None = None
    victory_image_ms: int = 0
    victory_image_after_videos: bool = False

    def create_board(self) -> Board:
        return Board([Piece(p.tipo, p.cor, p.row, p.col, p.asset) for p in self.pieces])


def P(row: int, col: int, tipo: PieceType, cor: Color, variant: int = 1) -> PieceSetup:
    """Atalho legível para declarar uma peça de uma fase."""
    return PieceSetup(row, col, tipo, cor, variant)
