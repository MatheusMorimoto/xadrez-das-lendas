"""Ações de interface independentes dos nomes internos dos botões."""

from enum import Enum


class UIAction(str, Enum):
    START_CAMPAIGN = "start_campaign"
    SHOW_VERSUS = "show_versus"
    PLAY_MACHINE = "play_machine"
    PLAY_PERSON = "play_person"
    LEVEL_EASY = "level_easy"
    LEVEL_MEDIUM = "level_medium"
    LEVEL_HARD = "level_hard"
    HINT = "hint"
    SHOW_ABOUT = "show_about"
    QUIT = "quit"
    START_PHASE = "start_phase"
    RETURN_TO_MENU = "return_to_menu"
