import pygame

from Engine.Utilities.yaml_reader import Reader
from Engine.BaseClasses.renderable import Renderable


class TextRenderable(Renderable):
    """
    The Text Renderable class is the base class for renderable text elements in the GVNEngine. This includes:
        - Titles
        - Sub-titles
        - Actions text
        - Pop-up text
        - etc
    """
    def __init__(self, pos, text, font, font_size, color):
        super().__init__(pos)

        self.font_obj = pygame.font.Font(font, font_size)
        self.surface = self.font_obj.render(text, True, tuple(color))
        self.rect = self.surface.get_rect()
        self.center_align = False




