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
import pygame
from HBEngine.Core import settings
from HBEngine.Core.Objects.renderable import Renderable


class SpriteRenderable(Renderable):
    """
    The Sprite Renderable class is the base class for renderable sprite elements in the HBEngine. This includes:
        - Interactables
        - Non-Interactables
        - Backgrounds
        - etc
    """
    def __init__(self, renderable_data: dict, initial_rescale: bool = True, parent: Renderable = None,
                 use_placeholder: bool = True):
        super().__init__(renderable_data, parent)

        if "sprite" in self.renderable_data:
            if self.renderable_data['sprite'] != "None" and self.renderable_data['sprite'] != "":
                sprite = settings.ConvertPartialToAbsolutePath(self.renderable_data['sprite'])

                try:
                    self.surface = pygame.image.load(sprite).convert_alpha()
                    self.rect = self.surface.get_rect()
                except Exception as exc:
                    raise ValueError(f"Failed to load sprite: '{sprite}' - Either the file was not found, or it is not a "
                          f"supported file type\n Exception: {exc}") from None  # PEP 409: Suppressing exception context

                # For new objects, resize initially in case we're already using a scaled resolution. Allow descendents
                # to defer this though if they need to do any additional work beforehand
                if initial_rescale:
                    self.RecalculateSize(settings.resolution_multiplier)


