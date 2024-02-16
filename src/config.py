from constants import *


class Config:
    def __init__(self):
        pygame.font.init()
        self.SQUARE_AMOUNT = 8
        self.SQUARE_SIZE = WIDTH // self.SQUARE_AMOUNT
        self.SQUARE_COLORS = [pygame.Color(227, 193, 111),
                              pygame.Color(184, 139, 74)]  # цвета клеток для шахматной доски
        self.font = pygame.font.SysFont('../src/assets/Rubik-VariableFont_wght.ttf', 20)

    def change_square(self, amount):
        self.SQUARE_AMOUNT = amount
        self.SQUARE_SIZE = WIDTH // self.SQUARE_AMOUNT
