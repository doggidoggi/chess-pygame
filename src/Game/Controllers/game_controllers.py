import time

import pygame.event
from src.Game.Board.chessboard import *
from src.Game.Controllers.dragger import Drag
from src.GUI.classic_chess_drawer import *
from src.GUI.mini_chess_drawer import *
from src.constants import *


class Game:
    def __init__(self, window, settings):

        self.config = settings

        self.ChessBoard = None
        self.ValidMoves = None
        self.GameScreen = window
        self.mainloop = True
        self.ChessDragger = Drag(settings=self.config)

        self.GameDrawer = None

        self.ChessPygameClock = pygame.time.Clock()
        self.PlayerSelectedCell = ()
        self.PlayerClicksLog = []
        self.PIECE_MOVED_FLAG = False
        self.last_move = None

        self.selected_cell = None
        self.clicked_row = None
        self.clicked_row = None
        self.clicked_piece = None
        self.mouse_position = ()
        self.game_end = False

        self.nuclear_game_mode = False

        self.clock = pygame.time.Clock()

    def __check_for_game_end(self):
        if self.ChessBoard.is_variant_checkmate() or self.ChessBoard.is_variant_stalemate():
            self.game_end = True
            self.__play_sound(None, force_end=True)

    def __check_for_game_end_until_check(self):
        if self.ChessBoard.is_variant_check():
            self.game_end = True
            self.__play_sound(None, force_end=True)

    def __check_for_game_end_opposite(self):
        if self.ChessBoard.winner:
            self.game_end = True
            self.__play_sound(None, force_end=True)
            print(self.ChessBoard.winner)

    def __check_for_game_end_nuclear(self):
        if self.ChessBoard.game_end or self.ChessBoard.is_variant_checkmate():
            self.game_end = True
            self.__play_sound(None, force_end=True, is_nuclear=True)

    def __check_for_game_end_marseille(self):
        if self.ChessBoard.game_end:
            self.game_end = True
            self.__play_sound(None, force_end=True)

    def checkers(self):
        pass

    def chess_960(self):
        pygame.event.clear()
        self.config.change_square(8)
        self.ChessBoard = Chess960()
        self.ValidMoves = self.ChessBoard.getValidMoves()
        self.GameDrawer = ChessDrawer(window=self.GameScreen, board=self.ChessBoard, valid_moves=self.ValidMoves,
                                      dragger=self.ChessDragger, settings=self.config)
        self.__draw_game()
        pygame.display.flip()
        game_start_sound.play_sound()
        while self.mainloop:
            if not self.game_end:
                self.__check_for_game_end()
            self.__update_mouse_position()
            self.__handle_events()
        pygame.quit()

    def nuclear_chess(self):  # TODO-LIST: Написать отдельный класс для каждого режима игры
        pygame.event.clear()
        self.config.change_square(8)
        self.ChessBoard = NukeBoard()
        self.ValidMoves = self.ChessBoard.getValidMoves()
        self.GameDrawer = ChessDrawer(window=self.GameScreen, board=self.ChessBoard, valid_moves=self.ValidMoves,
                                      dragger=self.ChessDragger, settings=self.config)
        self.__draw_game()
        pygame.display.flip()
        game_start_sound.play_sound()
        self.nuclear_game_mode = True
        while self.mainloop:
            if not self.game_end:
                self.__check_for_game_end_nuclear()
            self.__update_mouse_position()
            self.__handle_events()
        pygame.quit()

    def until_the_first_check(self):
        pygame.event.clear()
        self.config.change_square(8)
        self.ChessBoard = UntilTheFirstCheck()
        self.ValidMoves = self.ChessBoard.getValidMoves()
        self.GameDrawer = ChessDrawer(window=self.GameScreen, board=self.ChessBoard, valid_moves=self.ValidMoves,
                                      dragger=self.ChessDragger, settings=self.config)
        self.__draw_game()
        pygame.display.flip()
        game_start_sound.play_sound()
        while self.mainloop:
            if not self.game_end:
                self.__check_for_game_end_until_check()
            self.__update_mouse_position()
            self.__handle_events()
        pygame.quit()

    def opposite_chess(self):
        pygame.event.clear()
        self.config.change_square(8)
        self.ChessBoard = OppositeChess()
        self.ValidMoves = self.ChessBoard.getValidMoves()
        self.GameDrawer = ChessDrawer(window=self.GameScreen, board=self.ChessBoard, valid_moves=self.ValidMoves,
                                      dragger=self.ChessDragger, settings=self.config)
        self.__draw_game()
        pygame.display.flip()
        game_start_sound.play_sound()
        while self.mainloop:
            if not self.game_end:
                self.__check_for_game_end_opposite()
            self.__update_mouse_position()
            self.__handle_events()
        pygame.quit()

    def marseille_chess(self):
        pygame.event.clear()
        self.config.change_square(8)
        self.ChessBoard = MarseilleChess()
        self.ValidMoves = self.ChessBoard.getValidMoves()
        self.GameDrawer = ChessDrawer(window=self.GameScreen, board=self.ChessBoard, valid_moves=self.ValidMoves,
                                      dragger=self.ChessDragger, settings=self.config)
        self.__draw_game()
        pygame.display.flip()
        game_start_sound.play_sound()
        while self.mainloop:
            if not self.game_end:
                self.__check_for_game_end_marseille()
            self.__update_mouse_position()
            self.__handle_events()
        pygame.quit()

    def mini_chess(self):
        pygame.event.clear()
        self.config.change_square(5)
        self.ChessBoard = MiniChess()
        self.ValidMoves = self.ChessBoard.getValidMoves()
        self.GameDrawer = MiniChessDrawer(window=self.GameScreen, board=self.ChessBoard, valid_moves=self.ValidMoves,
                                          dragger=self.ChessDragger, settings=self.config)
        self.__draw_game()
        pygame.display.flip()
        game_start_sound.play_sound()
        while self.mainloop:
            if not self.game_end:
                self.__check_for_game_end()
            self.__update_mouse_position()
            self.__handle_events()
        pygame.quit()

    def bird_chess(self):
        pass

    def without_timer(self):
        pygame.event.clear()
        self.config.change_square(8)
        self.ChessBoard = WithoutTimerChess()
        self.ValidMoves = self.ChessBoard.getValidMoves()
        self.GameDrawer = ChessDrawer(window=self.GameScreen, board=self.ChessBoard, valid_moves=self.ValidMoves,
                                      dragger=self.ChessDragger, settings=self.config)
        self.__draw_game()
        pygame.display.flip()
        game_start_sound.play_sound()
        while self.mainloop:
            if not self.game_end:
                self.__check_for_game_end()
            self.__update_mouse_position()
            self.__handle_events()
        pygame.quit()

    def __update_mouse_position(self):
        if HEIGHT >= pygame.mouse.get_pos()[0] and pygame.mouse.get_pos()[1] <= WIDTH:
            self.mouse_position = [angle // self.config.SQUARE_SIZE for angle in pygame.mouse.get_pos()]

    def __update_drag(self, event):
        # обновление позиции курсора мыши
        self.ChessDragger.update_mouse_position(event.pos)
        self.clicked_row = self.ChessDragger.mouse_position[1] // self.config.SQUARE_SIZE
        self.clicked_column = self.ChessDragger.mouse_position[0] // self.config.SQUARE_SIZE
        self.clicked_piece = self.ChessBoard.board[self.clicked_row][self.clicked_column]

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # выход из игры
                self.mainloop = False
            elif not self.game_end:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.__update_drag(event)
                    self.__handle_lbm_pressed()
                elif event.type == pygame.MOUSEMOTION:
                    self.__handle_mouse_motion(event)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.__handle_lbm_released()
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_z and
                      pygame.key.get_mods() & pygame.KMOD_LCTRL):
                    self.__undo_move()
            self.__draw_game()
            if self.ChessDragger.DRAGGING_FLAG:
                self.GameDrawer.draw_squares((self.ChessDragger.current_row, self.ChessDragger.current_column))
                self.ChessDragger.draw_dragged_piece(self.GameScreen)
            self.clock.tick(FPS)
            pygame.display.flip()
            if self.PIECE_MOVED_FLAG:
                self.__play_sound(self.last_move, is_nuclear=self.nuclear_game_mode)
                self.ValidMoves = self.ChessBoard.getValidMoves()
                self.GameDrawer.update_valid_moves(self.ValidMoves)
                self.PIECE_MOVED_FLAG = not self.PIECE_MOVED_FLAG
            if self.game_end:
                time.sleep(5)
                pygame.quit()  # TODO: Реализовать возвращение в главное меню

    def __undo_move(self):
        self.ChessBoard.undoMove()
        self.ValidMoves = self.ChessBoard.getValidMoves()
        self.GameDrawer.update_valid_moves(self.ValidMoves)

    def __handle_lbm_pressed(self):
        if self.ChessBoard.piece_to_promote:
            choice = self.mouse_position[1]
            if choice > 3 and self.ChessBoard.whiteMove:
                self.ChessBoard.promote_piece(self.ChessBoard.piece_to_promote, choice)
            elif choice <= 3 and not self.ChessBoard.whiteMove:
                self.ChessBoard.promote_piece(self.ChessBoard.piece_to_promote, choice)
        if (self.clicked_piece and ((self.clicked_piece.piece_color == WHITE and self.ChessBoard.whiteMove)
                                    or (
                                            self.clicked_piece.piece_color == BLACK and not self.ChessBoard.whiteMove)) or
                self.PlayerClicksLog):
            if (self.clicked_piece and ((self.clicked_piece.piece_color == WHITE and self.ChessBoard.whiteMove)
                                        or (
                                                self.clicked_piece.piece_color == BLACK and
                                                not self.ChessBoard.whiteMove))):
                self.ChessDragger.save_original_position()
                self.ChessDragger.drag_piece(self.clicked_piece)

            if self.clicked_piece or self.PlayerClicksLog:

                if (self.clicked_row, self.clicked_column) == self.PlayerSelectedCell:
                    self.PlayerSelectedCell = ()
                    self.PlayerClicksLog = []
                else:
                    self.PlayerSelectedCell = (self.clicked_row, self.clicked_column)
                    self.PlayerClicksLog.append(self.PlayerSelectedCell)

            # если кликов больше двух, то идет проверка на присутствие фигуры и правильность
            # совершаемого хода
            if len(self.PlayerClicksLog) == 2:
                # обновить список возможных ходов в том случае, если будет совершено превращение пешки
                self.ValidMoves = self.ChessBoard.getValidMoves()
                self.GameDrawer.update_valid_moves(self.ValidMoves)

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
                        self.__play_sound(move=move, is_error_action=True, is_nuclear=self.nuclear_game_mode)
                        self.PlayerSelectedCell = ()
                        self.PlayerClicksLog = []
                else:
                    self.PlayerSelectedCell = ()
                    self.PlayerClicksLog = []

    def __handle_mouse_motion(self, event):
        if (self.clicked_piece and ((self.clicked_piece.piece_color == WHITE and self.ChessBoard.whiteMove)
                                    or (
                                            self.clicked_piece.piece_color == BLACK and not self.ChessBoard.whiteMove)) or
                self.PlayerClicksLog):
            if self.ChessDragger.DRAGGING_FLAG:
                self.ChessDragger.update_mouse_position(new_position=event.pos)
                self.PlayerSelectedCell = (self.clicked_row, self.clicked_column)

    def __handle_lbm_released(self):
        if (self.clicked_piece and ((self.clicked_piece.piece_color == WHITE and self.ChessBoard.whiteMove)
                                    or (
                                            self.clicked_piece.piece_color == BLACK and not self.ChessBoard.whiteMove)) or
                self.PlayerClicksLog):
            if self.ChessDragger.DRAGGING_FLAG:
                released_row = self.ChessDragger.mouse_position[1] // self.config.SQUARE_SIZE
                released_col = self.ChessDragger.mouse_position[0] // self.config.SQUARE_SIZE
                self.ValidMoves = self.ChessBoard.getValidMoves()
                self.GameDrawer.update_valid_moves(self.ValidMoves)
                move = Move((self.ChessDragger.original_row, self.ChessDragger.original_column),
                            (released_row, released_col), self.ChessBoard)
                if move in self.ValidMoves:
                    self.ChessBoard.make_move(move)
                    self.last_move = move
                    self.PIECE_MOVED_FLAG = True
                else:
                    if ((self.ChessDragger.original_row, self.ChessDragger.original_column) !=
                            (released_row, released_col)):
                        self.__play_sound(move=move, is_error_action=True, is_nuclear=self.nuclear_game_mode)
                self.ChessDragger.undrag_piece()

    def __play_sound(self, move, is_error_action=False, force_end=False, is_nuclear=False):
        if force_end:
            if is_nuclear:
                big_explosion_sound.play_sound()
                return
            game_end_sound.play_sound()
        elif is_error_action:
            error_action_sound.play_sound()
        elif self.ChessBoard.is_variant_checkmate() and not self.ChessBoard.game_end:
            game_end_sound.play_sound()
        elif self.ChessBoard.is_variant_stalemate() and not self.ChessBoard.game_end:
            game_draw_sound.play_sound()
        elif self.ChessBoard.is_variant_check() and not self.ChessBoard.game_end:
            check_sound.play_sound()
        elif move and move.capturedPiece is not None and not self.ChessBoard.game_end:
            if is_nuclear:
                explosion_sound.play_sound()
            move_capture_sound.play_sound()
        else:
            move_sound.play_sound()

    def __draw_game(self):
        self.GameDrawer.draw_board()
        self.GameDrawer.draw_squares_valid_moves(self.PlayerSelectedCell)
        self.GameDrawer.draw_checked_king()
        self.GameDrawer.draw_pieces()
        if self.ChessBoard.piece_to_promote:
            self.GameDrawer.draw_promotion_rect(self.ChessBoard.piece_to_promote)
