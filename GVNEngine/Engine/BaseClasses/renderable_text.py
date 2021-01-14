import pygame

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
    def __init__(self, scene, pos, text, font, font_size, color, center_align=False, z_order=0, key=None):
        super().__init__(scene, pos, center_align, z_order, key)

        self.font_obj = pygame.font.Font(font, font_size)
        self.text = text
        self.surface = self.font_obj.render(self.text, True, tuple(color))
        self.rect = self.surface.get_rect()

        # For new objects, resize initially in case we're already using a scaled resolution
        self.RecalculateSize(self.scene.resolution_multiplier)


