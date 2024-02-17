import pygame.time

import src.config
from src.Game.Controllers.game_controllers import Game
from src.GUI.menu_drawer import *
from src.config import *


class Menu:
    def __init__(self, window, settings):
        self.GameScreen = window
        self.config = settings

        self.MenuDrawer = MainMenuDrawer(window=self.GameScreen, settings=self.config)
        self.in_menu = True
        self.clock = pygame.time.Clock()

    def main_loop(self):
        while self.in_menu:
            self.MenuDrawer.draw()
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.in_menu = False
                elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT_CLICK:
                    self.__handle_lmb_up()

    def __handle_lmb_up(self):
        game = Game(window=self.GameScreen, settings=self.config)
        mouse_position = pygame.mouse.get_pos()
        if self.MenuDrawer.opposite_chess_button.collidepoint(mouse_position) and self.MenuDrawer.in_PVP_setup:
            game.opposite_chess()
        elif self.MenuDrawer.without_timer_button.collidepoint(mouse_position) and self.MenuDrawer.in_PVP_setup:
            game.without_timer()
        elif self.MenuDrawer.checkers_button.collidepoint(mouse_position) and self.MenuDrawer.in_PVP_setup:
            game.checkers()
        elif self.MenuDrawer.until_check_button.collidepoint(mouse_position) and self.MenuDrawer.in_PVP_setup:
            game.until_the_first_check()
        elif self.MenuDrawer.marseille_chess_button.collidepoint(mouse_position) and self.MenuDrawer.in_PVP_setup:
            game.marseille_chess()
        elif self.MenuDrawer.nuclear_chess_button.collidepoint(mouse_position) and self.MenuDrawer.in_PVP_setup:
            game.nuclear_chess()
        elif self.MenuDrawer.mini_chess_button.collidepoint(mouse_position) and self.MenuDrawer.in_PVP_setup:
            game.mini_chess()
        elif self.MenuDrawer.chess_960_button.collidepoint(mouse_position) and self.MenuDrawer.in_PVP_setup:
            game.chess_960()
        elif self.MenuDrawer.multiplayer_button.collidepoint(mouse_position) and self.MenuDrawer.in_main_menu:
            self.MenuDrawer.set_page_in_main_menu(False)
            self.MenuDrawer.set_page_in_PVP_setup(True)
            click_sound.play_sound()
        elif self.MenuDrawer.singleplayer_button.collidepoint(mouse_position) and self.MenuDrawer.in_main_menu:
            game.against_ai()
        elif (self.MenuDrawer.quit_button.collidepoint(mouse_position) and self.MenuDrawer.in_PVP_setup
              or self.MenuDrawer.quit_button.collidepoint(mouse_position) and self.MenuDrawer.in_AI_setup):
            self.MenuDrawer.set_page_in_main_menu(True)
            self.MenuDrawer.set_page_in_PVP_setup(False)
            click_sound.play_sound()


