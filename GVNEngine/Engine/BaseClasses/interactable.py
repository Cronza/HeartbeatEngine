import pygame

from Engine.Utilities.data_classes import State
from Engine.BaseClasses.renderable_sprite import SpriteRenderable

class Interactable(SpriteRenderable):
    def __init__(self, scene, data_path, pos, center_align=False, z_order=0, initial_rescale=False):
        super().__init__(scene, data_path, pos, center_align, z_order, initial_rescale)

        self.state = State.normal

        # Track whether the previous input frame was clicking to determine whether this interactable was clicked
        self.isClicking = False

        # Interactable state surfaces
        self.hover_surface = None
        self.clicked_surface = None
        self.scaled_hover_surface = None
        self.scaled_clicked_surface = None
        self.LoadStateSprites()

        # Due to interactables being functionally capable of overriding the active surface (Hover, clicked, etc), we
        # need a place to cache the original, unscaled surface so we don't have to reload it from scratch each time
        self.original_surface = self.surface
        self.scaled_original_surface = None

        # Defer the resize until we're able to define the interactive surfaces
        self.RecalculateSize(self.scene.resolution_multiplier)

    def update(self, *args):
        super().update()

        # If being hovered...
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            # If not already in the hover state...
            if self.state is State.normal:
                self.SetActiveSurface(self.GetStateSurface(State.hover))
                self.state = State.hover
                self.scene.Draw()
            else:  # Track whether the user has released their cursor over the sprite
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
            self.SetActiveSurface(self.GetStateSurface(State.normal))
            self.state = State.normal
            self.scene.Draw()

    def RecalculateSize(self, multiplier):
        # Call the parent function to recalculate the base surface
        super().RecalculateSize(multiplier)

        if self.scaled_surface:
            self.scaled_original_surface = self.scaled_surface
        else:
            self.scaled_original_surface = None

        # Recalculate each of the interactable states
        if multiplier == 1:
            self.hover_surface = self.RecalculateSurfaceSize(multiplier, self.hover_surface)
            self.clicked_surface = self.RecalculateSurfaceSize(multiplier, self.clicked_surface)
            self.scaled_hover_surface = None
            self.scaled_clicked_surface = None
        else:
            print("Resizing State Surfaces")
            self.scaled_hover_surface = self.RecalculateSurfaceSize(multiplier, self.hover_surface)
            self.scaled_clicked_surface = self.RecalculateSurfaceSize(multiplier, self.clicked_surface)

    def Interact(self):
        # Check if any actions are defined in the data file
        if 'action' in self.renderable_data:
            self.scene.a_manager.PerformAction(self.renderable_data['action'])
        else:
            print("No actions defined for this object - Clicking does nothing")

    def LoadStateSprites(self):
        """
        Load each of the state sprites in. This is arguably faster than loading them only when necessary, especially
        due to the speed at which they are requested when the user spams the hover or click events
        """
        state_missing_warning = " - Defaulting the state to use the 'Normal' sprite"

        if 'sprite_hover' in self.renderable_data:
            if self.renderable_data['sprite_hover'] != "":
                self.hover_surface = pygame.image.load(self.renderable_data['sprite_hover']).convert_alpha()
            else:
                print("No hover sprite specified" + state_missing_warning)
                self.hover_surface = self.surface
        else:
            print("No hover sprite specified" + state_missing_warning)
            self.hover_surface = self.surface

        if 'sprite_clicked' in self.renderable_data:
            if self.renderable_data['sprite_clicked'] != "":
                self.clicked_surface = pygame.image.load(self.renderable_data['sprite_clicked']).convert_alpha()
            else:
                print("No clicked sprite specified" + state_missing_warning)
                self.clicked_surface = self.surface
        else:
            print("No clicked sprite specified" + state_missing_warning)
            self.clicked_surface = self.surface

    def GetStateSurface(self, state):
        """ Based on the provided state, return the corresponding surface (Either scaled of unscaled) """
        if state == State.hover:
            if self.scaled_hover_surface:
                print("Scaled Hover Surface")
                return self.scaled_hover_surface
            else:
                print("Non-Scaled Hover Surface")
                return self.hover_surface
        elif state == State.pressed:
            if self.scaled_clicked_surface:
                return self.scaled_clicked_surface
            else:
                return self.clicked_surface
        elif state == State.normal:
            if self.scaled_original_surface:
                return self.scaled_original_surface
            else:
                return self.original_surface


    def Flip(self):
        #super().Flip()

        # Completely override the parent, as interactables use a cached original surface instead of explicitly using
        # the active surface

        if self.scaled_original_surface:
            self.scaled_original_surface = self.scene.pygame_lib.transform.flip(self.scaled_original_surface, True, False)
        else:
            self.original_surface = self.scene.pygame_lib.transform.flip(self.original_surface, True, False)

        # Flip the interactive surfaces along with the base surface
        if self.scaled_hover_surface:
            self.scaled_hover_surface = self.scene.pygame_lib.transform.flip(self.scaled_hover_surface, True, False)
        else:
            self.hover_surface = self.scene.pygame_lib.transform.flip(self.hover_surface, True, False)

        if self.scaled_clicked_surface:
            self.scaled_clicked_surface = self.scene.pygame_lib.transform.flip(self.scaled_clicked_surface, True, False)
        else:
            self.clicked_surface = self.scene.pygame_lib.transform.flip(self.clicked_surface, True, False)
