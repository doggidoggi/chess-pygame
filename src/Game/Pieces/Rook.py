from src.Game.Pieces.piece import Piece


class Rook(Piece):
    def __init__(self, piece_color):
        super().__init__(piece_color, self.__class__.__name__)
