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
DEFAULT_FONT = "Content/Fonts/Comfortaa/Comfortaa-Regular.ttf"


def ConvertPartialToAbsolutePath(partial_path):
    """ Given a partial path, return an absolute path using the editor's root """
    return f"{settings.editor_root}/{partial_path}"


def ResolveFilePath(path: str, fallback_path: str = ""):
    """
    Given a relative file path, return an absolute variant. If 'fallback_path' is provided, load it instead if
    'path' can not be found or is null
    """
    # If the path (assumably) points to the engine, check if the path exists within the engine root
    if path.startswith("HBEngine"):
        full_eng_path = f"{settings.engine_root}{path[len('HBEngine'):]}"
        if Path(full_eng_path).exists():
            return full_eng_path

    # The path is likely relative to the user's project directory
    else:
        if Path(f"{settings.user_project_dir}/{path}").exists():
            return f"{settings.user_project_dir}/{path}"
        else:
            if fallback_path:
                Logger.getInstance().Log(f"File does not Exist: '{path}' - Loading default file: '{fallback_path}'", 3)
                return f"{settings.engine_root}/{fallback_path}"
            else:
                Logger.getInstance().Log(f"File does not Exist: '{path}'", 3)


def ResolveFontFilePath(path: str):
    """ Given a relative font path, return an absolute variant """
    return ResolveFilePath(path, DEFAULT_FONT)
