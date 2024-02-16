from src.Game.Pieces.King import King
from src.Game.Pieces.Pawn import Pawn
from src.config import *


class Move:
    def __init__(self, startPosition: tuple, endPosition: tuple, board):
        self.movedPiece = board.board[startPosition[0]][startPosition[1]]
        self.startRow = startPosition[0]
        self.startColumn = startPosition[1]
        self.endRow = endPosition[0]
        self.endColumn = endPosition[1]
        self.board = board
        self.capturedPiece = board.board[endPosition[0]][endPosition[1]]
        self.is_en_passant_move = (self.endRow, self.endColumn) == self.board.possible_en_passant
        self.is_castle_move = isinstance(self.movedPiece, King) and abs(self.endColumn - self.startColumn) == 2
        self.is_promotion_move = (isinstance(self.movedPiece, Pawn) and self.endRow == 0 or self.endRow == 7 and
                                  isinstance(self.movedPiece, Pawn))
        if self.is_en_passant_move:
            self.capturedPiece = Pawn(BLACK) if self.movedPiece.piece_color == WHITE else Pawn(WHITE)

    def __eq__(self, other):
        if (self.startRow, self.startColumn, self.endColumn, self.endRow) == (
                other.startRow, other.startColumn, other.endColumn, other.endRow):
            return True
