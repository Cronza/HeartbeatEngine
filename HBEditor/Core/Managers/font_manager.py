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
import os
from PIL import ImageFont
from PyQt5 import QtGui
from HBEditor.Core.Logger.logger import Logger


class FontManager:

    @staticmethod
    def LoadCustomFont(file_path):
        """ Loads and creates a font using the provided file path, apply any style used by that font """
        if os.path.exists(file_path) and not os.path.isdir(file_path):

            # PyQt5 doesn't allow direct loading of fonts by file path, so we need to go through the FontDatabase system
            QtGui.QFontDatabase.addApplicationFont(file_path)

            # For some insane reason, 'QFontDatabase.addApplicationFont' doesn't return anything that would give you
            # information on what type of style the loaded font used (Bold, Italic, etc). All you get is an (int) ID
            # that lets you access the family name. This is only half of what we need.
            #
            # In order to get the style, we're using a font lib to get it directly from the file
            name, style = ImageFont.truetype(file_path).getname()
            new_font = QtGui.QFont(name)

            # Apply any style used by the loaded font
            FontManager.ApplyStyle(style, new_font)

            return new_font

        else:
            Logger.getInstance().Log(f"File does not Exist: '{file_path}'", 3)
            return None

    @staticmethod
    def LoadFont(name, style=""):
        """ Creates a font using the name of an already loaded family, and a pre-existing style """
        # Does this font exist?
        if QtGui.QFontDatabase().styles(name):
            # Does the provided style exist?
            available_styles = QtGui.QFontDatabase().styles(name)
            if style:
                if style in available_styles:
                    new_font = QtGui.QFont(name)
                    FontManager.ApplyStyle(style, new_font)
                    return new_font
                else:
                    Logger.getInstance().Log(f"Invalid style provided for '{name}'", 3)
                    style = available_styles[0]
                    new_font = QtGui.QFont(name)
                    FontManager.ApplyStyle(style, new_font)
                    return new_font
            else:
                style = available_styles[0]
                Logger.getInstance().Log(f"No style provided for '{name}' - Defaulting to '{style}'", 3)
                new_font = QtGui.QFont(name)
                FontManager.ApplyStyle(style, new_font)
                return new_font
        else:
            return None

    @staticmethod
    def ApplyStyle(style_string: str, font: QtGui.QFont) -> None:
        """ Given a string with style text within it, apply the correlating style to the given font """
        # Based on the style, enable the right style
        # Due to unique cases where certain styles state multiple style (IE. 'Bold Italic' for Arial), do an
        # 'in' check, instead of '=='
        font.setBold("Bold" in style_string)
        font.setItalic("Italic" in style_string)
