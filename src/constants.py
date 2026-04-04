from pathlib import Path

import pygame
from src.Game.sound import Sound

WHITE = 1
BLACK = 2

LEFT_CLICK = 1
RIGHT_CLICK = 3

BLACK_PAWN_START_ROW = 1
WHITE_PAWN_START_ROW = 6

WIDTH = HEIGHT = 600

SRC_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SRC_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"

ICON_PATH = ASSETS_DIR / "images" / "icon.png"

IMAGES128 = {}
IMAGES80 = {}

_PIECES = [
    "bBishop", "bKing", "bKnight", "bPawn", "bQueen", "bRook",
    "wBishop", "wKing", "wKnight", "wPawn", "wQueen", "wRook",
]

PROMOTION_WHITE = ["wQueen", "wRook", "wKnight", "wBishop"]
PROMOTION_BLACK = ["bQueen", "bRook", "bKnight", "bBishop"]

for _piece in _PIECES:
    IMAGES128[_piece] = pygame.image.load(
        str(ASSETS_DIR / "images" / "pieces128" / f"{_piece}.png")
    )

for _piece in _PIECES:
    IMAGES80[_piece] = pygame.image.load(
        str(ASSETS_DIR / "images" / "pieces80" / f"{_piece}.png")
    )

FPS = 60

rowsToSquares = {"7": 1, "6": 2, "5": 3, "4": 4, "3": 5, "2": 6, "1": 7, "0": 8}
colsToSquares = {"0": "a", "1": "b", "2": "c", "3": "d", "4": "e", "5": "f", "6": "g", "7": "h"}
squaresToRow = {str(square): int(row) for row, square in rowsToSquares.items()}
squaresToCols = {square: int(col) for col, square in colsToSquares.items()}

move_sound = Sound(str(ASSETS_DIR / "sounds" / "game" / "move-self.mp3"))
move_capture_sound = Sound(str(ASSETS_DIR / "sounds" / "game" / "capture.mp3"))
check_sound = Sound(str(ASSETS_DIR / "sounds" / "game" / "move-check.mp3"))
error_action_sound = Sound(str(ASSETS_DIR / "sounds" / "game" / "illegal.mp3"))
game_end_sound = Sound(str(ASSETS_DIR / "sounds" / "game" / "game-end.mp3"))
game_draw_sound = Sound(str(ASSETS_DIR / "sounds" / "game" / "game-draw.mp3"))
game_start_sound = Sound(str(ASSETS_DIR / "sounds" / "game" / "game-start.mp3"))
big_explosion_sound = Sound(str(ASSETS_DIR / "sounds" / "game" / "explosion.wav"))
explosion_sound = Sound(str(ASSETS_DIR / "sounds" / "game" / "explosion.wav"))
# В архиве нет отдельных menu/misc/nuclear sound-файлов.
# Даём безопасные алиасы, чтобы импорт не падал.
click_sound = move_sound