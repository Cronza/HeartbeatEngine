import pygame
import os
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
        #@TODO: Is it right that we concentate like this here?

        font = self.scene.settings.ConvertPartialToAbsolutePath(self.renderable_data['font'])
        self.text = self.renderable_data['text']
        text_size = self.renderable_data['text_size']
        text_color = self.renderable_data['text_color']

        self.font_obj = pygame.font.Font(font, text_size)
        self.surface = self.font_obj.render(self.text, True, text_color) #@TODO: Change the editor to use vector tuple nstead of lift for color
        self.rect = self.surface.get_rect()

        # For new objects, resize initially in case we're already using a scaled resolution
        self.RecalculateSize(self.scene.resolution_multiplier)


