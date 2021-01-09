import pygame

from Engine.Utilities.data_classes import State
from Engine.BaseClasses.interactable import Interactable
from Engine.BaseClasses.renderable_text import TextRenderable

class Button(Interactable):
    def __init__(self, scene, data_path, pos, text_position, text, font, font_size, text_color,
                 text_z_order=0, text_center_align=True, center_align=True, z_order=0, initial_rescale=False):
        super().__init__(scene, data_path, pos, center_align, z_order, initial_rescale)

        # Initialize text renderable
        self.children.append(
            TextRenderable(
                self.scene,
                text_position,
                text,
                font,
                font_size,
                text_color,
                text_center_align,
                text_z_order
            )
        )

        #self.font_obj = pygame.font.Font(self.renderable_data['font'], self.renderable_data['font_size'])
        #self.text = self.renderable_data['text']
        #self.surface = self.font_obj.render(self.text, True, tuple(color))
        #self.rect = self.surface.get_rect()

        # Add the text renderable to the main surface as only one surface can be drawn per object
        #print(self.surface.get_rect())
        #print(self.text_renderable.rect)
        #self.GetSurface().blit(self.text_renderable.GetSurface(), (self.text_renderable.rect.x, self.text_renderable.rect.y))

    def GetText(self):
        pass

    def SetText(self):
        pass

