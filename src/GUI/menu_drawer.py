from src.utils import *
from src.constants import *


class MainMenuDrawer:
    def __init__(self, window, settings):
        self.GameScreen: pygame.Surface = window
        self.config = settings

        self.background_surface = None
        self.board_surface = None
        self.singleplayer_button = None
        self.singleplayer_button_surface = None
        self.multiplayer_button = None
        self.multiplayer_button_surface = None
        self.without_timer_button = None
        self.without_timer_button_surface = None
        self.until_check_button = None
        self.until_check_button_surface = None
        self.nuclear_chess_button = None
        self.nuclear_chess_button_surface = None
        self.checkers_button = None
        self.checkers_button_surface = None
        self.chess_960_button = None
        self.chess_960_button_surface = None
        self.opposite_chess_button = None
        self.opposite_chess_button_surface = None
        self.marseille_chess_button = None
        self.marseille_chess_button_surface = None
        self.mini_chess_button = None
        self.mini_chess_button_surface = None
        self.bird_chess_button = None
        self.bird_chess_button_surface = None

        self.quit_button = None
        self.quit_button_surface = None
        self.in_main_menu = True
        self.in_AI_setup = False
        self.in_PVP_setup = False
        self.button_font_color = pygame.Color(255, 255, 255)
        self.__setup_buttons()

    def __setup_buttons(self):
        width = WIDTH // 4
        height = HEIGHT // 8
        color = pygame.Color(87, 131, 219)
        x_axis = WIDTH / 2 - width / 2
        y_axis = height * 2.5
        self.multiplayer_button = pygame.Rect(x_axis, y_axis, width, height)
        self.multiplayer_button_surface = get_button(self.multiplayer_button, pygame.font.SysFont('Ubuntu', 20,
                                                                                                  bold=True),
                                                     self.button_font_color, color, 'Против друга', WIDTH, HEIGHT)
        y_axis = height * 4
        self.singleplayer_button = pygame.Rect(x_axis, y_axis, width, height)
        self.singleplayer_button_surface = get_button(self.singleplayer_button, pygame.font.SysFont('Ubuntu', 20,
                                                                                                    bold=True),
                                                      self.button_font_color, color, 'Одиночная Игра', WIDTH, HEIGHT)
        y_axis = height * 1
        self.opposite_chess_button = pygame.Rect(x_axis, y_axis, width, height)
        self.opposite_chess_button_surface = get_button(self.opposite_chess_button,
                                                        pygame.font.SysFont('Ubuntu', 20,
                                                                            bold=True),
                                                        self.button_font_color, color, 'Наоборот', WIDTH, HEIGHT)
        y_axis = height * 2.5
        self.without_timer_button = pygame.Rect(x_axis, y_axis, width, height)
        self.without_timer_button_surface = get_button(self.without_timer_button,
                                                       pygame.font.SysFont('Ubuntu', 20,
                                                                           bold=True),
                                                       self.button_font_color, color, 'Без времени', WIDTH, HEIGHT)
        y_axis = height * 4
        self.until_check_button = pygame.Rect(x_axis, y_axis, width, height)
        self.until_check_button_surface = get_button(self.until_check_button,
                                                     pygame.font.SysFont('Ubuntu', 20,
                                                                         bold=True),
                                                     self.button_font_color, color, 'До шаха', WIDTH, HEIGHT)
        y_axis = height * 5.5
        self.nuclear_chess_button = pygame.Rect(x_axis, y_axis, width, height)
        self.nuclear_chess_button_surface = get_button(self.nuclear_chess_button,
                                                       pygame.font.SysFont('Ubuntu', 20,
                                                                           bold=True),
                                                       self.button_font_color, color, 'Ядерные', WIDTH, HEIGHT)
        y_axis = height * 1
        x_axis = WIDTH / 2 - width * 1.8
        self.mini_chess_button = pygame.Rect(x_axis, y_axis, width, height)
        self.mini_chess_button_surface = get_button(self.mini_chess_button,
                                                    pygame.font.SysFont('Ubuntu', 20,
                                                                        bold=True),
                                                    self.button_font_color, color, 'Мини', WIDTH, HEIGHT)
        y_axis = height * 4
        self.chess_960_button = pygame.Rect(x_axis, y_axis, width, height)
        self.chess_960_button_surface = get_button(self.chess_960_button,
                                                   pygame.font.SysFont('Ubuntu', 20,
                                                                       bold=True),
                                                   self.button_font_color, color, '960', WIDTH, HEIGHT)
        y_axis = height * 2.5
        self.bird_chess_button = pygame.Rect(x_axis, y_axis, width, height)
        self.bird_chess_button_surface = get_button(self.bird_chess_button,
                                                    pygame.font.SysFont('Ubuntu', 20,
                                                                        bold=True),
                                                    self.button_font_color, color, 'Птичьи', WIDTH, HEIGHT)
        y_axis = height * 5.5
        self.checkers_button = pygame.Rect(x_axis, y_axis, width, height)
        self.checkers_button_surface = get_button(self.checkers_button,
                                                  pygame.font.SysFont('Ubuntu', 20,
                                                                      bold=True),
                                                  self.button_font_color, color, 'Шашки', WIDTH, HEIGHT)
        y_axis = height * 1
        x_axis = WIDTH / 2 + width / 1.2
        self.marseille_chess_button = pygame.Rect(x_axis, y_axis, width, height)
        self.marseille_chess_button_surface = get_button(self.marseille_chess_button,
                                                         pygame.font.SysFont('Ubuntu', 20,
                                                                             bold=True),
                                                         self.button_font_color, color, 'Марсельские', WIDTH, HEIGHT)
        y_axis = height * 5.5
        self.quit_button = pygame.Rect(x_axis, y_axis, width, height)
        self.quit_button_surface = get_button(self.quit_button,
                                              pygame.font.SysFont('Ubuntu', 20,
                                                                  bold=True),
                                              self.button_font_color, pygame.Color(139, 0, 0), 'Назад', WIDTH, HEIGHT)

    def set_page_in_main_menu(self, boolean):
        self.in_main_menu = boolean

    def set_page_in_AI_setup(self, boolean):
        self.in_AI_setup = boolean

    def set_page_in_PVP_setup(self, boolean):
        self.in_PVP_setup = boolean

    def draw(self):
        self.GameScreen.fill((200, 200, 200))
        if self.in_main_menu:
            self.GameScreen.blit(self.multiplayer_button_surface, (0, 0))
            self.GameScreen.blit(self.singleplayer_button_surface, (0, 0))
        elif self.in_PVP_setup:
            self.GameScreen.blit(self.quit_button_surface, (0, 0))
            self.GameScreen.blit(self.without_timer_button_surface, (0, 0))
            self.GameScreen.blit(self.until_check_button_surface, (0, 0))
            self.GameScreen.blit(self.nuclear_chess_button_surface, (0, 0))
            self.GameScreen.blit(self.opposite_chess_button_surface, (0, 0))
            self.GameScreen.blit(self.chess_960_button_surface, (0, 0))
            self.GameScreen.blit(self.checkers_button_surface, (0, 0))
            self.GameScreen.blit(self.bird_chess_button_surface, (0, 0))
            self.GameScreen.blit(self.marseille_chess_button_surface, (0, 0))
            self.GameScreen.blit(self.mini_chess_button_surface, (0, 0))
        elif self.in_AI_setup:
            self.GameScreen.blit(self.quit_button_surface, (0, 0))
        pygame.display.flip()
