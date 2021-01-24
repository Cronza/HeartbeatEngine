import pygame

from Engine.Utilities.data_classes import State
from Engine.BaseClasses.interactable import Interactable
from Engine.BaseClasses.renderable_text import TextRenderable

class Button(Interactable):
    """
    The Button class extends the 'Interactable' class, and adds an additional child 'TextRenderable'
    """
    def __init__(self, scene, data_path, pos, text_position, text, font, font_size, text_color,
                 text_z_order=0, text_center_align=True, center_align=True, z_order=0, key=None, initial_rescale=False):
        super().__init__(scene, data_path, pos, center_align, z_order, key, initial_rescale)

        #@TODO: Make the text part optionable
        # Initialize text renderable
        button_text_renderable = TextRenderable(
            self.scene,
            text_position,
            text,
            font,
            font_size,
            text_color,
            text_center_align,
            text_z_order,
            self.key + "_Text"  # For simplicity, child text renderables will inherit a mod. version of the button's key
        )
        self.children.append(button_text_renderable)
        self.scene.renderables_group.Add(button_text_renderable)

    def GetText(self):
        pass

    def SetText(self):
        pass

