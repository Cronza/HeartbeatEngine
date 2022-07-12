"""
    The Heartbeat Engine is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The Heartbeat Engine is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with the Heartbeat Engine. If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations
from typing import Union
import pygame


class Renderable(pygame.sprite.Sprite):
    """
    The Renderable class is the base class for all renderable elements in the HBEngine. This includes:
        - Sprites
        - Text
        - Motion graphics
        - Etc

    This class is not meant to be used directly, but to be subclassed into more specialized objects
    """
    def __init__(self, scene, renderable_data: dict, parent: Renderable = None):
        super().__init__()

        # Renderables require access to the owning scene so that they can keep track of resolution updates
        self.scene = scene

        self.rect = None
        self.visible = True  # Allow objects to skip the draw step, but remain in the render stack
        self.surface = None  # The active surface
        self.scaled_surface = None  # The active surface used in resolutions different from the main resolution

        # YAML Parameters
        self.renderable_data = renderable_data
        self.position = self.renderable_data['position']
        self.center_align = self.renderable_data['center_align']
        self.z_order = self.renderable_data['z_order']

        # For indentification in the rendering stack, allow all renderables the ability be to assigned
        # a unique identifier. This parameter is mandatory, and is considered an exception if not provided
        if 'key' not in self.renderable_data:
            raise ValueError(f"No key assigned to {self}. The 'key' property is mandatory for all renderables")

        self.key = self.renderable_data['key']

        self.parent = parent
        self.children = []

    def RecalculateSize(self, multiplier):
        """ Resize the renderable and its surfaces based on the provided size multiplier """

        # Renderables can only have one rect which is based on the base surface. Any sprite changes won't alter the rect
        if multiplier == 1:
            self.scaled_surface = None
            self.UpdateRect(self.RecalculateSurfacePosition(self.surface), self.surface.get_size())
        else:
            self.scaled_surface = self.GetRescaledSurface(multiplier, self.surface)
            self.UpdateRect(self.RecalculateSurfacePosition(self.scaled_surface), self.scaled_surface.get_size())

    def RecalculateSurfacePosition(self, surface: pygame.Surface) -> tuple:
        new_position = 0,0
        if self.parent:
            # Since normalized values can be viewed as a percentage of a range (IE. 0.7 = 70/100),
            # use this to get our position in the parent's coordinate system by multiplying our parent's size
            # by our position (Ex. Size of 50 * 0.5 = 25, or center), then adding this to the parent's position
            new_position = (
                (self.parent.rect.width * self.position[0]) + self.parent.rect.x,
                (self.parent.rect.height * self.position[1]) + self.parent.rect.y
            )
        else:
            new_position = self.ConvertNormToScreen(tuple(self.position))

        # Offset the position so the origin point is in the center
        if self.center_align:
            new_position = self.GetCenterOffset(new_position, surface.get_size())

        return new_position

    def GetRescaledSurface(self, surface: pygame.Surface, multiplier: float) -> pygame.Surface:
        """ Rescale and return the provided surface using the provided multiplier """
        # @TODO Needs a review once resolution support has been updated / fixed
        width = surface.get_width()
        height = surface.get_height()

        # Round each value as blitting doesn't support floats
        new_size = tuple(
            [
                round(width * multiplier[0]),
                round(height * multiplier[1])
            ]
        )
        # Generate the scaled surface
        scaled_surface = pygame.transform.smoothscale(surface, new_size)

        return scaled_surface

    def GetSurface(self):
        """
        Return either the original, unscaled surface, or the scaled surface depending on the current resolution.
        This returns a copy, so edits make to the returned value won't apply to the original
        """
        if self.scaled_surface:
            return self.scaled_surface
        else:
            return self.surface

    def UpdateRect(self, new_pos: tuple, new_size: tuple):
        """ Updates this renderable's rect position and size using the provided values """
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

    def SetActiveSurface(self, surface):
        """ Updates the active surface using the provided surface """
        if self.scaled_surface:
            self.scaled_surface = surface
        else:
            self.surface = surface

    def ConvertNormToScreen(self, norm_value: tuple) -> tuple:
        """ Take the normalized pos and convert it to absolute screen space coordinates """
        screen_size = pygame.display.get_surface().get_size()

        return (
            norm_value[0] * screen_size[0],
            norm_value[1] * screen_size[1]
        )

    def ConvertScreenToNorm(self, screen_val: tuple) -> tuple:
        """ Take the screen space position and normalize it to 0-1 """
        screen_size = pygame.display.get_surface().get_size()

        return (
            screen_val[0] / screen_size[0],
            screen_val[1] / screen_size[1]
        )

    def GetCenterOffset(self, pos, size):
        """
        Given size and position tuples representing the center point of a surface,
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
            self.scaled_surface = pygame.transform.flip(self.scaled_surface, True, False)
        else:
            self.surface = pygame.transform.flip(self.surface, True, False)

