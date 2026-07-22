"""Posições e objetivos configuráveis das três fases originais."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .board import Board
from .piece import Color, Piece, PieceType, Square

ObjectiveKind = Literal["checkmate", "target"]


@dataclass(frozen=True, slots=True)
class PieceSetup:
    asset: str
    row: int
    col: int
    tipo: PieceType
    cor: Color


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

    def create_board(self) -> Board:
        return Board([Piece(p.tipo, p.cor, p.row, p.col, p.asset) for p in self.pieces])


def P(asset: str, row: int, col: int, tipo: PieceType, cor: Color) -> PieceSetup:
    return PieceSetup(asset, row, col, tipo, cor)


PHASES: dict[int, Phase] = {
    1: Phase(
        1,
        "branca",
        False,
        (
            P("rainha_branca.png", 1, 4, "rainha", "branca"),
            P("rei_branco.png", 2, 3, "rei", "branca"),
            P("cavalo_branco_2.png", 3, 6, "cavalo", "branca"),
            P("rei_preto.png", 0, 7, "rei", "preta"),
        ),
        videos=("YARA.mp4",),
    ),
    2: Phase(
        2,
        "preta",
        True,
        (
            P("rei_branco.png", 7, 7, "rei", "branca"),
            P("rainha_branca.png", 6, 2, "rainha", "branca"),
            P("torre_branca_2.png", 7, 6, "torre", "branca"),
            P("bispo_branco 1 .png", 5, 3, "bispo", "branca"),
            P("cavalo_branco_2.png", 5, 2, "cavalo", "branca"),
            P("cavalo_branco_2.png", 6, 3, "cavalo", "branca"),
            P("peao_branco 1.png", 6, 0, "peao", "branca"),
            P("peao_branco 2.png", 6, 1, "peao", "branca"),
            P("peao_branco 4.png", 4, 3, "peao", "branca"),
            P("peao_branco 5.png", 5, 5, "peao", "branca"),
            P("peao_branco 6.png", 6, 6, "peao", "branca"),
            P("peao_branco 7.png", 6, 7, "peao", "branca"),
            P("rei_preto.png", 0, 6, "rei", "preta"),
            P("torre_preta.png", 0, 0, "torre", "preta"),
            P("torre_preta_2.png", 0, 5, "torre", "preta"),
            P("bispo_preta.png", 4, 5, "bispo", "preta"),
            P("cavalo_preto .png", 1, 3, "cavalo", "preta"),
            P("cavalo_preto_2.png", 5, 7, "cavalo", "preta"),
            P("peão_preto 1.png", 1, 0, "peao", "preta"),
            P("peão_preto 2.png", 1, 1, "peao", "preta"),
            P("peão_preto 3.png", 2, 2, "peao", "preta"),
            P("peão_preto 4.png", 3, 5, "peao", "preta"),
            P("peão_preto 5.png", 1, 6, "peao", "preta"),
            P("peão_preto 6.png", 1, 7, "peao", "preta"),
        ),
        videos=("cucacaldeirao.mp4",),
    ),
    3: Phase(
        3,
        "preta",
        True,
        (
            P("rei_preto.png", 1, 3, "rei", "preta"),
            P("rainha_preta.png", 4, 5, "rainha", "preta"),
            P("cavalo_preto .png", 4, 4, "cavalo", "preta"),
            P("peão_preto 1.png", 1, 0, "peao", "preta"),
            P("peão_preto 2.png", 1, 2, "peao", "preta"),
            P("peão_preto 3.png", 1, 5, "peao", "preta"),
            P("peão_preto 4.png", 1, 6, "peao", "preta"),
            P("peão_preto 5.png", 1, 7, "peao", "preta"),
            P("rei_branco.png", 4, 7, "rei", "branca"),
            P("rainha_branca.png", 0, 7, "rainha", "branca"),
            P("torre_branca_2.png", 7, 7, "torre", "branca"),
            P("torre_branca_2.png", 4, 0, "torre", "branca"),
            P("bispo_branco 1 .png", 7, 5, "bispo", "branca"),
            P("cavalo_branco_2.png", 5, 5, "cavalo", "branca"),
            P("peao_branco 1.png", 6, 4, "peao", "branca"),
            P("peao_branco 2.png", 6, 7, "peao", "branca"),
            P("peao_branco 4.png", 4, 6, "peao", "branca"),
            P("peao_branco 5.png", 5, 7, "peao", "branca"),
        ),
        objective="target",
        target_piece="rainha",
        target_square=(3, 6),
        videos=("cuca.mp4", "boitata.mp4"),
    ),
}


def get_phase(number: int) -> Phase:
    try:
        return PHASES[number]
    except KeyError as exc:
        raise ValueError(f"Fase inexistente: {number}") from exc
