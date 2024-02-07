import src.constants
from src.Game.Board.chessboard import *
from src.Game.Controllers.dragger import Drag


class Menu:
    def __init__(self, window):
        self.GameScreen = window
        self.GameScreen.fill(color=pygame.Color(184, 139, 74))

        self.settings = src.constants
        self.in_menu = True

    def main_loop(self):
        while self.in_menu:
            for event in pygame.event.get():
                pass

    def play_sound(self, move, is_error_action=False):
        if is_error_action:
            self.settings.error_action_sound.play_sound()
        elif self.ChessBoard.is_variant_checkmate():
            self.settings.game_end_sound.play_sound()
        elif self.ChessBoard.is_variant_stalemate():
            self.settings.game_draw_sound.play_sound()
        elif self.ChessBoard.is_variant_check():
            self.settings.check_sound.play_sound()
        elif move.capturedPiece is not None:
            self.settings.move_capture_sound.play_sound()
        else:
            self.settings.move_sound.play_sound()


