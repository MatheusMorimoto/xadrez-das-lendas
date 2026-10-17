"""Renderização Pygame; nenhuma inicialização ocorre durante o import."""

from __future__ import annotations

import logging
from typing import Any

from .paths import asset_path
from .piece import Piece, Square
from .state import GameState, ScreenState
from .ui_actions import UIAction
from .ui_components import BLACK
from .ui_geometry import board_square
from .ui_screens import ScreenPainter

LOGGER = logging.getLogger(__name__)

GREEN = (0, 150, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
WOOD = (101, 67, 33)


class Renderer:
    def __init__(self, pygame: Any, screen: Any, scale: float) -> None:
        self.pg = pygame
        self.screen = screen
        self.scale = scale
        self.cell = int(80 * scale)
        self.margin = int(40 * scale)
        self.width, self.height = screen.get_size()
        self.font = pygame.font.SysFont("Arial", int(24 * scale))
        self.images: dict[tuple[str, int], Any] = {}
        self.menu_background = self._load_background()
        self.about_background = self._load_about_background()
        self.creator_portraits = self._load_creator_portraits()
        self.screens = ScreenPainter(pygame, screen, scale)

    def _load_background(self) -> Any | None:
        try:
            image = self.pg.image.load(str(asset_path("tela_inicio.png"))).convert()
            return self.pg.transform.scale(image, (self.width, self.height))
        except (FileNotFoundError, self.pg.error) as exc:
            LOGGER.error("Falha ao carregar fundo do menu: %s", exc)
            return None

    def _piece_image(self, piece: Piece) -> Any:
        key = piece.asset_name, self.cell
        if key in self.images:
            return self.images[key]
        try:
            image = self.pg.image.load(str(asset_path(piece.asset_name))).convert_alpha()
            image.set_colorkey(BLACK)
            image = self.pg.transform.smoothscale(image, (self.cell, self.cell))
        except (FileNotFoundError, self.pg.error) as exc:
            LOGGER.error("Falha ao carregar %s: %s", piece.asset_name, exc)
            image = self.pg.Surface((self.cell, self.cell))
            image.fill((255, 0, 255))
        self.images[key] = image
        return image

    def _load_about_background(self) -> Any | None:
        try:
            image = self.pg.image.load(str(asset_path("tabuleiro.png"))).convert()
            return self.pg.transform.smoothscale(image, (self.width, self.height))
        except (FileNotFoundError, self.pg.error) as exc:
            LOGGER.error("Falha ao carregar fundo da tela Sobre o Jogo: %s", exc)
            return None

    def _load_creator_portraits(self) -> dict[str, Any]:
        portraits = {
            "Matheus Morimoto": "Matheus_Morimoto.jpeg",
            "Ademar Pedro": "Ademar.jpeg",
            "João Victtor": "João_Victtor.jpeg",
        }
        size = int(122 * self.scale)
        loaded: dict[str, Any] = {}
        for name, filename in portraits.items():
            try:
                image = self.pg.image.load(str(asset_path(filename))).convert_alpha()
                source = image.get_rect()
                side = min(source.width, source.height)
                crop = self.pg.Rect((source.width - side) // 2, (source.height - side) // 2, side, side)
                loaded[name] = self.pg.transform.smoothscale(image.subsurface(crop), (size, size))
            except (FileNotFoundError, self.pg.error) as exc:
                LOGGER.error("Falha ao carregar foto de %s: %s", name, exc)
        return loaded

    def draw(self, state: GameState) -> None:
        self.screens.begin_frame()
        if state.screen == ScreenState.MENU:
            self.screens.menu(self.menu_background)
        elif state.screen == ScreenState.ABOUT:
            self.screens.about(self.about_background, self.creator_portraits)
        elif state.screen == ScreenState.VERSUS_MENU:
            self.screens.versus_menu(self.about_background)
        elif state.screen == ScreenState.DIFFICULTY:
            self.screens.difficulty(self.about_background)
        elif state.screen == ScreenState.VERSUS_PLAYING and state.versus is not None:
            self._versus_game(state.versus)
        elif state.screen == ScreenState.PHASE_INTRO:
            self.screens.phase_intro(state.phase_number)
        elif state.screen in (ScreenState.PLAYING, ScreenState.TRANSITION):
            self._game(state)
            if state.screen == ScreenState.TRANSITION:
                self.screens.components.message_box(state.message, state.last_move)
        elif state.screen == ScreenState.FINISHED:
            self.screens.finished()

    def _game(self, state: GameState) -> None:
        self.screen.fill(WOOD)
        inverted = state.phase.inverted
        board_size = self.cell * 8
        self.pg.draw.rect(self.screen, BLACK, (self.margin - 2, self.margin - 2, board_size + 4, board_size + 4), 2)
        for row in range(8):
            for col in range(8):
                draw_row = 7 - row if inverted else row
                color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
                self.pg.draw.rect(
                    self.screen,
                    color,
                    (col * self.cell + self.margin, draw_row * self.cell + self.margin, self.cell, self.cell),
                )
        self.screens.components.coordinates(inverted, cell=self.cell, margin=self.margin, font=self.font)
        for row, col in state.valid_moves:
            draw_row = 7 - row if inverted else row
            self.pg.draw.circle(
                self.screen,
                GREEN,
                (col * self.cell + self.margin + self.cell // 2, draw_row * self.cell + self.margin + self.cell // 2),
                max(5, int(10 * self.scale)),
            )
        for piece in state.board.pieces:
            draw_row = 7 - piece.row if inverted else piece.row
            self.screen.blit(
                self._piece_image(piece),
                (piece.col * self.cell + self.margin, draw_row * self.cell + self.margin),
            )
        self.screens.components.turn_indicator(state.phase.turn, self.margin)
        if state.message and state.screen == ScreenState.PLAYING:
            self.screens.components.center_text(
                state.message,
                self.height - max(15, self.margin // 3),
                (180, 0, 0),
                16,
                True,
            )

    def _versus_game(self, match: Any) -> None:
        self.screen.fill(WOOD)
        board = match.board
        inverted = match.inverted
        board_size = self.cell * 8
        self.pg.draw.rect(self.screen, BLACK, (self.margin - 2, self.margin - 2, board_size + 4, board_size + 4), 2)
        for row in range(8):
            for col in range(8):
                draw_row = 7 - row if inverted else row
                draw_col = 7 - col if inverted else col
                color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
                self.pg.draw.rect(
                    self.screen,
                    color,
                    (draw_col * self.cell + self.margin, draw_row * self.cell + self.margin, self.cell, self.cell),
                )
        self.screens.components.coordinates(
            inverted,
            cell=self.cell,
            margin=self.margin,
            font=self.font,
            rotate_files=True,
        )
        for row, col in match.valid_moves:
            draw_row = 7 - row if inverted else row
            draw_col = 7 - col if inverted else col
            self.pg.draw.circle(
                self.screen,
                GREEN,
                (draw_col * self.cell + self.margin + self.cell // 2, draw_row * self.cell + self.margin + self.cell // 2),
                max(5, int(10 * self.scale)),
            )
        for piece in board.pieces:
            draw_row = 7 - piece.row if inverted else piece.row
            draw_col = 7 - piece.col if inverted else piece.col
            self.screen.blit(self._piece_image(piece), (draw_col * self.cell + self.margin, draw_row * self.cell + self.margin))
        self.screens.components.turn_indicator(match.turn, self.margin)
        self.screens.versus_hud(match.message, match.hints_left)

    def versus_square(self, position: tuple[int, int], inverted: bool) -> Square | None:
        square = board_square(position, cell=self.cell, margin=self.margin, inverted=inverted)
        if square is None or not inverted:
            return square
        return square[0], 7 - square[1]

    def board_square(self, position: tuple[int, int], inverted: bool) -> Square | None:
        return board_square(position, cell=self.cell, margin=self.margin, inverted=inverted)

    def action_at(self, position: tuple[int, int]) -> UIAction | None:
        return self.screens.action_at(position)
