"""Representação e validação estrutural do tabuleiro."""

from __future__ import annotations

from dataclasses import dataclass, field

from .piece import Color, Piece, Square


@dataclass
class Board:
    pieces: list[Piece] = field(default_factory=list)

    def piece_at(self, square: Square) -> Piece | None:
        return next((piece for piece in self.pieces if piece.square == square), None)

    def king(self, color: Color) -> Piece | None:
        return next(
            (piece for piece in self.pieces if piece.tipo == "rei" and piece.cor == color),
            None,
        )

    def clone(self) -> Board:
        return Board([piece.copy() for piece in self.pieces])

    def validate(self) -> list[str]:
        errors: list[str] = []
        occupied: set[Square] = set()
        for piece in self.pieces:
            if not (0 <= piece.row < 8 and 0 <= piece.col < 8):
                errors.append(f"{piece.tipo} {piece.cor} fora do tabuleiro: {piece.square}")
            if piece.square in occupied:
                errors.append(f"Duas peças ocupam {piece.square}")
            occupied.add(piece.square)
        for color in ("branca", "preta"):
            if sum(p.tipo == "rei" and p.cor == color for p in self.pieces) != 1:
                errors.append(f"A posição deve possuir exatamente um rei {color}")
        return errors

    def move_unchecked(self, origin: Square, target: Square) -> Piece:
        piece = self.piece_at(origin)
        if piece is None:
            raise ValueError(f"Não existe peça em {origin}")
        captured = self.piece_at(target)
        if captured is not None:
            if captured.tipo == "rei":
                raise ValueError("O rei não pode ser capturado")
            self.pieces.remove(captured)
        piece.row, piece.col = target
        return piece
