"""Regras de movimento necessárias aos puzzles."""

from __future__ import annotations

from .board import Board
from .piece import Color, Piece, Square

SLIDING_DIRECTIONS = {
    "torre": ((1, 0), (-1, 0), (0, 1), (0, -1)),
    "bispo": ((1, 1), (-1, -1), (1, -1), (-1, 1)),
    "rainha": (
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (-1, -1),
        (1, -1),
        (-1, 1),
    ),
}
KING_OFFSETS = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))
KNIGHT_OFFSETS = ((2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1))


def opponent(color: Color) -> Color:
    return "preta" if color == "branca" else "branca"


def _inside(square: Square) -> bool:
    return 0 <= square[0] < 8 and 0 <= square[1] < 8


def attacked_squares(piece: Piece, board: Board) -> list[Square]:
    """Casas atacadas; peões atacam diagonais mesmo quando vazias."""
    if piece.tipo == "peao":
        direction = -1 if piece.cor == "branca" else 1
        return [square for dc in (-1, 1) if _inside(square := (piece.row + direction, piece.col + dc))]
    if piece.tipo == "cavalo":
        return [square for dc, dr in KNIGHT_OFFSETS if _inside(square := (piece.row + dr, piece.col + dc))]
    if piece.tipo == "rei":
        return [square for dc, dr in KING_OFFSETS if _inside(square := (piece.row + dr, piece.col + dc))]
    attacks: list[Square] = []
    for dc, dr in SLIDING_DIRECTIONS[piece.tipo]:
        for distance in range(1, 8):
            square = piece.row + dr * distance, piece.col + dc * distance
            if not _inside(square):
                break
            attacks.append(square)
            if board.piece_at(square) is not None:
                break
    return attacks


def is_square_attacked(board: Board, square: Square, by_color: Color) -> bool:
    return any(square in attacked_squares(piece, board) for piece in board.pieces if piece.cor == by_color)


def is_in_check(board: Board, color: Color) -> bool:
    king = board.king(color)
    if king is None:
        raise ValueError(f"Rei {color} ausente")
    return is_square_attacked(board, king.square, opponent(color))


def pseudo_legal_moves(piece: Piece, board: Board) -> list[Square]:
    if piece.tipo == "peao":
        moves: list[Square] = []
        direction = -1 if piece.cor == "branca" else 1
        start_row = 6 if piece.cor == "branca" else 1
        one = piece.row + direction, piece.col
        if _inside(one) and board.piece_at(one) is None:
            moves.append(one)
            two = piece.row + 2 * direction, piece.col
            if piece.row == start_row and board.piece_at(two) is None:
                moves.append(two)
        for target in attacked_squares(piece, board):
            occupant = board.piece_at(target)
            if occupant is not None and occupant.cor != piece.cor and occupant.tipo != "rei":
                moves.append(target)
            elif target == board.en_passant:
                adjacent = board.piece_at((piece.row, target[1]))
                if adjacent is not None and adjacent.tipo == "peao" and adjacent.cor != piece.cor:
                    moves.append(target)
        return moves

    moves = []
    for target in attacked_squares(piece, board):
        occupant = board.piece_at(target)
        if occupant is None or occupant.cor != piece.cor and occupant.tipo != "rei":
            moves.append(target)
        if piece.tipo in SLIDING_DIRECTIONS and occupant is not None:
            continue
    if piece.tipo == "rei" and not piece.moved and not is_in_check(board, piece.cor):
        for rook_col, direction in ((0, -1), (7, 1)):
            rook = board.piece_at((piece.row, rook_col))
            if rook is None or rook.tipo != "torre" or rook.cor != piece.cor or rook.moved:
                continue
            between = range(rook_col + 1, piece.col) if direction < 0 else range(piece.col + 1, rook_col)
            if any(board.piece_at((piece.row, col)) is not None for col in between):
                continue
            transit = (piece.row, piece.col + direction)
            destination = (piece.row, piece.col + 2 * direction)
            if not is_square_attacked(board, transit, opponent(piece.cor)) and not is_square_attacked(
                board, destination, opponent(piece.cor)
            ):
                moves.append(destination)
    return moves


def legal_moves(piece: Piece, board: Board) -> list[Square]:
    moves: list[Square] = []
    for target in pseudo_legal_moves(piece, board):
        simulation = board.clone()
        simulation.move_unchecked(piece.square, target)
        if not is_in_check(simulation, piece.cor):
            moves.append(target)
    return moves


def has_legal_move(board: Board, color: Color) -> bool:
    return any(legal_moves(piece, board) for piece in board.pieces if piece.cor == color)


def is_checkmate(board: Board, color: Color) -> bool:
    return is_in_check(board, color) and not has_legal_move(board, color)


def is_stalemate(board: Board, color: Color) -> bool:
    return not is_in_check(board, color) and not has_legal_move(board, color)


def is_insufficient_material(board: Board) -> bool:
    """Detecta as combinações básicas em que o mate é impossível."""
    material = [piece for piece in board.pieces if piece.tipo != "rei"]
    if not material:
        return True
    if len(material) == 1 and material[0].tipo in ("bispo", "cavalo"):
        return True
    if material and all(piece.tipo == "bispo" for piece in material):
        square_colors = {(piece.row + piece.col) % 2 for piece in material}
        return len(square_colors) == 1
    return False


def apply_legal_move(board: Board, origin: Square, target: Square) -> Piece:
    piece = board.piece_at(origin)
    if piece is None:
        raise ValueError(f"Não existe peça em {origin}")
    if target not in legal_moves(piece, board):
        raise ValueError(f"Movimento ilegal: {origin} -> {target}")
    return board.move_unchecked(origin, target)
