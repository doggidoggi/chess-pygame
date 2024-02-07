import pygame
from src.Game.Controllers.game_controllers import Game
from constants import *


def main():
    pygame.init()
    pygame.font.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
    pygame.display.set_caption('Шахматы')
    game = Game(window)
    game.main_loop()
    pygame.quit()


if __name__ == '__main__':
    main()
