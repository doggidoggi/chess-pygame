import pygame


class Sound:
    def __init__(self, file_path):
        pygame.mixer.init()
        self.file_path = file_path
        self.sound_object = pygame.mixer.Sound(file_path)

    def play_sound(self):
        pygame.mixer.Sound.play(self.sound_object)
