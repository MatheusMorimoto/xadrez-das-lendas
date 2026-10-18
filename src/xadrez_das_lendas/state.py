"""Máquina de estados do jogo, independente de tempo e renderização."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .board import Board
from .phases import PHASES, Phase, get_phase
from .piece import Piece, Square
from .rules import apply_legal_move, is_checkmate, opponent
from .versus import VersusMatch

WRONG_MOVE_RESET_MS = 3000
WIN_TRANSITION_MS = 2500


class ScreenState(str, Enum):
    MENU = "menu"
    ABOUT = "about"
    VERSUS_MENU = "versus_menu"
    DIFFICULTY = "difficulty"
    VERSUS_PLAYING = "versus_playing"
    PODIUM = "podium"
    MATCH_RECORD = "match_record"
    PLAYING = "playing"
    TRANSITION = "transition"
    VIDEO = "video"
    VICTORY_IMAGE = "victory_image"
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
    transition_at: int | None = None
    victory_image_until: int | None = None
    versus: VersusMatch | None = None

    def start_phase(self, number: int) -> None:
        self.phase_number = number
        self.phase = get_phase(number)
        self.board = self.phase.create_board()
        self.screen = ScreenState.PLAYING
        self.clear_selection()
        self.message = ""
        self.last_move = ""
        self.reset_at = None
        self.transition_at = None
        self.victory_image_until = None

    def show_phase_intro(self, number: int) -> None:
        self.phase_number = number
        self.phase = get_phase(number)
        self.board = self.phase.create_board()
        self.screen = ScreenState.PHASE_INTRO
        self.clear_selection()
        self.reset_at = None
        self.transition_at = None
        self.victory_image_until = None

    def return_to_menu(self) -> None:
        self.phase_number = 1
        self.phase = get_phase(1)
        self.board = self.phase.create_board()
        self.screen = ScreenState.MENU
        self.clear_selection()
        self.message = ""
        self.reset_at = None
        self.transition_at = None
        self.victory_image_until = None

    def show_about(self) -> None:
        self.screen = ScreenState.ABOUT
        self.clear_selection()

    def show_versus_menu(self) -> None:
        self.screen = ScreenState.VERSUS_MENU
        self.versus = None
        self.clear_selection()

    def show_difficulty(self) -> None:
        self.screen = ScreenState.DIFFICULTY

    def start_versus(self, mode: str, difficulty: int = 1) -> None:
        import random

        color = random.choice(("branca", "preta"))
        if mode == "machine":
            self.versus = VersusMatch("machine", difficulty=difficulty, human_color=color)
            self.versus.message = f"Sorteio: você joga com as {color}s. Vez das brancas."
        else:
            self.versus = VersusMatch("person", player_one_color=color)
            other = "preta" if color == "branca" else "branca"
            self.versus.message = f"Sorteio: jogador 1 = {color}s; jogador 2 = {other}s."
        self.screen = ScreenState.VERSUS_PLAYING

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
            self.transition_at = now_ms + WIN_TRANSITION_MS
        else:
            self.message = "Movimento incorreto para vencer"
            self.reset_at = now_ms + WRONG_MOVE_RESET_MS
        return won

    def update(self, now_ms: int) -> None:
        if self.reset_at is not None and now_ms >= self.reset_at:
            self.start_phase(self.phase_number)

    def transition_ready(self, now_ms: int) -> bool:
        return (
            self.screen == ScreenState.TRANSITION
            and self.transition_at is not None
            and now_ms >= self.transition_at
        )

    def consume_transition(self) -> None:
        self.transition_at = None

    def show_victory_image(self, now_ms: int) -> None:
        self.screen = ScreenState.VICTORY_IMAGE
        self.victory_image_until = now_ms + self.phase.victory_image_ms

    def victory_image_ready(self, now_ms: int) -> bool:
        return (
            self.screen == ScreenState.VICTORY_IMAGE
            and self.victory_image_until is not None
            and now_ms >= self.victory_image_until
        )

    def finish_video_sequence(self) -> None:
        """Avança a campanha após os vídeos, preservando o fluxo original."""
        if self.phase_number >= max(PHASES):
            self.screen = ScreenState.FINISHED
        else:
            self.start_phase(self.phase_number + 1)


def notation(square: Square) -> str:
    return f"{chr(ord('a') + square[1])}{8 - square[0]}"
