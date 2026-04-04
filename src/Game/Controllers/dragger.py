from src.config import *
from src.Game.Pieces.piece import Piece


class Drag:
    def __init__(self, settings):
        self.mouse_position = ()
        self.dragged_piece: Piece = None
        self.original_row = 0
        self.original_column = 0
        self.DRAGGING_FLAG = False
        self.current_row = 0
        self.current_column = 0
        self.config = settings

    def draw_dragged_piece(self, screen):
        image = IMAGES128[self.dragged_piece.symbol()]
        image_center = self.mouse_position
        rect = image.get_rect(center=image_center)
        screen.blit(IMAGES128[self.dragged_piece.symbol()], rect)

    def drag_piece(self, dragged_piece):
        self.DRAGGING_FLAG = True
        self.dragged_piece = dragged_piece

    def undrag_piece(self):
        self.DRAGGING_FLAG = False
        self.dragged_piece = Piece

    def update_mouse_position(self, new_position):
        self.mouse_position = new_position
        self.current_row = self.mouse_position[1] // self.config.SQUARE_SIZE
        self.current_column = self.mouse_position[0] // self.config.SQUARE_SIZE

    def save_original_position(self):
        self.original_row = self.mouse_position[1] // self.config.SQUARE_SIZE
        self.original_column = self.mouse_position[0] // self.config.SQUARE_SIZE
