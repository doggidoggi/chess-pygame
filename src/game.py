import pygame
import config
from chessboard import *
from dragger import Drag


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Шахматы')
        self.GameScreen = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
        self.GameScreen.fill(color=pygame.Color(184, 139, 74))
        self.mainloop = True
        self.ChessPygameClock = pygame.time.Clock()
        self.PlayerSelectedCell = ()
        self.ChessBoard = Board()
        self.ChessDragger = Drag()
        self.ValidMoves = self.ChessBoard.getValidMoves()
        self.PlayerClicksLog = []
        self.PIECE_MOVED_FLAG = False
        self.config = config
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

            self.draw_game(self.GameScreen, self.PlayerSelectedCell)
            if self.ChessDragger.DRAGGING_FLAG:
                self.draw_squares(self.GameScreen, (self.ChessDragger.current_row, self.ChessDragger.current_column))
                self.ChessDragger.draw_dragged_piece(self.GameScreen)
            self.ChessPygameClock.tick(FPS)
            pygame.display.flip()

            if self.PIECE_MOVED_FLAG:
                self.play_sound(self.last_move)
                self.ValidMoves = self.ChessBoard.getValidMoves()
                self.PIECE_MOVED_FLAG = not self.PIECE_MOVED_FLAG
        pygame.quit()

    def play_sound(self, move, is_error_action=False):
        if is_error_action:
            self.config.error_action_sound.play_sound()
        elif self.ChessBoard.is_variant_checkmate():
            self.config.game_end_sound.play_sound()
        elif self.ChessBoard.is_variant_stalemate():
            self.config.game_draw_sound.play_sound()
        elif self.ChessBoard.is_variant_check():
            self.config.check_sound.play_sound()
        elif move.capturedPiece is not None:
            self.config.move_capture_sound.play_sound()
        else:
            self.config.move_sound.play_sound()

    def draw_checked_king(self):
        if self.ChessBoard.is_variant_check():
            king_position = self.ChessBoard.whiteKingPosition if self.ChessBoard.whiteMove else (
                self.ChessBoard.blackKingPosition)
            circle_check = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            circle_check.set_alpha(100)
            circle_check.fill((178, 34, 34))
            self.GameScreen.blit(circle_check, (king_position[1] * SQUARE_SIZE, king_position[0] * SQUARE_SIZE))

    def draw_board(self, screen):
        for row in range(SQUARES_AMOUNT):
            for column in range(SQUARES_AMOUNT):
                color = SQUARE_COLORS[(row + column) % 2]
                pygame.draw.rect(screen, color, (SQUARE_SIZE * column, SQUARE_SIZE * row,
                                                 SQUARE_SIZE, SQUARE_SIZE))

                if column == 0:
                    color = SQUARE_COLORS[0] if (row + column) % 2 else SQUARE_COLORS[1]
                    label = font.render(str(SQUARES_AMOUNT - row), 1, color)
                    screen.blit(label, (2, row * SQUARE_SIZE))

                if row == 7:
                    color = SQUARE_COLORS[0] if (row + column) % 2 else SQUARE_COLORS[1]
                    label = font.render(colsToSquares.get(str(column)), 1, color)
                    screen.blit(label, (SQUARE_SIZE * column + SQUARE_SIZE * 0.85, SQUARE_SIZE * row + SQUARE_SIZE * 0.8))

    def draw_squares_valid_moves(self, screen, selectedCell):
        if selectedCell:
            draw_piece = self.ChessBoard.board[selectedCell[0]][selectedCell[1]]
            if draw_piece:
                row, column = selectedCell
                surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                surface.set_alpha(100)
                surface.fill((1, 50, 32))
                circle_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                circle_surface.set_alpha(100)
                circle_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(circle_surface, (1, 50, 32), (SQUARE_SIZE / 2, SQUARE_SIZE / 2), SQUARE_SIZE * 0.15)
                screen.blit(surface, (column * SQUARE_SIZE, row * SQUARE_SIZE))
                attack_square = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                attack_square.set_alpha(100)
                attack_square.fill((178, 34, 34))
                for move in self.ValidMoves:
                    if (move.startRow, move.startColumn) == (selectedCell[0], selectedCell[1]):
                        if self.ChessBoard.board[move.endRow][move.endColumn]:
                            screen.blit(attack_square, (move.endColumn * SQUARE_SIZE, move.endRow * SQUARE_SIZE))
                        else:
                            screen.blit(circle_surface, (move.endColumn * SQUARE_SIZE, move.endRow * SQUARE_SIZE))

    def draw_pieces(self, screen):
        for row in range(SQUARES_AMOUNT):
            for column in range(SQUARES_AMOUNT):
                draw_piece = self.ChessBoard.board[row][column]
                if draw_piece and draw_piece != self.ChessDragger.dragged_piece:
                    image_center = (column * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    rect = IMAGES80[draw_piece.symbol()].get_rect(center=image_center)
                    screen.blit(IMAGES80[draw_piece.symbol()],
                                rect)

    def draw_squares(self, screen, current_position):
        row, column = current_position
        surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        surface.set_alpha(90)
        surface.fill((1, 50, 32))
        screen.blit(surface, (column * SQUARE_SIZE, row * SQUARE_SIZE))

    def menu(self):
        bg_color = (255, 255, 255)
        self.GameScreen.fill(bg_color)
        black_color = (0, 0, 0)
        start_btn = pygame.Rect(270, 300, 100, 50)
        pygame.draw.rect(self.GameScreen, black_color, start_btn)
        white_color = (255, 255, 255)
        big_font = pygame.font.SysFont("comicsansms", 50)
        small_font = pygame.font.SysFont("comicsansms", 20)
        welcome_text = big_font.render("Шахматы", False, black_color)
        created_by = small_font.render("Created by Sheriff", True, black_color)
        start_btn_label = small_font.render("Играть", True, white_color)
        self.GameScreen.blit(welcome_text,
                         ((self.GameScreen.get_width() - welcome_text.get_width()) // 2,
                          150))
        self.GameScreen.blit(created_by,
                         ((self.GameScreen.get_width() - created_by.get_width()) // 2,
                          self.GameScreen.get_height() - created_by.get_height() - 100))
        self.GameScreen.blit(start_btn_label,
                         ((start_btn.x + (start_btn.width - start_btn_label.get_width()) // 2,
                           start_btn.y + (start_btn.height - start_btn_label.get_height()) // 2)))
        key_pressed = pygame.key.get_pressed()

    def draw_game(self, screen, selectedCell):
        self.draw_board(screen)
        self.draw_squares_valid_moves(screen, selectedCell)
        self.draw_checked_king()
        self.draw_pieces(screen)

