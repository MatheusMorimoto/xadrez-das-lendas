"""Aplicação e loop principal do jogo."""

from __future__ import annotations

import logging

from .renderer import Renderer
from .rules import legal_moves
from .state import GameState, ScreenState
from .ui_actions import UIAction
from .versus import choose_machine_move
from .video import VideoPlayer

LOGGER = logging.getLogger(__name__)
FPS = 30


class Game:
    def __init__(self) -> None:
        import pygame

        self.pg = pygame
        pygame.init()
        info = pygame.display.Info()
        screen_height = info.current_h if info.current_h > 0 else 720
        self.scale = max(0.5, (screen_height * 0.85) / 720)
        cell, margin = int(80 * self.scale), int(40 * self.scale)
        size = cell * 8 + margin * 2
        self.screen = pygame.display.set_mode((size, size))
        pygame.display.set_caption("Xadrez das Lendas")
        self.renderer = Renderer(pygame, self.screen, self.scale)
        self.state = GameState()
        self.video = VideoPlayer()
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self) -> None:
        try:
            while self.running:
                now = self.pg.time.get_ticks()
                self._events(now)
                self.state.update(now)
                self._advance(now)
                self._draw()
                self.pg.display.flip()
                self.clock.tick(FPS)
        finally:
            self.video.stop()
            self.pg.quit()

    def _events(self, now: int) -> None:
        for event in self.pg.event.get():
            if event.type == self.pg.QUIT:
                self.running = False
            elif event.type == self.pg.KEYDOWN and event.key == self.pg.K_ESCAPE:
                if self.state.screen == ScreenState.VIDEO:
                    self.video.stop()
                    self._after_videos()
                elif self.state.screen == ScreenState.VICTORY_IMAGE:
                    self._after_videos()
                elif self.state.screen == ScreenState.MENU:
                    self.running = False
                else:
                    self.state.return_to_menu()
            elif event.type == self.pg.MOUSEBUTTONDOWN and event.button == 1:
                self._click(event.pos, now)

    def _click(self, position: tuple[int, int], now: int) -> None:
        action = self.renderer.action_at(position)
        if self.state.screen == ScreenState.MENU:
            if action == UIAction.START_CAMPAIGN:
                self.state.start_phase(1)
            elif action == UIAction.SHOW_VERSUS:
                self.state.show_versus_menu()
            elif action == UIAction.SHOW_ABOUT:
                self.state.show_about()
            elif action == UIAction.QUIT:
                self.running = False
            return
        if self.state.screen == ScreenState.VERSUS_MENU:
            if action == UIAction.PLAY_MACHINE:
                self.state.show_difficulty()
            elif action == UIAction.PLAY_PERSON:
                self.state.start_versus("person")
            elif action == UIAction.RETURN_TO_MENU:
                self.state.return_to_menu()
            return
        if self.state.screen == ScreenState.DIFFICULTY:
            levels = {
                UIAction.LEVEL_EASY: 1,
                UIAction.LEVEL_MEDIUM: 2,
                UIAction.LEVEL_HARD: 3,
            }
            if action in levels:
                self.state.start_versus("machine", levels[action])
            elif action == UIAction.RETURN_TO_MENU:
                self.state.show_versus_menu()
            return
        if self.state.screen == ScreenState.VERSUS_PLAYING:
            self._versus_click(position, action)
            return
        if self.state.screen == ScreenState.ABOUT:
            if action == UIAction.RETURN_TO_MENU:
                self.state.return_to_menu()
            return
        if self.state.screen == ScreenState.PHASE_INTRO:
            if action == UIAction.START_PHASE:
                self.state.start_phase(self.state.phase_number)
            return
        if self.state.screen == ScreenState.FINISHED:
            if action == UIAction.RETURN_TO_MENU:
                self.state.return_to_menu()
            return
        if self.state.screen != ScreenState.PLAYING or self.state.reset_at is not None:
            return
        square = self.renderer.board_square(position, self.state.phase.inverted)
        if square is None:
            self.state.clear_selection()
            return
        if self.state.selected is not None:
            if square in self.state.valid_moves:
                self.state.move(self.state.selected, square, now)
                return
            self.state.clear_selection()
        piece = self.state.board.piece_at(square)
        if piece is not None and piece.cor == self.state.phase.turn:
            self.state.selected = square
            self.state.valid_moves = legal_moves(piece, self.state.board)
        elif piece is not None:
            self.state.message = "Não é sua vez de mover esta peça."

    def _versus_click(self, position: tuple[int, int], action: UIAction | None) -> None:
        match = self.state.versus
        if match is None or match.finished:
            return
        if action == UIAction.HINT:
            match.hint()
            return
        if match.mode == "machine" and match.turn != match.human_color:
            return
        square = self.renderer.versus_square(position, match.inverted)
        if square is None:
            match.selected = None
            match.valid_moves = []
            return
        if match.selected is not None and square in match.valid_moves:
            match.play(match.selected, square)
            return
        match.selected = None
        match.valid_moves = []
        piece = match.board.piece_at(square)
        if piece is not None and piece.cor == match.turn:
            from .rules import legal_moves

            match.selected = square
            match.valid_moves = legal_moves(piece, match.board)
        elif piece is not None:
            match.message = "Escolha uma peça da cor da vez."

    def _advance(self, now: int) -> None:
        if self.state.screen == ScreenState.VERSUS_PLAYING and self.state.versus is not None:
            match = self.state.versus
            if match.mode == "machine" and not match.finished and match.turn != match.human_color:
                origin, target = choose_machine_move(match.board, match.turn, match.difficulty)
                match.play(origin, target)
            return
        if self.state.transition_ready(now):
            self.state.consume_transition()
            if self.state.phase.victory_image:
                self.state.show_victory_image(now)
            elif self.video.start(self.state.phase.videos):
                self.state.screen = ScreenState.VIDEO
            else:
                self._after_videos()
        elif self.state.victory_image_ready(now) or self.state.screen == ScreenState.VIDEO and not self.video.active:
            self._after_videos()

    def _after_videos(self) -> None:
        # O vídeo desaparece e o próximo tabuleiro é mostrado no mesmo frame.
        self.state.finish_video_sequence()

    def _draw(self) -> None:
        if self.state.screen == ScreenState.VICTORY_IMAGE and self.state.phase.victory_image:
            self.renderer.draw_victory_image(self.state.phase.victory_image)
        elif self.state.screen == ScreenState.VIDEO:
            surface = self.video.next_surface(self.screen.get_size())
            if surface is not None:
                self.screen.blit(surface, (0, 0))
            else:
                self._after_videos()
                self.renderer.draw(self.state)
        else:
            self.renderer.draw(self.state)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        Game().run()
    except ImportError as exc:
        LOGGER.error("Dependência ausente: %s. Execute: python -m pip install -r requirements.txt", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
