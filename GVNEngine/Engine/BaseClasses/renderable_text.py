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
    def __init__(self, scene, pos, text, font, font_size, color, center_align = False):
        super().__init__(scene, pos, center_align)

        self.font_obj = pygame.font.Font(font, font_size)
        self.surface = self.font_obj.render(text, True, tuple(color))
        self.rect = self.surface.get_rect()

        # For new objects, resize initially in case we're already using a scaled resolution
        self.RecalculateSize(self.scene.resolution_multiplier)




