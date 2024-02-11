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
    Folder = 1
    Project_Settings = 2
    Values = 3
    Interface = 4
    Dialogue = 5
    Scene = 6
    Asset_Data = 7
    Asset_Image = 8
    Asset_Font = 9
    Asset_Sound = 10
    #Character = 3


class FileTypeIcons:
    icons = {
        FileType.Folder: "EditorContent:Icons/Folder.png",
        FileType.Interface: "EditorContent:Icons/Interface.png",
        FileType.Project_Settings: "EditorContent:Icons/File.png",
        FileType.Dialogue: "EditorContent:Icons/File.png",
        FileType.Scene: "EditorContent:Icons/File.png",
        FileType.Asset_Data: "EditorContent:Icons/File.png",
        FileType.Asset_Image: "EditorContent:Icons/File_Image.png",
        FileType.Asset_Font: "EditorContent:Icons/File.png",
        FileType.Asset_Sound: "EditorContent:Icons/File.png"
    }
