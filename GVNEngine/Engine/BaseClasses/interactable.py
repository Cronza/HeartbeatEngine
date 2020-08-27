import pygame

from Engine.Utilities.data_classes import State
from Engine.BaseClasses.renderable_sprite import SpriteRenderable


class Interactable(SpriteRenderable):
    def __init__(self, scene, data_path, pos):
        super().__init__(scene, data_path, pos)

        # We need to be able to talk to the scene object for render calls
        self.scene = None

        # Track input state using the State enum
        self.state = State(0)

        # Track whether the previous input frame was clicking to determine whether this interactable was clicked
        self.isClicking = False


    def update(self, *args):
        super().update()

        # If being hovered...
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            # If not already in the hover state...
            if self.state is State.normal:
                self.surface = pygame.image.load(self.renderable_data['sprite_hover']).convert_alpha()
                self.state = State.hover
                self.scene.Draw()
            else:  # Track whether the user has release their cursor over the sprite
                if pygame.mouse.get_pressed()[0] == 1:
                    # Begin the click
                    self.isClicking = True
                elif pygame.mouse.get_pressed()[0] == 0 and self.isClicking is True:
                    # User has clicked this renderable
                    self.Interact()
                    self.isClicking = False
                elif self.isClicking is True:
                    # End the click
                    self.isClicking = False

        # If no longer hovering...
        elif self.state is State.hover:
            self.surface = pygame.image.load(self.renderable_data['sprite']).convert_alpha()
            self.state = State.normal
            self.scene.Draw()

    def Interact(self):
        # Check if any actions are defined in the data file
        if 'action' in self.renderable_data:
            self.scene.a_manager.PerformAction(self.renderable_data['action'])
        else:
            print("No actions defined for this object - Clicking does nothing")

