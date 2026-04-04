from __future__ import annotations

from typing import Optional

import torch

from src.constants import BLACK, WHITE
from src.Game.Pieces.Bishop import Bishop
from src.Game.Pieces.King import King
from src.Game.Pieces.Knight import Knight
from src.Game.Pieces.Pawn import Pawn
from src.Game.Pieces.Queen import Queen
from src.Game.Pieces.Rook import Rook


class BoardEncoder:
    """
    Кодирует позицию в tensor [18, 8, 8].

    Каналы:
    0-5   : белые P/N/B/R/Q/K
    6-11  : черные P/N/B/R/Q/K
    12    : side to move (all ones if white to move)
    13-16 : права рокировки WK/WQ/BK/BQ
    17    : en passant square (если есть)
    """

    CHANNELS = 18

    def encode(self, board) -> torch.Tensor:
        planes = torch.zeros((self.CHANNELS, 8, 8), dtype=torch.float32)

        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece is None:
                    continue
                channel = self._piece_to_channel(piece)
                if channel is not None:
                    planes[channel, row, col] = 1.0

        if getattr(board, "whiteMove", False):
            planes[12, :, :] = 1.0

        wk, wq, bk, bq = self._infer_castling_rights(board)
        if wk:
            planes[13, :, :] = 1.0
        if wq:
            planes[14, :, :] = 1.0
        if bk:
            planes[15, :, :] = 1.0
        if bq:
            planes[16, :, :] = 1.0

        en_passant = self._extract_en_passant_square(board)
        if en_passant is not None:
            row, col = en_passant
            if 0 <= row < 8 and 0 <= col < 8:
                planes[17, row, col] = 1.0

        return planes

    @staticmethod
    def _piece_to_channel(piece) -> Optional[int]:
        white = getattr(piece, "piece_color", None) == WHITE
        base = 0 if white else 6

        if isinstance(piece, Pawn):
            return base + 0
        if isinstance(piece, Knight):
            return base + 1
        if isinstance(piece, Bishop):
            return base + 2
        if isinstance(piece, Rook):
            return base + 3
        if isinstance(piece, Queen):
            return base + 4
        if isinstance(piece, King):
            return base + 5
        return None

    @staticmethod
    def _extract_en_passant_square(board) -> Optional[tuple[int, int]]:
        candidates = (
            getattr(board, "enPassantPossible", None),
            getattr(board, "en_passant_possible", None),
            getattr(board, "en_passant_square", None),
            getattr(board, "enPassantSquare", None),
        )
        for candidate in candidates:
            if isinstance(candidate, tuple) and len(candidate) == 2:
                row, col = candidate
                if isinstance(row, int) and isinstance(col, int):
                    return row, col
        return None

    @staticmethod
    def _infer_castling_rights(board) -> tuple[bool, bool, bool, bool]:
        def unmoved_piece_at(row: int, col: int, piece_cls, color) -> bool:
            piece = board.board[row][col]
            return (
                isinstance(piece, piece_cls)
                and getattr(piece, "piece_color", None) == color
                and not getattr(piece, "moved", True)
            )

        white_king_ready = unmoved_piece_at(7, 4, King, WHITE)
        black_king_ready = unmoved_piece_at(0, 4, King, BLACK)

        white_king_side = white_king_ready and unmoved_piece_at(7, 7, Rook, WHITE)
        white_queen_side = white_king_ready and unmoved_piece_at(7, 0, Rook, WHITE)
        black_king_side = black_king_ready and unmoved_piece_at(0, 7, Rook, BLACK)
        black_queen_side = black_king_ready and unmoved_piece_at(0, 0, Rook, BLACK)

        return white_king_side, white_queen_side, black_king_side, black_queen_side
