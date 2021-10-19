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
from enum import Enum


class FileType(Enum):
    Scene_Dialogue = 1
    Project_Settings = 2
    #Scene_Point_And_Click = 2
    #Character = 3
    #Project_Settings = 4


class FileTypeDescriptions:
    descriptions = {
        FileType.Scene_Dialogue: "A scene containing a sequence of dialogue between characters. "
                                 "These files may contain additional branches"#,

        #FileType.Scene_Point_And_Click: "A scene with interactable objects. Perfect for designing "
        #                                "Point & Click scenes, or interactive maps",

        #FileType.Character: "A file containing details on a character, such as a special font for "
        #                    "their name, their unique color, or various sprites representing their moods"
    }
