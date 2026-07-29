"""Ações de interface independentes dos nomes internos dos botões."""

from enum import Enum


class UIAction(str, Enum):
    START_CAMPAIGN = "start_campaign"
    QUIT = "quit"
    START_PHASE = "start_phase"
    RETURN_TO_MENU = "return_to_menu"
