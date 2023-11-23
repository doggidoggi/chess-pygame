from config import *


class Piece:
    def __init__(self, piece_color, piece_type):
        self.piece_color = piece_color
        self.piece_type = piece_type
        self.moved = False

    def symbol(self) -> str:
        symbol = 'w' + self.piece_type if self.piece_color == WHITE else 'b' + self.piece_type
        return symbol

    def __str__(self):
        return self.symbol()


class Pawn(Piece):
    def __init__(self, piece_color):
        super().__init__(piece_color, self.__class__.__name__)
        self.direction = -1 if piece_color == WHITE else 1


class King(Piece):
    def __init__(self, piece_color):
        super().__init__(piece_color, self.__class__.__name__)


class Knight(Piece):
    def __init__(self, piece_color):
        super().__init__(piece_color, self.__class__.__name__)


class Bishop(Piece):
    def __init__(self, piece_color):
        super().__init__(piece_color, self.__class__.__name__)


class Rook(Piece):
    def __init__(self, piece_color):
        super().__init__(piece_color, self.__class__.__name__)


class Queen(Piece):
    def __init__(self, piece_color):
        super().__init__(piece_color, self.__class__.__name__)