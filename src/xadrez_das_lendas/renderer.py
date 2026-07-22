"""Renderização Pygame; nenhuma inicialização ocorre durante o import."""

from __future__ import annotations

import logging
from typing import Any

from .paths import asset_path
from .piece import Piece, Square
from .state import GameState, ScreenState

LOGGER = logging.getLogger(__name__)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
GREEN = (0, 150, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
NAVY = (0, 0, 50)
WOOD = (101, 67, 33)
BUTTON = (50, 150, 50)
BUTTON_HOVER = (80, 180, 80)


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
        self.buttons: dict[str, Any] = {}
        self.menu_background = self._load_background()

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

    def draw(self, state: GameState) -> None:
        self.buttons.clear()
        if state.screen == ScreenState.MENU:
            self._menu()
        elif state.screen == ScreenState.PHASE_INTRO:
            self._phase_intro(state)
        elif state.screen in (ScreenState.PLAYING, ScreenState.TRANSITION):
            self._game(state)
            if state.screen == ScreenState.TRANSITION:
                self._message_box(state.message, state.last_move)
        elif state.screen == ScreenState.FINISHED:
            self._finished()

    def _menu(self) -> None:
        if self.menu_background is not None:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self.screen.fill(NAVY)
            self._center_text("XADREZ DAS LENDAS", self.height // 3, GOLD, 54, True)
        self.buttons["start"] = self._menu_button(
            (0.19, 0.305, 0.61, 0.066),
            glow=(205, 255, 90),
        )
        self.buttons["quit"] = self._menu_button(
            (0.19, 0.51, 0.61, 0.066),
            glow=(255, 95, 80),
        )

    def _phase_intro(self, state: GameState) -> None:
        self.screen.fill(NAVY)
        self._center_text(f"FASE {state.phase_number - 1} CONCLUÍDA!", self.height // 3, GOLD, 48, True)
        self.buttons["start_phase"] = self._button(f"INICIAR FASE {state.phase_number}", self.height // 2)

    def _finished(self) -> None:
        self.screen.fill(NAVY)
        self._center_text("CAMPANHA FINALIZADA!", self.height // 3, GOLD, 54, True)
        self._center_text("VITÓRIA TOTAL!", self.height // 3 + int(70 * self.scale), (255, 127, 127), 42, True)
        self.buttons["menu"] = self._button("VOLTAR AO MENU", self.height // 2 + int(100 * self.scale))

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
        self._coordinates(inverted)
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
                self._piece_image(piece), (piece.col * self.cell + self.margin, draw_row * self.cell + self.margin)
            )
        self._turn_indicator(state.phase.turn)
        if state.message and state.screen == ScreenState.PLAYING:
            self._center_text(state.message, self.height - max(15, self.margin // 3), (180, 0, 0), 16, True)

    def _turn_indicator(self, turn: str) -> None:
        """Indicador compacto no canto inferior direito, sem texto de turno."""
        size = max(18, int(24 * self.scale))
        x = self.width - self.margin + max(4, int(7 * self.scale))
        y = self.height - self.margin + max(4, int(7 * self.scale))
        square_color = WHITE if turn == "branca" else BLACK
        arrow_color = BLACK if turn == "branca" else WHITE
        rect = self.pg.Rect(x, y, size, size)
        self.pg.draw.rect(self.screen, square_color, rect, border_radius=max(2, int(3 * self.scale)))
        self.pg.draw.rect(self.screen, BLACK if turn == "branca" else WHITE, rect, max(1, int(self.scale)))

        center_x = rect.centerx
        tip_y = rect.top + max(3, int(4 * self.scale))
        base_y = rect.bottom - max(3, int(4 * self.scale))
        line_width = max(2, int(3 * self.scale))
        self.pg.draw.line(self.screen, arrow_color, (center_x, base_y), (center_x, tip_y), line_width)
        head = max(4, int(6 * self.scale))
        self.pg.draw.polygon(
            self.screen,
            arrow_color,
            [(center_x, tip_y), (center_x - head, tip_y + head), (center_x + head, tip_y + head)],
        )

    def _coordinates(self, inverted: bool) -> None:
        for col in range(8):
            text = self.font.render(chr(ord("A") + col), True, BLACK)
            x = col * self.cell + self.margin + (self.cell - text.get_width()) // 2
            self.screen.blit(text, (x, 4))
            self.screen.blit(text, (x, self.height - self.margin + 4))
        for display_row in range(8):
            number = str(display_row + 1 if inverted else 8 - display_row)
            text = self.font.render(number, True, BLACK)
            y = display_row * self.cell + self.margin + (self.cell - text.get_height()) // 2
            self.screen.blit(text, (self.margin - int(28 * self.scale), y))
            self.screen.blit(text, (self.width - self.margin + int(8 * self.scale), y))

    def _message_box(self, title: str, subtitle: str) -> None:
        overlay = self.pg.Surface((self.width, int(135 * self.scale)), self.pg.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        y = self.height // 2 - overlay.get_height() // 2
        self.screen.blit(overlay, (0, y))
        self._center_text(title, y + int(42 * self.scale), GOLD, 34, True)
        self._center_text(subtitle, y + int(92 * self.scale), WHITE, 21)

    def _center_text(self, value: str, y: int, color: tuple[int, int, int], size: int, bold: bool = False) -> None:
        font = self.pg.font.SysFont("Arial", max(12, int(size * self.scale)), bold=bold)
        surface = font.render(value, True, color)
        self.screen.blit(surface, surface.get_rect(center=(self.width // 2, y)))

    def _button(self, label: str, center_y: int) -> Any:
        width, height = int(330 * self.scale), int(64 * self.scale)
        rect = self.pg.Rect((self.width - width) // 2, center_y - height // 2, width, height)
        color = BUTTON_HOVER if rect.collidepoint(self.pg.mouse.get_pos()) else BUTTON
        self.pg.draw.rect(self.screen, color, rect, border_radius=max(4, int(10 * self.scale)))
        self._center_text(label, center_y, WHITE, 27, True)
        return rect

    def _menu_button(
        self,
        normalized_rect: tuple[float, float, float, float],
        *,
        glow: tuple[int, int, int],
    ) -> Any:
        """Área clicável e hover sutil sobre uma placa já presente na arte."""
        x_ratio, y_ratio, width_ratio, height_ratio = normalized_rect
        rect = self.pg.Rect(
            int(self.width * x_ratio),
            int(self.height * y_ratio),
            int(self.width * width_ratio),
            int(self.height * height_ratio),
        )
        if not rect.collidepoint(self.pg.mouse.get_pos()):
            return rect

        arrow_depth = max(10, int(rect.height * 0.42))
        points = [
            (rect.left, rect.centery),
            (rect.left + arrow_depth, rect.top),
            (rect.right, rect.top),
            (rect.right, rect.bottom),
            (rect.left + arrow_depth, rect.bottom),
        ]
        overlay = self.pg.Surface((self.width, self.height), self.pg.SRCALPHA)
        self.pg.draw.polygon(overlay, (*glow, 28), points)
        for thickness, alpha in ((8, 30), (5, 55), (2, 210)):
            self.pg.draw.lines(overlay, (*glow, alpha), True, points, thickness)
        self.screen.blit(overlay, (0, 0))
        return rect

    def board_square(self, position: tuple[int, int], inverted: bool) -> Square | None:
        col = (position[0] - self.margin) // self.cell
        display_row = (position[1] - self.margin) // self.cell
        if not (0 <= col < 8 and 0 <= display_row < 8):
            return None
        return (7 - display_row if inverted else display_row), col
