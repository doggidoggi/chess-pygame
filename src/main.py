import pygame

from src.Game.Controllers.menu_controllers import Menu
from src.config import Config
from src.constants import WIDTH, HEIGHT, ICON_PATH


def main():
    pygame.init()
    pygame.font.init()

    config = Config()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Шахматы PYGAME")

    icon = pygame.transform.smoothscale(pygame.image.load(str(ICON_PATH)), (80, 80))
    pygame.display.set_icon(icon)

    Menu(window, config).main_loop()
    pygame.quit()


if __name__ == "__main__":
    main()