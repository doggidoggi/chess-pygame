import src.constants
from src.Game.Board.chessboard import *
from src.Game.Controllers.dragger import Drag
from src.GUI.main_game_drawer import *


class Game:
    def __init__(self, window):
        self.ChessBoard = Board()
        self.ValidMoves = self.ChessBoard.getValidMoves()
        self.GameScreen = window
        self.mainloop = True
        self.ChessDragger = Drag()

        self.GameDrawer = MainGameDrawer(window=window, board=self.ChessBoard, valid_moves=self.ValidMoves,
                                     dragger=self.ChessDragger)

        self.ChessPygameClock = pygame.time.Clock()
        self.PlayerSelectedCell = ()
        self.PlayerClicksLog = []
        self.PIECE_MOVED_FLAG = False
        self.settings = src.constants
        self.last_move = None

    def main_loop(self):
        global clicked_row, clicked_column, clicked_piece
        clicked_row = None
        clicked_column = None
        clicked_piece = None
        while self.mainloop:  # цикл игры
            for event in pygame.event.get():

                if event.type == pygame.QUIT:  # выход из игры
                    self.mainloop = False

                if not self.ChessBoard.game_end:
                    # нажатие левой кнопки мыши
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # обновление позиции курсора мыши
                        self.ChessDragger.update_mouse_position(event.pos)
                        clicked_row = self.ChessDragger.mouse_position[1] // SQUARE_SIZE
                        clicked_column = self.ChessDragger.mouse_position[0] // SQUARE_SIZE
                        clicked_piece = self.ChessBoard.board[clicked_row][clicked_column]
                        if (clicked_piece and ((clicked_piece.piece_color == WHITE and self.ChessBoard.whiteMove)
                                               or (clicked_piece.piece_color == BLACK and not self.ChessBoard.whiteMove)) or
                                self.PlayerClicksLog):
                            if (clicked_piece and ((clicked_piece.piece_color == WHITE and self.ChessBoard.whiteMove)
                                                   or (
                                                           clicked_piece.piece_color == BLACK and
                                                           not self.ChessBoard.whiteMove))):
                                self.ChessDragger.save_original_position()
                                self.ChessDragger.drag_piece(clicked_piece)

                            if clicked_piece or self.PlayerClicksLog:

                                if (clicked_row, clicked_column) == self.PlayerSelectedCell:
                                    self.PlayerSelectedCell = ()
                                    self.PlayerClicksLog = []
                                else:
                                    self.PlayerSelectedCell = (clicked_row, clicked_column)
                                    self.PlayerClicksLog.append(self.PlayerSelectedCell)

                            # если кликов больше двух, то идет проверка на присутствие фигуры и правильность
                            # совершаемого хода
                            if len(self.PlayerClicksLog) == 2:
                                move = Move((self.PlayerClicksLog[0][0],
                                             self.PlayerClicksLog[0][1]),
                                            (self.PlayerSelectedCell[0],
                                             self.PlayerSelectedCell[1]),
                                            self.ChessBoard)
                                if self.ChessBoard.board[self.PlayerClicksLog[0][0]][self.PlayerClicksLog[0][1]]:
                                    if move in self.ValidMoves:
                                        # совершить ход
                                        self.ChessBoard.make_move(move)
                                        self.PIECE_MOVED_FLAG = True
                                        self.last_move = move
                                        self.PlayerClicksLog = []
                                        self.PlayerSelectedCell = ()
                                    else:
                                        self.play_sound(move=move, is_error_action=True)
                                        self.PlayerSelectedCell = ()
                                        self.PlayerClicksLog = []
                                else:
                                    self.PlayerSelectedCell = ()
                                    self.PlayerClicksLog = []

                    elif event.type == pygame.MOUSEMOTION:
                        if (clicked_piece and ((clicked_piece.piece_color == WHITE and self.ChessBoard.whiteMove)
                                               or (clicked_piece.piece_color == BLACK and not self.ChessBoard.whiteMove)) or
                                self.PlayerClicksLog):
                            if self.ChessDragger.DRAGGING_FLAG:
                                self.ChessDragger.update_mouse_position(new_position=event.pos)
                                self.PlayerSelectedCell = (clicked_row, clicked_column)

                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        if (clicked_piece and ((clicked_piece.piece_color == WHITE and self.ChessBoard.whiteMove)
                                               or (clicked_piece.piece_color == BLACK and not self.ChessBoard.whiteMove)) or
                                self.PlayerClicksLog):
                            if self.ChessDragger.DRAGGING_FLAG:
                                released_row = self.ChessDragger.mouse_position[1] // SQUARE_SIZE
                                released_col = self.ChessDragger.mouse_position[0] // SQUARE_SIZE
                                move = Move((self.ChessDragger.original_row, self.ChessDragger.original_column),
                                            (released_row, released_col), self.ChessBoard)
                                if move in self.ValidMoves:
                                    self.ChessBoard.make_move(move)
                                    self.last_move = move
                                    self.PIECE_MOVED_FLAG = True
                                else:
                                    if ((self.ChessDragger.original_row, self.ChessDragger.original_column) !=
                                            (released_row, released_col)):
                                        self.play_sound(move=move, is_error_action=True)
                                self.ChessDragger.undrag_piece()

                    elif (event.type == pygame.KEYDOWN and event.key == pygame.K_z and
                          pygame.key.get_mods() & pygame.KMOD_LCTRL):
                        self.ChessBoard.undoMove()
                        self.ValidMoves = self.ChessBoard.getValidMoves()
                        self.GameDrawer.update_valid_moves(self.ValidMoves)

            self.draw_game(self.GameScreen, self.PlayerSelectedCell)
            if self.ChessDragger.DRAGGING_FLAG:
                self.GameDrawer.draw_squares(self.GameScreen, (self.ChessDragger.current_row, self.ChessDragger.current_column))
                self.ChessDragger.draw_dragged_piece(self.GameScreen)
            self.ChessPygameClock.tick(FPS)
            pygame.display.flip()

            if self.PIECE_MOVED_FLAG:
                self.play_sound(self.last_move)
                self.ValidMoves = self.ChessBoard.getValidMoves()
                self.GameDrawer.update_valid_moves(self.ValidMoves)
                self.PIECE_MOVED_FLAG = not self.PIECE_MOVED_FLAG
        pygame.quit()

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

    def draw_game(self, screen, selectedCell):
        self.GameDrawer.draw_board(screen)
        self.GameDrawer.draw_squares_valid_moves(screen, selectedCell)
        self.GameDrawer.draw_checked_king()
        self.GameDrawer.draw_pieces(screen)

