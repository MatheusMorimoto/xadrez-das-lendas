"""Telas e componentes de interface que não desenham o tabuleiro."""

from __future__ import annotations

from typing import Any

from .ui_actions import UIAction
from .ui_components import GOLD, WHITE, InterfaceComponents

NAVY = (0, 0, 50)
ABOUT_TEXT = (
    "Xadrez das Lendas é uma experiência educativa que une os desafios do xadrez à riqueza do "
    "folclore brasileiro. Ao analisar cada jogada, o jogador exercita a concentração, o raciocínio "
    "lógico, o planejamento, a tomada de decisões e a resolução de problemas.\n"
    "Durante as fases, personagens e narrativas lendárias despertam a curiosidade e ampliam o "
    "conhecimento sobre a cultura brasileira. Idealizado pelos alunos da UniSENAI Matheus Morimoto, "
    "Ademar Pedro e João Victtor, o projeto promove uma aprendizagem lúdica e significativa para crianças, "
    "jovens e adultos."
)


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
        self._actions[UIAction.SHOW_VERSUS] = self.components.menu_button(
            (0.19, 0.375, 0.61, 0.066),
            glow=(120, 220, 255),
        )
        self._actions[UIAction.SHOW_ABOUT] = self.components.menu_button(
            (0.19, 0.445, 0.61, 0.066),
            glow=(255, 215, 90),
        )
        self._actions[UIAction.QUIT] = self.components.menu_button(
            (0.19, 0.51, 0.61, 0.066),
            glow=(255, 95, 80),
        )

    def versus_menu(self, background: Any | None) -> None:
        self._selection_background(background)
        self.components.center_text("PARTIDA CONTRA", int(155 * self.scale), WHITE, 42, True)
        self.components.center_text("Escolha como deseja jogar", int(205 * self.scale), WHITE, 21)
        self._actions[UIAction.PLAY_MACHINE] = self.components.board_button(
            "JOGAR CONTRA A MÁQUINA", int(310 * self.scale)
        )
        self._actions[UIAction.PLAY_PERSON] = self.components.board_button(
            "JOGAR CONTRA OUTRA PESSOA", int(405 * self.scale)
        )
        self._actions[UIAction.RETURN_TO_MENU] = self.components.board_button(
            "VOLTAR AO MENU", int(555 * self.scale)
        )

    def difficulty(self, background: Any | None) -> None:
        self._selection_background(background)
        self.components.center_text("NÍVEL DA MÁQUINA", int(125 * self.scale), WHITE, 40, True)
        self.components.center_text("A dificuldade aumenta a capacidade de previsão", int(170 * self.scale), WHITE, 19)
        choices = (
            (UIAction.LEVEL_EASY, "FÁCIL", 260),
            (UIAction.LEVEL_MEDIUM, "MÉDIO", 350),
            (UIAction.LEVEL_HARD, "DIFÍCIL", 440),
        )
        for action, label, y in choices:
            self._actions[action] = self.components.board_button(label, int(y * self.scale))
        self._actions[UIAction.RETURN_TO_MENU] = self.components.board_button(
            "VOLTAR", int(575 * self.scale)
        )

    def _selection_background(self, background: Any | None) -> None:
        if background is not None:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill(NAVY)
        shade = self.pg.Surface((self.width, self.height), self.pg.SRCALPHA)
        shade.fill((0, 0, 0, 155))
        self.screen.blit(shade, (0, 0))

    def versus_hud(self, message: str, hints_left: int) -> None:
        hint_rect = self.pg.Rect(int(12 * self.scale), int(5 * self.scale), int(118 * self.scale), int(30 * self.scale))
        hovered = hint_rect.collidepoint(self.pg.mouse.get_pos())
        self.pg.draw.rect(self.screen, (70, 105, 40) if hovered else (45, 27, 12), hint_rect, border_radius=6)
        self.pg.draw.rect(self.screen, WHITE, hint_rect, 1, border_radius=6)
        font = self.pg.font.SysFont("Arial", max(12, int(15 * self.scale)), bold=True)
        label = font.render(f"DICA ({hints_left})", True, WHITE)
        self.screen.blit(label, label.get_rect(center=hint_rect.center))
        self._actions[UIAction.HINT] = hint_rect
        if message:
            self.components.center_text(message, self.height - max(15, int(13 * self.scale)), WHITE, 16, True)

    def about(self, background: Any | None, portraits: dict[str, Any]) -> None:
        if background is not None:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill(NAVY)
        shade = self.pg.Surface((self.width, self.height), self.pg.SRCALPHA)
        shade.fill((0, 0, 0, 148))
        self.screen.blit(shade, (0, 0))
        self.components.center_text("SOBRE O JOGO", int(62 * self.scale), WHITE, 38, True)

        text_rect = self.pg.Rect(
            int(58 * self.scale), int(105 * self.scale), self.width - int(116 * self.scale), int(230 * self.scale)
        )
        self.components.wrapped_text(ABOUT_TEXT, text_rect, WHITE, 19, line_spacing=1.2)
        self.components.center_text("IDEALIZADORES", int(374 * self.scale), WHITE, 24, True)

        names = ("Matheus Morimoto", "Ademar Pedro", "João Victtor")
        card_width = int(190 * self.scale)
        gap = int(14 * self.scale)
        start_x = (self.width - (card_width * 3 + gap * 2)) // 2
        image_size = int(122 * self.scale)
        for index, name in enumerate(names):
            card = self.pg.Rect(start_x + index * (card_width + gap), int(402 * self.scale), card_width, int(184 * self.scale))
            card_surface = self.pg.Surface((card.width, card.height), self.pg.SRCALPHA)
            card_surface.fill((0, 0, 0, 142))
            self.screen.blit(card_surface, card.topleft)
            self.pg.draw.rect(
                self.screen,
                WHITE,
                card,
                max(1, int(2 * self.scale)),
                border_radius=max(5, int(10 * self.scale)),
            )
            portrait = portraits.get(name)
            if portrait is not None:
                image_rect = portrait.get_rect(center=(card.centerx, card.top + int(70 * self.scale)))
                self.screen.blit(portrait, image_rect)
            else:
                self.pg.draw.rect(
                    self.screen,
                    (70, 70, 80),
                    self.pg.Rect(card.centerx - image_size // 2, card.top + int(9 * self.scale), image_size, image_size),
                )
            label = self.pg.Rect(card.left + 4, card.bottom - int(30 * self.scale), card.width - 8, int(22 * self.scale))
            self.components.wrapped_text(name, label, WHITE, 16, line_spacing=1.0)

        self._actions[UIAction.RETURN_TO_MENU] = self.components.board_button(
            "VOLTAR AO MENU", int(650 * self.scale)
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
