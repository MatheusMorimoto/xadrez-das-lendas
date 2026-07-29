"""Catálogo de posições e objetivos das três fases originais."""

from __future__ import annotations

from .phase_models import P, Phase

PHASES: dict[int, Phase] = {
    1: Phase(
        1,
        "branca",
        False,
        (
            P(1, 4, "rainha", "branca"),
            P(2, 3, "rei", "branca"),
            P(3, 6, "cavalo", "branca", 2),
            P(0, 7, "rei", "preta"),
        ),
        videos=("YARA.mp4",),
    ),
    2: Phase(
        2,
        "preta",
        True,
        (
            P(7, 7, "rei", "branca"),
            P(6, 2, "rainha", "branca"),
            P(7, 6, "torre", "branca", 2),
            P(5, 3, "bispo", "branca"),
            P(5, 2, "cavalo", "branca", 2),
            P(6, 3, "cavalo", "branca", 2),
            P(6, 0, "peao", "branca", 1),
            P(6, 1, "peao", "branca", 2),
            P(4, 3, "peao", "branca", 4),
            P(5, 5, "peao", "branca", 5),
            P(6, 6, "peao", "branca", 6),
            P(6, 7, "peao", "branca", 7),
            P(0, 6, "rei", "preta"),
            P(0, 0, "torre", "preta"),
            P(0, 5, "torre", "preta", 2),
            P(4, 5, "bispo", "preta"),
            P(1, 3, "cavalo", "preta"),
            P(5, 7, "cavalo", "preta", 2),
            P(1, 0, "peao", "preta", 1),
            P(1, 1, "peao", "preta", 2),
            P(2, 2, "peao", "preta", 3),
            P(3, 5, "peao", "preta", 4),
            P(1, 6, "peao", "preta", 5),
            P(1, 7, "peao", "preta", 6),
        ),
        videos=("cucacaldeirao.mp4",),
    ),
    3: Phase(
        3,
        "preta",
        True,
        (
            P(1, 3, "rei", "preta"),
            P(4, 5, "rainha", "preta"),
            P(4, 4, "cavalo", "preta"),
            P(1, 0, "peao", "preta", 1),
            P(1, 2, "peao", "preta", 2),
            P(1, 5, "peao", "preta", 3),
            P(1, 6, "peao", "preta", 4),
            P(1, 7, "peao", "preta", 5),
            P(4, 7, "rei", "branca"),
            P(0, 7, "rainha", "branca"),
            P(7, 7, "torre", "branca", 2),
            P(4, 0, "torre", "branca", 2),
            P(7, 5, "bispo", "branca"),
            P(5, 5, "cavalo", "branca", 2),
            P(6, 4, "peao", "branca", 1),
            P(6, 7, "peao", "branca", 2),
            P(4, 6, "peao", "branca", 4),
            P(5, 7, "peao", "branca", 5),
        ),
        objective="target",
        target_piece="rainha",
        target_square=(3, 6),
        videos=("cuca.mp4", "boitata.mp4"),
    ),
}


def get_phase(number: int) -> Phase:
    try:
        return PHASES[number]
    except KeyError as exc:
        raise ValueError(f"Fase inexistente: {number}") from exc
