"""Máquina de estados do jogo, independente de tempo e renderização."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .board import Board
from .phases import Phase, get_phase
from .piece import Piece, Square
from .rules import apply_legal_move, is_checkmate, opponent


class ScreenState(str, Enum):
    MENU = "menu"
    PLAYING = "playing"
    TRANSITION = "transition"
    VIDEO = "video"
    PHASE_INTRO = "phase_intro"
    FINISHED = "finished"


@dataclass
class GameState:
    screen: ScreenState = ScreenState.MENU
    phase_number: int = 1
    phase: Phase = field(default_factory=lambda: get_phase(1))
    board: Board = field(default_factory=lambda: get_phase(1).create_board())
    selected: Square | None = None
    valid_moves: list[Square] = field(default_factory=list)
    message: str = ""
    last_move: str = ""
    reset_at: int | None = None

    def start_phase(self, number: int) -> None:
        self.phase_number = number
        self.phase = get_phase(number)
        self.board = self.phase.create_board()
        self.screen = ScreenState.PLAYING
        self.clear_selection()
        self.message = ""
        self.last_move = ""
        self.reset_at = None

    def show_phase_intro(self, number: int) -> None:
        self.phase_number = number
        self.phase = get_phase(number)
        self.board = self.phase.create_board()
        self.screen = ScreenState.PHASE_INTRO
        self.clear_selection()

    def return_to_menu(self) -> None:
        self.phase_number = 1
        self.phase = get_phase(1)
        self.board = self.phase.create_board()
        self.screen = ScreenState.MENU
        self.clear_selection()
        self.message = ""
        self.reset_at = None

    def clear_selection(self) -> None:
        self.selected = None
        self.valid_moves.clear()

    def objective_met(self, moved: Piece) -> bool:
        if self.phase.objective == "target":
            return moved.tipo == self.phase.target_piece and moved.square == self.phase.target_square
        return is_checkmate(self.board, opponent(moved.cor))

    def move(self, origin: Square, target: Square, now_ms: int = 0) -> bool:
        moving = self.board.piece_at(origin)
        if moving is None or moving.cor != self.phase.turn:
            raise ValueError("A peça escolhida não pertence ao turno da fase")
        moved = apply_legal_move(self.board, origin, target)
        self.last_move = f"{moved.tipo.capitalize()} {moved.cor}: {notation(origin)} → {notation(target)}"
        won = self.objective_met(moved)
        self.clear_selection()
        if won:
            self.message = "Movimento correto!"
            self.screen = ScreenState.TRANSITION
        else:
            self.message = "Movimento incorreto para vencer"
            self.reset_at = now_ms + 3000
        return won

    def update(self, now_ms: int) -> None:
        if self.reset_at is not None and now_ms >= self.reset_at:
            self.start_phase(self.phase_number)


def notation(square: Square) -> str:
    return f"{chr(ord('a') + square[1])}{8 - square[0]}"
