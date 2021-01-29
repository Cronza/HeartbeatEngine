import pygame

from Engine.Utilities.data_classes import State
from Engine.BaseClasses.interactable import Interactable
from Engine.BaseClasses.renderable import Renderable
from Engine.BaseClasses.renderable_sprite import SpriteRenderable
from Engine.BaseClasses.renderable_text import TextRenderable
from Engine.BaseClasses.renderable_container import Container

class Choice(Container):
    def __init__(self, scene, data, pos, center_align=True, z_order=0, key=None):
        super().__init__(scene, pos, center_align, z_order, key)
        self.visible = False

        #Pass in a button list, and generate buttons

        # Load any specified buttons
        if 'buttons' in data:
            f_buttons = data['buttons']

            for f_button in f_buttons:
                self.children.append(self.scene.a_manager.PerformAction(f_button, 'create_button'))
        else:
            print('Data file does not specify any buttons')