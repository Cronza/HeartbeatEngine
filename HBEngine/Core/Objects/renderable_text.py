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
from Tools.HBYaml.CustomTags.connection import Connection


class TextRenderable(Renderable):
    """
    The Text Renderable class is the base class for renderable text elements in the HBEngine. This includes:
        - Titles
        - Sub-titles
        - Actions text
        - Pop-up text
        - etc

    This class has the following (additional) Renderable Data requirements:
    - text (String)
    - text_size (Int)
    - text_color (Vector3)
    - font (String)
    - wrap_bounds (Vector2)
    """
    DEFAULT_FONT = "HBEngine/Content/Fonts/Comfortaa/Comfortaa-Regular.ttf"
    def __init__(self, renderable_data: dict, parent: Renderable = None, process_data: bool = True):
        # Parameters
        self.text = ""
        self.text_color = (0, 0, 0)
        self.text_size = 12
        self.font = pygame.font.Font(self.DEFAULT_FONT, self.text_size)
        self.wrap_bounds = (0, 1)

        # Run parent implementation which will perform recalculations with the aforementioned parameters
        super().__init__(renderable_data, parent, process_data)

    def ApplyRenderableData(self):
        if 'text' in self.renderable_data:
            if isinstance(self.renderable_data['text'], Connection):
                self.text = settings.GetConnectionData(self.renderable_data['text'])
                self.RegisterConnectionListener(self.renderable_data['text'])
            else:
                self.text = self.renderable_data['text']

        if 'text_size' in self.renderable_data:
            if isinstance(self.renderable_data['text_size'], Connection):
                self.text_size = settings.GetConnectionData(self.renderable_data['text_size'])
                self.RegisterConnectionListener(self.renderable_data['text_size'])
            else:
                self.text_size = self.renderable_data['text_size']

            # The initial font is loaded during the init function, which is when the starting 'text_size' value is used.
            # Only when 'font' is provided does the font object get regenerated. If 'font' is not passed, then
            # 'text_size' is never used. As such, do a special check here to ensure 'text_size' changes are always used
            if 'font' not in self.renderable_data:
                self.font = pygame.font.Font(self.DEFAULT_FONT, self.text_size)

        if 'text_color' in self.renderable_data:
            if isinstance(self.renderable_data['text_color'], Connection):
                self.text_color = settings.GetConnectionData(self.renderable_data['text_color'])
                self.RegisterConnectionListener(self.renderable_data['text_color'])
            else:
                self.text_color = self.renderable_data['text_color']

        if 'font' in self.renderable_data:
            if isinstance(self.renderable_data['font'], Connection):
                self.font = pygame.font.Font(
                    settings.ConvertPartialToAbsolutePath(settings.GetConnectionData(self.renderable_data['font'])),
                    self.text_size
                )
                self.RegisterConnectionListener(self.renderable_data['font'])
            else:
                self.font = pygame.font.Font(
                    settings.ConvertPartialToAbsolutePath(self.renderable_data['font']),
                    self.text_size
                )

        if 'wrap_bounds' in self.renderable_data:
            if isinstance(self.renderable_data['wrap_bounds'], Connection):
                self.wrap_bounds = settings.GetConnectionData(self.renderable_data['wrap_bounds'])
                self.RegisterConnectionListener(self.renderable_data['wrap_bounds'])
            else:
                self.wrap_bounds = self.renderable_data['wrap_bounds']

        # Run the parent implementation to ensure all changes are considered, and the surfaces are recalculated
        super().ApplyRenderableData()

        # Rebuild the surface
        self.WrapText()
        self.RecalculateSize(settings.resolution_multiplier)

    def WrapText(self):
        """ Clears the surface and redraws / re-wraps the text """
        # Reset the surface back to the full size of wrap_bounds in order to wrap properly
        size = self.ConvertNormToScreen(self.wrap_bounds)
        self.surface = pygame.Surface(
            (
                int(size[0]),
                int(size[1])
            ),
            pygame.SRCALPHA
        )
        rect = self.surface.get_rect()

        base_top = rect.top
        line_spacing = 0
        font_height = self.font.size("Tg")[1]
        largest_width = 0  # The size of the largest line
        total_height = 0  # The height of all lines including between-line spacing

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
                while self.font.size(line[:i])[0] < rect.width and i < len(line):
                    i += 1

                # If we didn't reach the end of the string, grab the last occurrence of a whitespace
                if i < len(line):
                    i = line.rfind(" ", 0, i) + 1

                # Prior to blitting, measure the length of the string and record it if it's the largest so far
                if self.font.size(line[:i])[0] > largest_width:
                    largest_width = self.font.size(line[:i])[0]

                # Render the line and blit it to the surface
                image = self.font.render(line[:i], True, self.text_color)

                # If applicable, center align the line based on its unique size
                if self.center_align:
                    extra_space = self.surface.get_size()[0] - image.get_size()[0]
                    centered_width = rect.left + extra_space / 2
                    self.surface.blit(image, (centered_width, base_top))
                else:
                    self.surface.blit(image, (rect.left, base_top))

                base_top += font_height + line_spacing
                total_height += font_height + line_spacing

                # Remove the text we just blitted
                line = line[i:]

                # Exit if we're finished processing everything in this line
                if not line:
                    processing_complete = True

        # Now that we have the text organized and blitted correctly on the larger wrap_bounds-based surface, we need to
        # trim the excess space between the text and the wrap_bounds (Vertically and horizontally).
        #
        # Note: Remove 'pygame.SRCALPHA' if you want to force the background to be black for visualization / testing
        new_surface = pygame.Surface((largest_width, total_height), pygame.SRCALPHA)
        if self.center_align:
            new_rect = new_surface.blit(self.surface, (0 - (self.surface.get_width() - largest_width) / 2, 0 - (self.surface.get_height() - total_height) / 2))
        else:
            new_rect = new_surface.blit(self.surface, (0, 0))

        self.surface = new_surface
        self.rect = pygame.Rect(self.rect.x, self.rect.y, new_rect.w, new_rect.h)

    #def ConnectionUpdate(self, new_value):
    #    if isinstance(new_value, str):
    #        self.text = new_value
    #        self.WrapText()
    #        self.RecalculateSize(settings.resolution_multiplier)
    #    else:
    #        raise ValueError(f"Connection value is an invalid type. Received '{type(new_value)}' when expecting 'str'")

