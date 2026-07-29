"""Componentes visuais reutilizados pelas telas e pelo tabuleiro."""

from __future__ import annotations

from typing import Any

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
BUTTON = (50, 150, 50)
BUTTON_HOVER = (80, 180, 80)


class InterfaceComponents:
    def __init__(self, pygame: Any, screen: Any, scale: float) -> None:
        self.pg = pygame
        self.screen = screen
        self.scale = scale
        self.width, self.height = screen.get_size()

    def turn_indicator(self, turn: str, margin: int) -> None:
        size = max(18, int(24 * self.scale))
        x = self.width - margin + max(4, int(7 * self.scale))
        y = self.height - margin + max(4, int(7 * self.scale))
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

    def coordinates(self, inverted: bool, *, cell: int, margin: int, font: Any) -> None:
        for col in range(8):
            text = font.render(chr(ord("A") + col), True, BLACK)
            x = col * cell + margin + (cell - text.get_width()) // 2
            self.screen.blit(text, (x, 4))
            self.screen.blit(text, (x, self.height - margin + 4))
        for display_row in range(8):
            number = str(display_row + 1 if inverted else 8 - display_row)
            text = font.render(number, True, BLACK)
            y = display_row * cell + margin + (cell - text.get_height()) // 2
            self.screen.blit(text, (margin - int(28 * self.scale), y))
            self.screen.blit(text, (self.width - margin + int(8 * self.scale), y))

    def message_box(self, title: str, subtitle: str) -> None:
        overlay = self.pg.Surface((self.width, int(135 * self.scale)), self.pg.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        y = self.height // 2 - overlay.get_height() // 2
        self.screen.blit(overlay, (0, y))
        self.center_text(title, y + int(42 * self.scale), GOLD, 34, True)
        self.center_text(subtitle, y + int(92 * self.scale), WHITE, 21)

    def center_text(
        self,
        value: str,
        y: int,
        color: tuple[int, int, int],
        size: int,
        bold: bool = False,
    ) -> None:
        font = self.pg.font.SysFont("Arial", max(12, int(size * self.scale)), bold=bold)
        surface = font.render(value, True, color)
        self.screen.blit(surface, surface.get_rect(center=(self.width // 2, y)))

    def button(self, label: str, center_y: int) -> Any:
        width, height = int(330 * self.scale), int(64 * self.scale)
        rect = self.pg.Rect((self.width - width) // 2, center_y - height // 2, width, height)
        color = BUTTON_HOVER if rect.collidepoint(self.pg.mouse.get_pos()) else BUTTON
        self.pg.draw.rect(self.screen, color, rect, border_radius=max(4, int(10 * self.scale)))
        self.center_text(label, center_y, WHITE, 27, True)
        return rect

    def menu_button(
        self,
        normalized_rect: tuple[float, float, float, float],
        *,
        glow: tuple[int, int, int],
    ) -> Any:
        """Desenha o hover sobre uma placa já presente na arte do menu."""
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
