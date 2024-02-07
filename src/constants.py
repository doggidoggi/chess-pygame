import pygame
import os
from src.Game.Models.sound import Sound

pygame.font.init()

WHITE = 1  # белый цвет
BLACK = 2  # черный цвет

LEFT_CLICK = 1
RIGHT_CLICK = 3

BLACK_PAWN_START_ROW = 1
WHITE_PAWN_START_ROW = 6

WIDTH = HEIGHT = 600  # размеры окна
SQUARES_AMOUNT = 8  # количество клеток
SQUARE_SIZE = WIDTH // SQUARES_AMOUNT  # размеры одной шахматной клетки

IMAGES128 = {}  # изображения, которые будут загружаться во время старта игры
pieces = ['bBishop', 'bKing', 'bKnight', 'bPawn', 'bQueen', 'bRook',
          'wBishop', 'wKing', 'wKnight', 'wPawn', 'wQueen', 'wRook']
IMAGES80 = {}  # изображения, которые будут загружаться во время старта игры
_pieces = ['bBishop', 'bKing', 'bKnight', 'bPawn', 'bQueen', 'bRook',
           'wBishop', 'wKing', 'wKnight', 'wPawn', 'wQueen', 'wRook']

for _piece in _pieces:
    IMAGES128[_piece] = pygame.image.load("../src/assets/images/pieces128/" + _piece + ".png")
for _piece in _pieces:
    IMAGES80[_piece] = pygame.image.load("../src/assets/images/pieces80/" + _piece + ".png")

FPS = 60  # кадры в секунду
SQUARE_COLORS = [pygame.Color(227, 193, 111), pygame.Color(184, 139, 74)]  # цвета клеток для шахматной доски

rowsToSquares = {'7': 1, '6': 2, '5': 3, '4': 4,
                 '3': 5, '2': 6, '1': 7, '0': 8}
colsToSquares = {'0': 'a', '1': 'b', '2': 'c', '3': 'd',
                 '4': 'e', '5': 'f', '6': 'g', '7': 'h'}
squaresToRow = {str(square): int(row) for row, square in rowsToSquares.items()}
squaresToCols = {square: int(col) for col, square in colsToSquares.items()}

move_sound = Sound(os.path.join('assets/sounds/game/move-self.mp3'))
move_capture_sound = Sound(os.path.join('assets/sounds/game/capture.mp3'))
check_sound = Sound(os.path.join('assets/sounds/game/move-check.mp3'))
error_action_sound = Sound(os.path.join('assets/sounds/game/illegal.mp3'))
game_end_sound = Sound(os.path.join('assets/sounds/game/game-end.mp3'))
game_draw_sound = Sound(os.path.join('assets/sounds/game/game-draw.mp3'))

font = pygame.font.SysFont('monospace', int(SQUARE_SIZE * 0.2), bold=True)
