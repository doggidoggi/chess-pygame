import pygame


def get_button(button_rect: pygame.Rect, button_font: pygame.font.Font, font_color: pygame.Color,
               button_color: pygame.Color, button_text: str, width: int, height: int) -> object:
    button = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(button, button_color, button_rect)
    text_surface = button_font.render(button_text, True, font_color)
    text_rect = text_surface.get_rect()
    text_rect.center = button_rect.center
    button.blit(text_surface, text_rect)
    return button
