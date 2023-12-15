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
    Interface = 3
    Dialogue = 4
    Scene = 5
    Asset_Data = 6
    Asset_Image = 7
    Asset_Font = 8
    Asset_Sound = 9
    #Character = 3


class FileTypeIcons:
    icons = {
        FileType.Folder: ":/Icons/Folder.png",
        FileType.Interface: ":/Icons/Interface.png",
        FileType.Project_Settings: ":/Icons/File.png",
        FileType.Dialogue: ":/Icons/File.png",
        FileType.Scene: ":/Icons/File.png",
        FileType.Asset_Data: ":/Icons/File.png",
        FileType.Asset_Image: ":/Icons/File_Image.png",
        FileType.Asset_Font: ":/Icons/File.png",
        FileType.Asset_Sound: ":/Icons/File.png"
    }
