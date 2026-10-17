"""Representação e validação estrutural do tabuleiro."""

from __future__ import annotations

from dataclasses import dataclass, field

from .piece import Color, Piece, Square


@dataclass
class Board:
    pieces: list[Piece] = field(default_factory=list)
    en_passant: Square | None = None

    def piece_at(self, square: Square) -> Piece | None:
        return next((piece for piece in self.pieces if piece.square == square), None)

    def king(self, color: Color) -> Piece | None:
        return next(
            (piece for piece in self.pieces if piece.tipo == "rei" and piece.cor == color),
            None,
        )

    def clone(self) -> Board:
        return Board([piece.copy() for piece in self.pieces], self.en_passant)

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
        if piece.tipo == "peao" and captured is None and target == self.en_passant:
            captured = self.piece_at((origin[0], target[1]))
        if captured is not None:
            if captured.tipo == "rei":
                raise ValueError("O rei não pode ser capturado")
            self.pieces.remove(captured)
        if piece.tipo == "rei" and abs(target[1] - origin[1]) == 2:
            rook_origin = (origin[0], 7 if target[1] > origin[1] else 0)
            rook_target = (origin[0], 5 if target[1] > origin[1] else 3)
            rook = self.piece_at(rook_origin)
            if rook is not None:
                rook.row, rook.col = rook_target
                rook.moved = True
        self.en_passant = None
        if piece.tipo == "peao" and abs(target[0] - origin[0]) == 2:
            self.en_passant = ((origin[0] + target[0]) // 2, origin[1])
        piece.row, piece.col = target
        piece.moved = True
        if piece.tipo == "peao" and target[0] in (0, 7):
            from .asset_catalog import piece_asset

            piece.tipo = "rainha"
            piece.asset_name = piece_asset("rainha", piece.cor)
        return piece
