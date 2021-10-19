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
from HBEngine.Core.BaseClasses.renderable import Renderable


class TextRenderable(Renderable):
    """
    The Text Renderable class is the base class for renderable text elements in the HBEngine. This includes:
        - Titles
        - Sub-titles
        - Actions text
        - Pop-up text
        - etc
    """
    def __init__(self, scene, renderable_data):
        super().__init__(scene, renderable_data)

        font = self.scene.settings.ConvertPartialToAbsolutePath(self.renderable_data['font'])
        self.text = self.renderable_data['text']
        text_size = self.renderable_data['text_size']
        text_color = self.renderable_data['text_color']

        self.font_obj = pygame.font.Font(font, text_size)
        self.surface = self.font_obj.render(self.text, True, text_color)
        self.rect = self.surface.get_rect()

        # For new objects, resize initially in case we're already using a scaled resolution
        self.RecalculateSize(self.scene.resolution_multiplier)


