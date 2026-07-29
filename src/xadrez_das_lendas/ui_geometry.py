"""Conversões entre coordenadas da janela e casas do tabuleiro."""

from __future__ import annotations

from .piece import Square

BOARD_DIMENSION = 8


def board_square(
    position: tuple[int, int],
    *,
    cell: int,
    margin: int,
    inverted: bool,
) -> Square | None:
    """Converte a posição do mouse para uma casa lógica do tabuleiro."""
    col = (position[0] - margin) // cell
    display_row = (position[1] - margin) // cell
    if not (0 <= col < BOARD_DIMENSION and 0 <= display_row < BOARD_DIMENSION):
        return None
    return (BOARD_DIMENSION - 1 - display_row if inverted else display_row), col
