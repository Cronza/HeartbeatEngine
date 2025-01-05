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
from Tools.HBYaml.CustomTags.connection import Connection


class SpriteRenderable(Renderable):
    """
    The Sprite Renderable class is the base class for renderable sprite elements in the HBEngine. This includes:
        - Interactables
        - Non-Interactables
        - Backgrounds
        - etc

    This class has the following (additional) Renderable Data requirements:
    - sprite (String)
    """
    def __init__(self, renderable_data: dict, parent: Renderable = None, process_data: bool = True):
        # Parameters
        self.sprite = ""

        # Run parent implementation which will perform recalculations with the aforementioned parameters
        super().__init__(renderable_data, parent, process_data)

    def ApplyRenderableData(self):
        if "sprite" in self.renderable_data:
            if self.renderable_data['sprite'] != "None" and self.renderable_data['sprite'] != "":
                if isinstance(self.renderable_data['sprite'], Connection):
                    self.sprite = settings.ConvertPartialToAbsolutePath(settings.GetConnectionData(self.renderable_data['sprite']))
                    self.RegisterConnectionListener(self.renderable_data['sprite'])
                else:
                    self.sprite = settings.ConvertPartialToAbsolutePath(self.renderable_data['sprite'])

                # Attempt to load the sprite
                try:
                    self.surface = pygame.image.load(self.sprite).convert_alpha()
                    self.rect = self.surface.get_rect()
                except Exception as exc:
                    raise ValueError(f"Failed to load sprite: '{self.sprite}' - Either the file was not found, or it is not a "
                                     f"supported file type\n Exception: {exc}") from None  # PEP 409: Suppressing exception context

        # Run the parent implementation to ensure all changes are considered, and the surfaces are recalculated
        super().ApplyRenderableData()
