import pygame
import os
from src.Game.sound import Sound

WHITE = 1  # белый цвет
BLACK = 2  # черный цвет

LEFT_CLICK = 1
RIGHT_CLICK = 3

BLACK_PAWN_START_ROW = 1
WHITE_PAWN_START_ROW = 6

WIDTH = HEIGHT = 600  # размеры окна

ICON_PATH = "../src/assets/images/icon.png"

IMAGES128 = {}  # изображения, которые будут загружаться во время старта игры
IMAGES80 = {}  # изображения, которые будут загружаться во время старта игры
_pieces = ['bBishop', 'bKing', 'bKnight', 'bPawn', 'bQueen', 'bRook',
           'wBishop', 'wKing', 'wKnight', 'wPawn', 'wQueen', 'wRook']
_checkers = ['bChecker', 'wChecker', 'wKinger', 'bKinger']

PROMOTION_WHITE = ['wQueen', 'wRook', 'wKnight', 'wBishop']
PROMOTION_BLACK = ['bQueen', 'bRook', 'bKnight', 'bBishop']

for _piece in _pieces:
    IMAGES128[_piece] = pygame.image.load("../src/assets/images/pieces128/chess/" + _piece + ".png")
for _piece in _pieces:
    IMAGES80[_piece] = pygame.image.load("../src/assets/images/pieces80/chess/" + _piece + ".png")

for _piece in _checkers:
    IMAGES128[_piece] = pygame.image.load("../src/assets/images/pieces128/checkers/" + _piece + ".png")
for _piece in _checkers:
    IMAGES80[_piece] = pygame.image.load("../src/assets/images/pieces80/checkers/" + _piece + ".png")

FPS = 60  # кадры в секунду

rowsToSquares = {'7': 1, '6': 2, '5': 3, '4': 4,
                 '3': 5, '2': 6, '1': 7, '0': 8}
colsToSquares = {'0': 'a', '1': 'b', '2': 'c', '3': 'd',
                 '4': 'e', '5': 'f', '6': 'g', '7': 'h'}
squaresToRow = {str(square): int(row) for row, square in rowsToSquares.items()}
squaresToCols = {square: int(col) for col, square in colsToSquares.items()}

move_sound = Sound(os.path.join('assets/sounds/board/move-self.mp3'))
move_capture_sound = Sound(os.path.join('assets/sounds/board/capture.mp3'))
check_sound = Sound(os.path.join('assets/sounds/board/move-check.mp3'))
error_action_sound = Sound(os.path.join('assets/sounds/board/illegal.mp3'))
game_end_sound = Sound(os.path.join('assets/sounds/board/game-end.mp3'))
game_draw_sound = Sound(os.path.join('assets/sounds/board/game-draw.mp3'))
game_start_sound = Sound(os.path.join('assets/sounds/board/game-start.mp3'))
explosion_sound = Sound(os.path.join('assets/sounds/misc/nuclear/explosion.ogg'))
big_explosion_sound = Sound(os.path.join('assets/sounds/misc/nuclear/big-explosion.mp3'))
click_sound = Sound(os.path.join('assets/sounds/menu/click.mp3'))
