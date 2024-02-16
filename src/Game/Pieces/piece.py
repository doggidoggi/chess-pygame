from src.config import *


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
