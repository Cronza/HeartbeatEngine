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
import pygame.freetype
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core import settings

class TextRenderable(Renderable):
    """
    The Text Renderable class is the base class for renderable text elements in the HBEngine. This includes:
        - Titles
        - Sub-titles
        - Actions text
        - Pop-up text
        - etc
    """
    def __init__(self, scene, renderable_data: dict, parent: Renderable = None):
        super().__init__(scene, renderable_data, parent)

        font = settings.ConvertPartialToAbsolutePath(self.renderable_data['font'])
        self.text = self.renderable_data["text"]
        self.text_color = self.renderable_data["text_color"]
        text_size = self.renderable_data["text_size"]
        self.font_obj = pygame.font.Font(font, text_size)

        if "wrap_bounds" not in self.renderable_data:
            raise ValueError(f"No 'wrap_bounds' value assigned to '{self}' - This makes for an impossible action!")

        # Build a surface using the wrap bounds as the containing area. The values are expected to be normalized so that
        # we avoid resolution-dependent positioning (IE. 0.2 works for 16/9 and 4/3)
        #
        # If text spills outside these bounds, it's automatically wrapped until the maximum Y
        size = self.ConvertNormToScreen(self.renderable_data["wrap_bounds"])
        self.surface = pygame.Surface(
            (
                int(size[0]),
                int(size[1])
            ),
            pygame.SRCALPHA
        )
        self.rect = self.surface.get_rect()

        # For new objects, resize initially in case we're already using a scaled resolution
        self.RecalculateSize(self.scene.resolution_multiplier)
        self.WrapText()

    def WrapText(self):
        """ Clears the surface and redraws / re-wraps the text """
        # Reset the surface, undoing any previous blitting
        self.surface.fill((0,0,0,0))

        rect = self.surface.get_rect()
        base_top = rect.top
        line_spacing = -2
        font_height = self.font_obj.size("Tg")[1]

        # Pre-split the text based on any specified newlines
        text_to_process = self.text.split("\n")

        if self.center_align:
            num_of_lines = len(text_to_process)
            if num_of_lines < 2:
                num_of_lines = 2

            # Vertically center the text
            base_top += (self.surface.get_size()[1] / num_of_lines) - (font_height / 2)

        # Process each line, applying wrapping where necessary
        for line in text_to_process:

            processing_complete = False
            while not processing_complete:
                i = 1

                # Determine if the text will exceed the bounds height
                if base_top + font_height > rect.bottom:
                    break

                # Parse the text until we've exceeded horizontal bounds, or we reached the end of the string
                while self.font_obj.size(line[:i])[0] < rect.width and i < len(line):
                    i += 1

                # If we didn't reach the end of the string, grab the last occurrence of a whitespace
                if i < len(line):
                    i = line.rfind(" ", 0, i) + 1

                # Render the line and blit it to the surface
                image = self.font_obj.render(line[:i], True, self.text_color)

                # If applicable, center align the line based on its unique size
                if self.center_align:
                    extra_space = self.surface.get_size()[0] - image.get_size()[0]
                    centered_width = rect.left + extra_space / 2
                    self.surface.blit(image, (centered_width, base_top))
                else:
                    self.surface.blit(image, (rect.left, base_top))

                base_top += font_height + line_spacing

                # Remove the text we just blitted
                line = line[i:]

                # Exit if we're finished processing everything in this line
                if not line:
                    processing_complete = True


