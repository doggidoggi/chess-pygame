import src.Game.Controllers.game_controllers
from src.constants import *


class MainGameDrawer:
    def __init__(self, window, board, valid_moves, dragger):
        self.GameScreen = window
        self.ChessBoard = board
        self.ValidMoves = valid_moves
        self.ChessDragger = dragger

    def __setup_window(self):
        self.GameScreen.fill(color=pygame.Color(184, 139, 74))

    def update_valid_moves(self, valid_moves):
        self.ValidMoves = valid_moves

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