"""Partidas tradicionais contra outra pessoa ou contra a máquina."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

from .asset_catalog import piece_asset
from .board import Board
from .piece import Color, Piece, Square
from .rules import (
    apply_legal_move,
    is_checkmate,
    is_in_check,
    is_insufficient_material,
    is_stalemate,
    legal_moves,
    opponent,
)

VersusMode = Literal["machine", "person"]
PIECE_VALUE = {"peao": 1, "cavalo": 3, "bispo": 3, "torre": 5, "rainha": 9, "rei": 100}


def standard_board() -> Board:
    pieces: list[Piece] = []
    order = ("torre", "cavalo", "bispo", "rainha", "rei", "bispo", "cavalo", "torre")
    variants: dict[str, int] = {}
    for color, back_row, pawn_row in (("preta", 0, 1), ("branca", 7, 6)):
        variants.clear()
        for col, kind in enumerate(order):
            variants[kind] = variants.get(kind, 0) + 1
            variant = variants[kind] if kind in ("torre", "bispo", "cavalo") else 1
            pieces.append(Piece(kind, color, back_row, col, piece_asset(kind, color, variant)))
        for col in range(8):
            pieces.append(Piece("peao", color, pawn_row, col, piece_asset("peao", color, col + 1)))
    return Board(pieces)


def all_moves(board: Board, color: Color) -> list[tuple[Square, Square]]:
    return [
        (piece.square, target)
        for piece in board.pieces
        if piece.cor == color
        for target in legal_moves(piece, board)
    ]


def choose_machine_move(board: Board, color: Color, level: int, rng: random.Random | None = None) -> tuple[Square, Square]:
    rng = rng or random.Random()
    moves = all_moves(board, color)
    if not moves:
        raise ValueError("A máquina não possui movimentos legais")
    if level <= 1:
        return rng.choice(moves)

    def score(move: tuple[Square, Square]) -> float:
        origin, target = move
        captured = board.piece_at(target)
        value = PIECE_VALUE[captured.tipo] if captured is not None else 0
        simulation = board.clone()
        apply_legal_move(simulation, origin, target)
        if is_checkmate(simulation, opponent(color)):
            return 10_000
        result = value * 20 + (4 if is_in_check(simulation, opponent(color)) else 0)
        if level >= 3:
            replies = all_moves(simulation, opponent(color))
            worst_loss = 0
            for reply_origin, reply_target in replies:
                reply_capture = simulation.piece_at(reply_target)
                if reply_capture is not None:
                    worst_loss = max(worst_loss, PIECE_VALUE[reply_capture.tipo])
            result -= worst_loss * 12
        return result + rng.random()

    return max(moves, key=score)


@dataclass
class VersusMatch:
    mode: VersusMode
    difficulty: int = 1
    board: Board | None = None
    turn: Color = "branca"
    human_color: Color = "branca"
    player_one_color: Color = "branca"
    selected: Square | None = None
    valid_moves: list[Square] | None = None
    message: str = ""
    finished: bool = False
    hints_left: int = 3
    halfmove_clock: int = 0
    position_history: list[tuple] | None = None

    def __post_init__(self) -> None:
        self.board = self.board or standard_board()
        self.valid_moves = self.valid_moves or []
        self.position_history = self.position_history or [self._position_key()]

    @property
    def inverted(self) -> bool:
        if self.mode == "machine":
            return self.human_color == "preta"
        return self.turn == "preta"

    def play(self, origin: Square, target: Square) -> None:
        assert self.board is not None
        moving = self.board.piece_at(origin)
        capture = self.board.piece_at(target) is not None or (
            moving is not None and moving.tipo == "peao" and target == self.board.en_passant
        )
        pawn_move = moving is not None and moving.tipo == "peao"
        moved = apply_legal_move(self.board, origin, target)
        self.halfmove_clock = 0 if pawn_move or capture else self.halfmove_clock + 1
        self.turn = opponent(self.turn)
        self.position_history.append(self._position_key())
        self.selected = None
        self.valid_moves = []
        if is_checkmate(self.board, self.turn):
            self.finished = True
            self.message = f"Xeque-mate! Vitória das {moved.cor}s."
        elif is_stalemate(self.board, self.turn):
            self.finished = True
            self.message = "Empate por afogamento."
        elif is_insufficient_material(self.board):
            self.finished = True
            self.message = "Empate por material insuficiente."
        elif self.halfmove_clock >= 100:
            self.finished = True
            self.message = "Empate pela regra dos 50 movimentos."
        elif self.position_history.count(self.position_history[-1]) >= 3:
            self.finished = True
            self.message = "Empate por repetição tripla."
        elif is_in_check(self.board, self.turn):
            self.message = "Xeque!"
        else:
            self.message = f"Vez das {self.turn}s"

    def hint(self) -> tuple[Square, Square] | None:
        assert self.board is not None
        if self.hints_left <= 0 or self.finished:
            self.message = "As 3 dicas já foram utilizadas."
            return None
        self.hints_left -= 1
        move = choose_machine_move(self.board, self.turn, 3)
        self.message = f"Dica: {notation(move[0])} → {notation(move[1])} ({self.hints_left} restantes)"
        return move

    def _position_key(self) -> tuple:
        assert self.board is not None
        pieces = tuple(
            sorted((piece.tipo, piece.cor, piece.row, piece.col, piece.moved) for piece in self.board.pieces)
        )
        return pieces, self.turn, self.board.en_passant


def notation(square: Square) -> str:
    return f"{chr(ord('a') + square[1])}{8 - square[0]}"
