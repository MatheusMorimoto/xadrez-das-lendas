"""Aplicação e loop principal do jogo."""

from __future__ import annotations

import logging
import math

from .history import HistoryStore, MatchRecord, leaderboard
from .renderer import Renderer
from .rules import legal_moves
from .state import GameState, ScreenState
from .ui_actions import UIAction
from .versus import VersusMatch, choose_machine_move
from .video import VideoPlayer

LOGGER = logging.getLogger(__name__)
FPS = 30
MACHINE_THINK_MS = 1600
HISTORY_PAGE_SIZE = 4
MOVES_PAGE_SIZE = 16


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
        self.history_store = HistoryStore()
        self.history_records = self.history_store.load()
        self.history_page = 0
        self.selected_record: MatchRecord | None = None
        self.moves_page = 0
        self.machine_move_at: int | None = None
        self.machine_thinking_since: int | None = None

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
                    self._after_video_playback(now)
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
                self._reset_machine_timer()
            elif action == UIAction.SHOW_PODIUM:
                self.history_records = self.history_store.load()
                self.history_page = 0
                self.state.screen = ScreenState.PODIUM
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
                self._reset_machine_timer()
            elif action == UIAction.RETURN_TO_MENU:
                self.state.show_versus_menu()
            return
        if self.state.screen == ScreenState.VERSUS_PLAYING:
            self._versus_click(position, action, now)
            return
        if self.state.screen == ScreenState.PODIUM:
            record_index = self.renderer.screens.history_index_at(position)
            if record_index is not None:
                absolute_index = self.history_page * HISTORY_PAGE_SIZE + record_index
                visible = list(reversed(self.history_records))
                if absolute_index < len(visible):
                    self.selected_record = visible[absolute_index]
                    self.moves_page = 0
                    self.state.screen = ScreenState.MATCH_RECORD
            elif action == UIAction.HISTORY_PREV:
                self.history_page = max(0, self.history_page - 1)
            elif action == UIAction.HISTORY_NEXT:
                self.history_page += 1
            elif action == UIAction.RETURN_TO_MENU:
                self.state.show_versus_menu()
            return
        if self.state.screen == ScreenState.MATCH_RECORD:
            if action == UIAction.MATCH_PREV:
                self.moves_page = max(0, self.moves_page - 1)
            elif action == UIAction.MATCH_NEXT:
                self.moves_page += 1
            elif action == UIAction.RETURN_TO_PODIUM:
                self.state.screen = ScreenState.PODIUM
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

    def _versus_click(self, position: tuple[int, int], action: UIAction | None, now: int) -> None:
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
            self._record_finished_match(match)
            if match.mode == "machine" and not match.finished and match.turn != match.human_color:
                self._start_machine_timer(now)
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
                if self.machine_move_at is None:
                    self._start_machine_timer(now)
                assert self.machine_move_at is not None
                assert self.machine_thinking_since is not None
                dots = "." * (1 + ((now - self.machine_thinking_since) // 400) % 3)
                match.message = f"Máquina pensando{dots}"
                if now >= self.machine_move_at:
                    origin, target = choose_machine_move(match.board, match.turn, match.difficulty)
                    match.play(origin, target)
                    self._reset_machine_timer()
                    self._record_finished_match(match)
            else:
                self._reset_machine_timer()
            return
        if self.state.transition_ready(now):
            self.state.consume_transition()
            if self.state.phase.victory_image and not self.state.phase.victory_image_after_videos:
                self.state.show_victory_image(now)
            elif self.video.start(self.state.phase.videos):
                self.state.screen = ScreenState.VIDEO
            elif self.state.phase.victory_image:
                self.state.show_victory_image(now)
            else:
                self._after_videos()
        elif self.state.victory_image_ready(now) or self.state.screen == ScreenState.VIDEO and not self.video.active:
            if self.state.screen == ScreenState.VIDEO:
                self._after_video_playback(now)
            else:
                self._after_videos()

    def _after_video_playback(self, now: int) -> None:
        if self.state.phase.victory_image and self.state.phase.victory_image_after_videos:
            self.state.show_victory_image(now)
        else:
            self._after_videos()

    def _after_videos(self) -> None:
        # O vídeo desaparece e o próximo tabuleiro é mostrado no mesmo frame.
        self.state.finish_video_sequence()

    def _start_machine_timer(self, now: int) -> None:
        self.machine_thinking_since = now
        self.machine_move_at = now + MACHINE_THINK_MS

    def _reset_machine_timer(self) -> None:
        self.machine_thinking_since = None
        self.machine_move_at = None

    def _record_finished_match(self, match: VersusMatch) -> None:
        if not getattr(match, "finished", False) or getattr(match, "recorded", False):
            return
        white_player = match.player_for_color("branca")
        black_player = match.player_for_color("preta")
        record = MatchRecord.create(white_player, black_player, match.message, match.winner, match.move_history)
        try:
            self.history_store.append(record)
        except OSError as exc:
            LOGGER.error("Nao foi possivel salvar o historico: %s", exc)
        self.history_records.append(record)
        match.recorded = True

    def _draw(self) -> None:
        if self.state.screen == ScreenState.PODIUM:
            visible = list(reversed(self.history_records))
            pages = max(1, math.ceil(len(visible) / HISTORY_PAGE_SIZE))
            self.history_page = min(self.history_page, pages - 1)
            start = self.history_page * HISTORY_PAGE_SIZE
            records = visible[start : start + HISTORY_PAGE_SIZE]
            self.renderer.draw_podium(leaderboard(self.history_records), records, self.history_page, pages)
        elif self.state.screen == ScreenState.MATCH_RECORD and self.selected_record is not None:
            pages = max(1, math.ceil(len(self.selected_record.moves) / MOVES_PAGE_SIZE))
            self.moves_page = min(self.moves_page, pages - 1)
            self.renderer.draw_match_record(self.selected_record, self.moves_page, pages)
        elif self.state.screen == ScreenState.VICTORY_IMAGE and self.state.phase.victory_image:
            self.renderer.draw_victory_image(self.state.phase.victory_image)
        elif self.state.screen == ScreenState.VIDEO:
            surface = self.video.next_surface(self.screen.get_size())
            if surface is not None:
                self.screen.blit(surface, (0, 0))
            else:
                self._after_video_playback(self.pg.time.get_ticks())
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
