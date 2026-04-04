import pygame
from src.constants import *


class ChessDrawer:
    def __init__(self, window, board, valid_moves, dragger, settings):
        self.GameScreen = window
        self.ChessBoard = board
        self.ValidMoves = valid_moves
        self.ChessDragger = dragger
        self.config = settings

    def __setup_window(self):
        self.GameScreen.fill(color=pygame.Color(184, 139, 74))

    def update_valid_moves(self, valid_moves):
        self.ValidMoves = valid_moves

    def draw_checked_king(self):
        if self.ChessBoard.is_variant_check():
            king_position = self.ChessBoard.whiteKingPosition if self.ChessBoard.whiteMove else (
                self.ChessBoard.blackKingPosition)
            circle_check = pygame.Surface((self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))
            circle_check.set_alpha(100)
            circle_check.fill((178, 34, 34))
            self.GameScreen.blit(circle_check, (king_position[1] * self.config.SQUARE_SIZE, king_position[0] * self.config.SQUARE_SIZE))

    def draw_board(self):
        for row in range(self.config.SQUARE_AMOUNT):
            for column in range(self.config.SQUARE_AMOUNT):
                color = self.config.SQUARE_COLORS[(row + column) % 2]
                pygame.draw.rect(self.GameScreen, color, (self.config.SQUARE_SIZE * column, self.config.SQUARE_SIZE * row,
                                                          self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))

                if column == 0:
                    color = self.config.SQUARE_COLORS[0] if (row + column) % 2 else self.config.SQUARE_COLORS[1]
                    label = self.config.font.render(str(self.config.SQUARE_AMOUNT - row), 1, color)
                    self.GameScreen.blit(label, (2, row * self.config.SQUARE_SIZE))

                if row == 7:
                    color = self.config.SQUARE_COLORS[0] if (row + column) % 2 else self.config.SQUARE_COLORS[1]
                    label = self.config.font.render(colsToSquares.get(str(column)), 1, color)
                    self.GameScreen.blit(label, (
                        self.config.SQUARE_SIZE * column + self.config.SQUARE_SIZE * 0.85, self.config.SQUARE_SIZE * row + self.config.SQUARE_SIZE * 0.8))

    def draw_squares_valid_moves(self, selectedCell):
        if selectedCell:
            draw_piece = self.ChessBoard.board[selectedCell[0]][selectedCell[1]]
            if draw_piece:
                row, column = selectedCell
                surface = pygame.Surface((self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))
                surface.set_alpha(100)
                surface.fill((1, 50, 32))
                circle_surface = pygame.Surface((self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))
                circle_surface.set_alpha(100)
                circle_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(circle_surface, (1, 50, 32), (self.config.SQUARE_SIZE / 2, self.config.SQUARE_SIZE / 2), self.config.SQUARE_SIZE * 0.15)
                self.GameScreen.blit(surface, (column * self.config.SQUARE_SIZE, row * self.config.SQUARE_SIZE))
                attack_square = pygame.Surface((self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))
                attack_square.set_alpha(100)
                attack_square.fill((178, 34, 34))
                for move in self.ValidMoves:
                    if (move.startRow, move.startColumn) == (selectedCell[0], selectedCell[1]):
                        if self.ChessBoard.board[move.endRow][move.endColumn]:
                            self.GameScreen.blit(attack_square,
                                                 (move.endColumn * self.config.SQUARE_SIZE, move.endRow * self.config.SQUARE_SIZE))
                        else:
                            self.GameScreen.blit(circle_surface,
                                                 (move.endColumn * self.config.SQUARE_SIZE, move.endRow * self.config.SQUARE_SIZE))

    def draw_pieces(self):
        for row in range(self.config.SQUARE_AMOUNT):
            for column in range(self.config.SQUARE_AMOUNT):
                draw_piece = self.ChessBoard.board[row][column]
                if draw_piece and draw_piece != self.ChessDragger.dragged_piece:
                    image_center = (column * self.config.SQUARE_SIZE + self.config.SQUARE_SIZE // 2, row * self.config.SQUARE_SIZE + self.config.SQUARE_SIZE // 2)
                    rect = IMAGES80[draw_piece.symbol()].get_rect(center=image_center)
                    self.GameScreen.blit(IMAGES80[draw_piece.symbol()],
                                         rect)

    def draw_squares(self, current_position):
        row, column = current_position
        surface = pygame.Surface((self.config.SQUARE_SIZE, self.config.SQUARE_SIZE))
        surface.set_alpha(90)
        surface.fill((1, 50, 32))
        self.GameScreen.blit(surface, (column * self.config.SQUARE_SIZE, row * self.config.SQUARE_SIZE))

    def draw_promotion_rect(self, current_position):
        row, column = current_position
        if self.ChessBoard.board[row][column].piece_color == WHITE:
            rect = pygame.Rect(self.config.SQUARE_SIZE * column, self.config.SQUARE_SIZE * row, self.config.SQUARE_SIZE, self.config.SQUARE_SIZE * 4)
            pygame.draw.rect(self.GameScreen, (255, 255, 255), rect)
            for i in range(len(PROMOTION_WHITE)):
                self.GameScreen.blit(IMAGES80[PROMOTION_WHITE[i]], (column * self.config.SQUARE_SIZE, i * self.config.SQUARE_SIZE))
        else:
            row -= 3
            rect = pygame.Rect(self.config.SQUARE_SIZE * column, self.config.SQUARE_SIZE * row, self.config.SQUARE_SIZE, self.config.SQUARE_SIZE * 4)
            pygame.draw.rect(self.GameScreen, (255, 255, 255), rect)
            for i in range(1, len(PROMOTION_BLACK) + 1):
                piece = IMAGES80[PROMOTION_BLACK[-i]]
                i += 3
                self.GameScreen.blit(piece, (column * self.config.SQUARE_SIZE, i * self.config.SQUARE_SIZE))
