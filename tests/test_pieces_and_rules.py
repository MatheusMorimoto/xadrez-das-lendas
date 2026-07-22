import pytest

from xadrez_das_lendas.board import Board
from xadrez_das_lendas.piece import Piece
from xadrez_das_lendas.rules import (
    apply_legal_move,
    is_checkmate,
    is_in_check,
    is_square_attacked,
    is_stalemate,
    legal_moves,
    pseudo_legal_moves,
)


def piece(tipo, cor, row, col):
    return Piece(tipo, cor, row, col, f"{tipo}.png")


@pytest.mark.parametrize(
    ("tipo", "origin", "expected"),
    [
        ("rei", (4, 4), {(3, 3), (3, 4), (3, 5), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)}),
        ("cavalo", (4, 4), {(2, 3), (2, 5), (3, 2), (3, 6), (5, 2), (5, 6), (6, 3), (6, 5)}),
        ("torre", (4, 4), {(row, 4) for row in range(8) if row != 4} | {(4, col) for col in range(8) if col != 4}),
        (
            "bispo",
            (4, 4),
            {(3, 3), (2, 2), (1, 1), (0, 0), (3, 5), (2, 6), (1, 7), (5, 3), (6, 2), (7, 1), (5, 5), (6, 6), (7, 7)},
        ),
    ],
)
def test_basic_piece_movements(tipo, origin, expected):
    moving = piece(tipo, "branca", *origin)
    board = Board([moving, piece("rei", "branca", 7, 0), piece("rei", "preta", 0, 7)])
    assert set(pseudo_legal_moves(moving, board)) == expected


def test_queen_combines_rook_and_bishop_moves():
    queen = piece("rainha", "branca", 4, 4)
    board = Board([queen, piece("rei", "branca", 7, 0), piece("rei", "preta", 0, 7)])
    assert len(pseudo_legal_moves(queen, board)) == 27


def test_sliding_piece_is_blocked_and_can_capture_enemy():
    rook = piece("torre", "branca", 4, 4)
    board = Board(
        [
            rook,
            piece("peao", "branca", 4, 2),
            piece("peao", "preta", 4, 6),
            piece("rei", "branca", 7, 0),
            piece("rei", "preta", 0, 7),
        ]
    )
    moves = pseudo_legal_moves(rook, board)
    assert (4, 3) in moves and (4, 2) not in moves and (4, 1) not in moves
    assert (4, 6) in moves and (4, 7) not in moves


def test_pawn_single_double_capture_and_attack():
    pawn = piece("peao", "branca", 6, 3)
    board = Board([pawn, piece("peao", "preta", 5, 4), piece("rei", "branca", 7, 0), piece("rei", "preta", 0, 7)])
    assert set(pseudo_legal_moves(pawn, board)) == {(5, 3), (4, 3), (5, 4)}
    assert is_square_attacked(board, (5, 2), "branca")


def test_piece_cannot_capture_same_color_or_a_king():
    rook = piece("torre", "branca", 4, 4)
    board = Board([rook, piece("peao", "branca", 4, 5), piece("rei", "branca", 7, 0), piece("rei", "preta", 4, 2)])
    assert (4, 5) not in pseudo_legal_moves(rook, board)
    assert (4, 2) not in pseudo_legal_moves(rook, board)
    with pytest.raises(ValueError, match="não pode ser capturado"):
        board.move_unchecked((4, 4), (4, 2))


def test_move_exposing_own_king_is_illegal():
    king = piece("rei", "branca", 7, 4)
    blocker = piece("torre", "branca", 6, 4)
    board = Board([king, blocker, piece("torre", "preta", 0, 4), piece("rei", "preta", 0, 0)])
    assert (6, 3) not in legal_moves(blocker, board)


def test_king_cannot_enter_attack_or_touch_other_king():
    white = piece("rei", "branca", 4, 4)
    board = Board([white, piece("rei", "preta", 2, 4), piece("torre", "preta", 4, 7)])
    assert (3, 4) not in legal_moves(white, board)
    assert (4, 5) not in legal_moves(white, board)


def test_check_checkmate_and_stalemate_are_distinct():
    mate = Board([piece("rei", "preta", 0, 7), piece("rainha", "branca", 1, 7), piece("rei", "branca", 2, 6)])
    assert is_in_check(mate, "preta")
    assert is_checkmate(mate, "preta")
    assert not is_stalemate(mate, "preta")
    stale = Board([piece("rei", "preta", 0, 7), piece("rainha", "branca", 2, 6), piece("rei", "branca", 1, 5)])
    assert not is_in_check(stale, "preta")
    assert is_stalemate(stale, "preta")


def test_apply_legal_capture():
    board = Board(
        [
            piece("rei", "branca", 7, 0),
            piece("rei", "preta", 0, 7),
            piece("torre", "branca", 4, 4),
            piece("cavalo", "preta", 4, 6),
        ]
    )
    moved = apply_legal_move(board, (4, 4), (4, 6))
    assert moved.square == (4, 6)
    assert len(board.pieces) == 3
