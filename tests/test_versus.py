import random

from xadrez_das_lendas.board import Board
from xadrez_das_lendas.piece import Piece
from xadrez_das_lendas.rules import apply_legal_move, legal_moves
from xadrez_das_lendas.versus import VersusMatch, all_moves, choose_machine_move, standard_board


def piece(tipo, cor, row, col, moved=False):
    return Piece(tipo, cor, row, col, f"{tipo}.png", moved)


def test_standard_board_has_all_pieces_and_white_starts():
    board = standard_board()
    assert len(board.pieces) == 32
    assert len(all_moves(board, "branca")) == 20
    assert len(all_moves(board, "preta")) == 20


def test_castling_moves_the_rook_too():
    board = Board(
        [
            piece("rei", "branca", 7, 4),
            piece("torre", "branca", 7, 7),
            piece("rei", "preta", 0, 4),
        ]
    )
    assert (7, 6) in legal_moves(board.king("branca"), board)
    apply_legal_move(board, (7, 4), (7, 6))
    assert board.piece_at((7, 5)).tipo == "torre"


def test_en_passant_and_automatic_promotion():
    board = Board(
        [
            piece("rei", "branca", 7, 4),
            piece("rei", "preta", 0, 4),
            piece("peao", "branca", 3, 4),
            piece("peao", "preta", 1, 5),
        ]
    )
    apply_legal_move(board, (1, 5), (3, 5))
    assert (2, 5) in legal_moves(board.piece_at((3, 4)), board)
    apply_legal_move(board, (3, 4), (2, 5))
    assert board.piece_at((3, 5)) is None

    promoting = piece("peao", "branca", 1, 0)
    board.pieces.append(promoting)
    apply_legal_move(board, (1, 0), (0, 0))
    assert promoting.tipo == "rainha"


def test_machine_levels_always_choose_legal_moves_and_hints_are_limited():
    board = standard_board()
    for level in (1, 2, 3):
        assert choose_machine_move(board, "branca", level, random.Random(1)) in all_moves(board, "branca")

    match = VersusMatch("person")
    for _ in range(3):
        assert match.hint() is not None
    assert match.hint() is None
    assert match.hints_left == 0


def test_board_orientation_follows_the_active_local_player():
    machine = VersusMatch("machine", human_color="preta")
    assert machine.inverted
    machine.turn = "preta"
    assert machine.inverted

    person = VersusMatch("person")
    assert not person.inverted
    person.turn = "preta"
    assert person.inverted


def test_every_move_is_added_to_the_match_record():
    match = VersusMatch("machine", human_color="branca")

    match.play((6, 4), (4, 4))
    match.play((1, 4), (3, 4))

    assert match.move_history == [
        "1. Brancas: e2 -> e4",
        "1. Pretas: e7 -> e5",
    ]
    assert match.player_for_color("branca") == "Você"
    assert match.player_for_color("preta") == "Máquina"
