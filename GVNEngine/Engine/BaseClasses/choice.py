import pygame

from Engine.Utilities.data_classes import State
from Engine.BaseClasses.interactable import Interactable
from Engine.BaseClasses.renderable import Renderable
from Engine.BaseClasses.renderable_sprite import SpriteRenderable
from Engine.BaseClasses.renderable_text import TextRenderable
from Engine.BaseClasses.renderable_container import Container

class Choice(Container):
    def __init__(self, scene, renderable_data):
        super().__init__(scene, renderable_data)
        self.visible = False

        """
        - action: "choice"
            choices:
              - 1:
                  branch: "Choice01_YesImGood"
                  text: "Im doing alright"
                  position:
                    - 0.4
                    - 0.5
                  key: "Choice01"
              - 2:
                  branch: "Choice01_ICouldBeBetter"
                  text: "I could be better"
                  position:
                    - 0.6
                    - 0.5
                  key: "Choice02"
        """

        #Pass in a button list, and generate buttons
        assert 'choices' in self.renderable_data, print(
            f"No 'choices' block assigned to {self}. This makes for an impossible action!")

        for choice in renderable_data['choices']:
            # Create each choice button
            self.children.append(self.scene.a_manager.PerformAction(choice, 'create_choice_button'))