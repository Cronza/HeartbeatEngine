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
from io import BytesIO
from PIL import ImageFont
from PyQt5 import QtGui, QtCore
from HBEditor.Core.Logger.logger import Logger


class FontManager:

    @staticmethod
    def LoadCustomFont(file_path):
        """
        Loads and creates a font using the provided file path (either absolute, or a Qt resource path),
        applying any style used by that font
        """
        if file_path.startswith(":/") or os.path.exists(file_path) and not os.path.isdir(file_path):
            QtGui.QFontDatabase.addApplicationFont(file_path)

            font_file = QtCore.QFile(file_path)
            if font_file.open(QtCore.QFile.ReadOnly):
                # 1:
                # 'QFontDatabase.addApplicationFont' doesn't return anything that would give us information on
                #  what type of style the loaded font used (Bold, Italic, etc). All we get is an (int) ID
                # that lets us access the family name. This is only half of what we need.
                #
                # In order to get the style, we're using a font lib to get it directly from the file

                # 2:
                # Only Qt can understand data stored by the resource system. Attempting to load a font resource with PIL
                # leads to an exception. Instead of passing PIL the file path (which it can't read), pass it the file's
                # data in byte form instead
                byte_data = BytesIO(font_file.readAll())
                name, style = ImageFont.truetype(byte_data).getname()
                new_font = QtGui.QFont(name)

                # Apply any style used by the loaded font
                FontManager.ApplyStyle(style, new_font)

                font_file.close()
                return new_font
            else:
                print(font_file.errorString())
                return None


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

    @staticmethod
    def ReadAsBytes(font_qfile):
        return BytesIO(font_qfile.readAll())()
