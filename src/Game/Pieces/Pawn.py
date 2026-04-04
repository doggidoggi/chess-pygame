from src.Game.Pieces.piece import Piece
from src.config import *


class Pawn(Piece):
    def __init__(self, piece_color):
        super().__init__(piece_color, self.__class__.__name__)
        self.direction = -1 if piece_color == WHITE else 1
