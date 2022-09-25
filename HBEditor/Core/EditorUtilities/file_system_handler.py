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
from pathlib import Path
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core import settings


# Default files that live in the engine content directory and are available to all projects
DEFAULT_SPRITE = "Content/Sprites/Placeholder.png"
DEFAULT_FONT = "Content/Fonts/Comfortaa/Comfortaa-Regular.ttf"


def ResolveFilePath(path: str, default_path: str):
    """ Given a relative image path, return an absolute variant """
    # If the user provided a null path, return the default sprite
    if path == "" or path.lower() == "none":
        Logger.getInstance().Log(f"No path provided - Loading default file: '{default_path}'", 3)
        return f"{settings.engine_root}/{default_path}"

    # If the path (assumably) points to the engine, check if the path exists within the engine root
    elif path.startswith("HBEngine"):
        full_eng_path = f"{settings.engine_root}/{Path(path.replace('HBEngine', '', 1))}"
        if Path(full_eng_path).exists():
            return full_eng_path

    # The path is likely relative to the user's project directory
    else:
        if Path(f"{settings.user_project_dir}/{path}").exists():
            return f"{settings.user_project_dir}/{path}"
        else:
            Logger.getInstance().Log(f"File does not Exist: '{path}' - Loading default file: '{default_path}'", 3)
            return f"{settings.engine_root}/{default_path}"

def ResolveImageFilePath(path: str,):
    """ Given a relative image path, return an absolute variant """
    return ResolveFilePath(path, DEFAULT_SPRITE)

def ResolveFontFilePath(path: str):
    """ Given a relative font path, return an absolute variant """
    return ResolveFilePath(path, DEFAULT_FONT)
