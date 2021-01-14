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

        # Instead of building the text renderale here, let's ue the action manager. That way, the button class ends up
        # acting more like an interactable container
        # ^ won't work, as containers have a special removal process that isn't support by normal renderables

        """
        # Load any specified text
        if 'text' in self.renderable_data:
            f_texts = self.renderable_data['text']

            for f_text in f_texts:
                f_text['action'] = 'create_text'
                self.children.append(self.scene.a_manager.PerformAction(f_text))
        else:
            print('Data file does not specify any text')
        """

    def GetText(self):
        pass

    def SetText(self):
        pass

