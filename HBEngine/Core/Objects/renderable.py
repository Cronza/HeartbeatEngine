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
from HBEngine.Core import settings
from Tools.HBYaml.CustomTags.connection import Connection


class Renderable(pygame.sprite.Sprite):
    """
    The Renderable class is the base class for all renderable elements in the HBEngine. This includes:
        - Sprites
        - Text
        - Motion graphics
        - Etc

    This class has the following Renderable Data requirements:
    - key (String)
    - position (Tuple)
    - center_align (Boolean)
    - z_order (Float)
    - flip (Boolean)
    """
    def __init__(self, renderable_data: dict, parent: Renderable = None, process_data: bool = True):
        super().__init__()
        self.parent = parent
        self.children = []

        self.connected = False  # Control whether state is determined by an external source

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.visible = True  # Allow objects to skip the draw step, but remain in the render stack
        self.surface = pygame.Surface((0, 0), pygame.SRCALPHA)  # The active surface
        self.scaled_surface = None  # The active surface used in resolutions different from the main resolution

        # Parameters
        self.renderable_data = renderable_data
        self.key = ''
        self.position = (0, 0)
        self.center_align = True
        self.z_order = 0
        self.flip = False

        if process_data:
            self.ApplyRenderableData()

    def Destroy(self):
        """ Recursively remove all references to children to allow for GC for this object """
        for child in self.children:
            child.Destroy()

        self.children.clear()
        self.parent = None
        settings.scene.active_renderables.Remove(self.key)

    def ApplyRenderableData(self):
        # Since parameters may either be of the associated type or a 'Connection' type, we need to check whether any
        # parameter is a connection. If so, load the associated connected value

        # For identification in the rendering stack, all renderables require a unique identifier
        if 'key' in self.renderable_data:
            if isinstance(self.renderable_data['key'], Connection):
                self.key = settings.GetConnectionData(self.renderable_data['key'])
            else:
                self.key = self.renderable_data['key']
        else:
            raise ValueError(f"No key assigned to {self}. The 'key' property is mandatory for all renderables")

        if "position" in self.renderable_data:
            if isinstance(self.renderable_data['position'], Connection):
                self.position = settings.GetConnectionData(self.renderable_data['position'])
            else:
                self.position = self.renderable_data['position']

        if "center_align" in self.renderable_data:
            if isinstance(self.renderable_data['center_align'], Connection):
                self.center_align = settings.GetConnectionData(self.renderable_data['center_align'])
            else:
                self.center_align = self.renderable_data['center_align']

        if "z_order" in self.renderable_data:
            if isinstance(self.renderable_data['z_order'], Connection):
                self.z_order = settings.GetConnectionData(self.renderable_data['z_order'])
            else:
                self.z_order = self.renderable_data['z_order']

        # Recalculate the surface given the above changes before we consider transformational changes
        self.RecalculateSize(settings.resolution_multiplier)

        if "flip" in self.renderable_data:
            if isinstance(self.renderable_data['flip'], Connection):
                self.flip = settings.GetConnectionData(self.renderable_data['flip'])
            else:
                self.flip = self.renderable_data['flip']

            self.Flip()

    def RecalculateSize(self, multiplier):
        """ Resize the renderable and its surfaces based on the provided size multiplier """

        # Renderables can only have one rect which is based on the base surface. Any sprite changes won't alter the rect
        if multiplier == 1:
            self.scaled_surface = None
            self.UpdateRect(self.RecalculateSurfacePosition(self.surface), self.surface.get_size())
        else:
            self.scaled_surface = self.GetRescaledSurface(self.surface, multiplier)
            self.UpdateRect(self.RecalculateSurfacePosition(self.scaled_surface), self.scaled_surface.get_size())

    def RecalculateSurfacePosition(self, surface: pygame.Surface) -> tuple:
        new_position = 0,0

        if self.parent:
            # If the parent has a surface but it is unused (IE. 0,0), fallback to screen space
            if self.parent.surface.get_width() == 0 and self.parent.surface.get_height() == 0:
                new_position = self.ConvertNormToScreen(tuple(self.position))
            else:
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

    def ConnectProjectSetting(self, connection_data: dict) -> bool:
        if "category" in connection_data:
            if connection_data["category"] == "":
                return False
        else:
            return False

        if "setting" in connection_data:
            if connection_data["setting"] == "":
                return False
        else:
            return False

        # Add this object as a listener to the connected setting
        if self not in settings.project_setting_listeners[connection_data["category"]][connection_data["setting"]]:
            settings.project_setting_listeners[connection_data["category"]][connection_data["setting"]][self] = self.ConnectionUpdate

        self.connected = True

        # Apply the initial state change
        self.ConnectionUpdate(settings.project_settings[connection_data["category"]][connection_data["setting"]])
        return True

    def ConnectionUpdate(self, new_value):
        pass

    # ***************** TRANSFORM ACTIONS *******************

    def Flip(self):
        """ Flips the sprite horizontally. Chooses between the unscaled and scaled surface """
        if self.scaled_surface:
            self.scaled_surface = pygame.transform.flip(self.scaled_surface, True, False)
        else:
            self.surface = pygame.transform.flip(self.surface, True, False)


