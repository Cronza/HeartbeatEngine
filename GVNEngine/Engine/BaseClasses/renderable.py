import pygame

class Renderable(pygame.sprite.Sprite):
    """
    The Renderable class is the base class for all renderable elements in the GVNEngine. This includes:
        - Sprites
        - Text
        - Motion graphics
        - Etc

    This class is not meant to be used directly, but to be subclassed into more specialized objects
    """
    def __init__(self, scene, pos, center_align = False):
        super().__init__()

        # Renderables require access to the owning scene so that they can keep track of resolution updates
        self.scene = scene

        self.position = pos
        self.surface = None  # The original, unscaled surface
        self.scaled_surface = None  # Used in resolutions different from the main resolution
        self.rect = None

        # Allow renderables to opt out of center aligning (Generally used for things like background sprites, or
        # screen-width sprites
        self.center_align = center_align

        # For indentification in the rendering stack, allow all renderables the ability be to assigned a unique
        # identifier
        self.key = None

        # Control render order
        self.z_order = 0

    def RecalculateSize(self, multiplier):
        """ Based on the provided multiplier, resize the image accordingly """

        # A multiplier of 1 means this is the main resolution. Load the unscaled sprite to avoid continuous scaling
        if multiplier == 1:
            print("Multiplier provided is 1, using unscaled sprite")
            self.scaled_surface = None

            new_position = self.ConvertNormToScreen(tuple(self.position))

            if self.center_align:
                new_position = self.GetCenterOffset(new_position, self.surface.get_size())

            print(new_position)
            self.UpdateRect(new_position, self.surface.get_size())
        else:  # We're using a different resolution. We need to use a scaled version of our surface
            width = self.surface.get_width()
            height = self.surface.get_height()

            # Round each value as blitting doesn't support floats
            new_size = tuple(
                [
                    round(width * multiplier[0]),
                    round(height * multiplier[1])
                ]
            )
            # Generate the scaled surface
            self.scaled_surface = self.scene.pygame_lib.transform.smoothscale(self.surface, new_size)

            new_position = self.ConvertNormToScreen(tuple(self.position))

            if self.center_align:
                new_position = self.GetCenterOffset(new_position, self.scaled_surface.get_size())

            self.UpdateRect(new_position, self.scaled_surface.get_size())

    def GetSurface(self):
        """
        Return either the original, unscaled surface, or the scaled surface depending on the current resolution.
        This returns a copy, so edits make to the returned value won't apply to the original
        """
        if self.scaled_surface:
            return self.scaled_surface
        else:
            return self.surface

    def UpdateRect(self, new_pos, new_size):
        """ Sets the rect location to the provided X and Y"""
        self.rect.x = new_pos[0]
        self.rect.y = new_pos[1]
        self.rect.w = new_size[0]
        self.rect.h = new_size[1]

    def GetActiveSurface(self):
        """
        Return the active surface which is either the unscaled surface based on the main resolution,
        or a scaled surface based on the current resolution
        """
        if self.scaled_surface:
            return self.scaled_surface
        else:
            return self.surface

    def ConvertNormToScreen(self, norm_value):
        """ Take the normalized object pos and convert it to relative screen space coordinates """
        screen_size = self.scene.pygame_lib.display.get_surface().get_size()

        return (
            norm_value[0] * screen_size[0],
            norm_value[1] * screen_size[1]
        )

    def GetCenterOffset(self, pos, size):
        """
        Given size and position tuples representing the center point of a sprite,
        return the offset position for the top-left corner
        """
        
        return (
            round(pos[0] - size[0] / 2),
            round(pos[1] - size[1] / 2)
        )

    # ***************** TRANSFORM ACTIONS *******************
    def Flip(self):
        """ Flips the sprite horizontally. Chooses between the unscaled and scaled surface """
        if self.scaled_surface:
            self.scaled_surface = self.scene.pygame_lib.transform.flip(self.scaled_surface, True, False)
        else:
            self.surface = self.scene.pygame_lib.transform.flip(self.surface, True, False)