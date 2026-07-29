"""Reprodução interna e não bloqueante de sequências de vídeo."""

from __future__ import annotations

import logging
from collections import deque
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .paths import asset_path

LOGGER = logging.getLogger(__name__)


class VideoPlayer:
    def __init__(self, *, cv2_module: Any = None, pygame_module: Any = None) -> None:
        self._queue: deque[str] = deque()
        self._capture: Any = None
        self._cv2: Any = cv2_module
        self._pygame: Any = pygame_module
        self._frame_ended = False
        self._last_surface: Any = None

    @property
    def active(self) -> bool:
        return self._capture is not None or bool(self._queue)

    def start(self, names: Iterable[str]) -> bool:
        self.stop()
        self._queue.extend(names)
        if self._cv2 is None or self._pygame is None:
            try:
                import cv2
                import pygame
            except ImportError:
                LOGGER.warning("OpenCV ou Pygame indisponível; vídeos serão ignorados.")
                self._queue.clear()
                return False
            self._cv2 = cv2
            self._pygame = pygame
        return self._open_next()

    def _open_next(self) -> bool:
        self.release_current()
        while self._queue:
            name = self._queue.popleft()
            path = asset_path(name, required=False)
            if not path.is_file():
                LOGGER.error("Vídeo não encontrado: %s", path)
                continue
            capture = self._cv2.VideoCapture(str(path))
            if capture.isOpened():
                self._capture = capture
                self._frame_ended = False
                self._last_surface = None
                self._start_audio(path)
                return True
            capture.release()
            LOGGER.error("Não foi possível abrir o vídeo: %s", path)
        return False

    def next_surface(self, size: tuple[int, int]) -> Any | None:
        if self._capture is None:
            return None
        if self._frame_ended:
            if self._audio_busy():
                return self._last_surface
            return self.next_surface(size) if self._open_next() else None
        ok, frame = self._capture.read()
        if not ok:
            self._frame_ended = True
            if self._audio_busy():
                return self._last_surface
            return self.next_surface(size) if self._open_next() else None

        frame = self._cv2.resize(frame, size)
        frame = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2RGB)
        self._last_surface = self._pygame.image.frombuffer(frame.tobytes(), size, "RGB")
        return self._last_surface

    def _start_audio(self, video_path: Path) -> None:
        audio_path = asset_path(f"{video_path.stem}.ogg", required=False)
        if not audio_path.is_file():
            LOGGER.error("Trilha de áudio não encontrada: %s", audio_path)
            return
        try:
            if not self._pygame.mixer.get_init():
                self._pygame.mixer.init()
            self._pygame.mixer.music.load(str(audio_path))
            self._pygame.mixer.music.set_volume(1.0)
            self._pygame.mixer.music.play()
        except self._pygame.error as exc:
            LOGGER.error("Não foi possível reproduzir o áudio %s: %s", audio_path, exc)

    def _audio_busy(self) -> bool:
        return bool(self._pygame and self._pygame.mixer.get_init() and self._pygame.mixer.music.get_busy())

    def release_current(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        if self._pygame and self._pygame.mixer.get_init():
            self._pygame.mixer.music.stop()
            self._pygame.mixer.music.unload()
        self._frame_ended = False
        self._last_surface = None

    def stop(self) -> None:
        self.release_current()
        self._queue.clear()
