"""Telas e componentes de interface que não desenham o tabuleiro."""

from __future__ import annotations

from typing import Any

from .ui_actions import UIAction
from .ui_components import GOLD, InterfaceComponents

NAVY = (0, 0, 50)


class ScreenPainter:
    """Desenha telas estáticas e mantém suas regiões clicáveis encapsuladas."""

    def __init__(self, pygame: Any, screen: Any, scale: float) -> None:
        self.pg = pygame
        self.screen = screen
        self.scale = scale
        self.width, self.height = screen.get_size()
        self._actions: dict[UIAction, Any] = {}
        self.components = InterfaceComponents(pygame, screen, scale)

    def begin_frame(self) -> None:
        self._actions.clear()

    def action_at(self, position: tuple[int, int]) -> UIAction | None:
        return next((action for action, rect in self._actions.items() if rect.collidepoint(position)), None)

    def menu(self, background: Any | None) -> None:
        if background is not None:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill(NAVY)
            self.components.center_text("XADREZ DAS LENDAS", self.height // 3, GOLD, 54, True)
        self._actions[UIAction.START_CAMPAIGN] = self.components.menu_button(
            (0.19, 0.305, 0.61, 0.066),
            glow=(205, 255, 90),
        )
        self._actions[UIAction.QUIT] = self.components.menu_button(
            (0.19, 0.51, 0.61, 0.066),
            glow=(255, 95, 80),
        )

    def phase_intro(self, phase_number: int) -> None:
        self.screen.fill(NAVY)
        self.components.center_text(f"FASE {phase_number - 1} CONCLUÍDA!", self.height // 3, GOLD, 48, True)
        self._actions[UIAction.START_PHASE] = self.components.button(
            f"INICIAR FASE {phase_number}",
            self.height // 2,
        )

    def finished(self) -> None:
        self.screen.fill(NAVY)
        self.components.center_text("CAMPANHA FINALIZADA!", self.height // 3, GOLD, 54, True)
        self.components.center_text(
            "VITÓRIA TOTAL!",
            self.height // 3 + int(70 * self.scale),
            (255, 127, 127),
            42,
            True,
        )
        self._actions[UIAction.RETURN_TO_MENU] = self.components.button(
            "VOLTAR AO MENU",
            self.height // 2 + int(100 * self.scale),
        )
