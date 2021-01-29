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
    def __init__(self, scene, renderable_data):
        super().__init__(scene, renderable_data)

        # YAML Parameters
        font = self.renderable_data['font']
        text = self.renderable_data['text']
        text_size = self.renderable_data['text_size']
        text_color = tuple(self.renderable_data['text_color'])

        self.font_obj = pygame.font.Font(font, text_size)
        self.text = text
        self.surface = self.font_obj.render(self.text, True, text_color)
        self.rect = self.surface.get_rect()

        # For new objects, resize initially in case we're already using a scaled resolution
        self.RecalculateSize(self.scene.resolution_multiplier)


