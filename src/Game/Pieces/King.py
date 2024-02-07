from src.Game.Models.piece import Piece
from src.constants import *


class King(Piece):
    def __init__(self, piece_color):
        super().__init__(piece_color, self.__class__.__name__)
