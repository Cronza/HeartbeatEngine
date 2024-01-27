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
import inspect
import copy
from PyQt6 import QtGui
from HBEditor.Core.DataTypes.file_types import FileType
from HBEngine.Core.Actions import actions
from Tools.HBYaml.hb_yaml import Reader, Writer


def GetProjectContentDirectory():
    """ Returns the 'Content' folder for the active project """
    global user_project_dir
    return f"{user_project_dir}/Content"


def GetMetadataString():
    """ Return the metadata string used to mark HBEditor-authored files """
    global editor_data
    metadata_str = f"# {editor_data['EditorSettings']['version_string']}"

    return metadata_str


def GetProjectSettingsPath() -> str:
    """ Returns the absolute path to the active project's 'Game.yaml' file """
    global user_project_dir
    return user_project_dir + "/" + 'Config/Game.yaml'


def GetValuesPath() -> str:
    """ Returns the absolute path to the active project's 'Values.yaml' file """
    global user_project_dir
    return user_project_dir + "/" + 'Config/Values.yaml'


def LoadProjectSettings():
    """ Reads the 'Game.yaml' file for the active project """
    global user_project_dir
    global user_project_data
    global project_default_files
    user_project_data = Reader.ReadAll(GetProjectSettingsPath())


def RegisterAsset(parent_path: str, asset_name: str, asset_type: FileType):
    """
    Registers the provided file. 'parent_path' must be a partial path with the content directory as the root
    """
    global asset_registry
    split_path = parent_path.split("/")
    cur_depth = asset_registry
    for folder in split_path:
        cur_depth = cur_depth[folder]

    cur_depth[asset_name] = asset_type.name

    SortRegistry(cur_depth)
    SaveHeartbeatFile(asset_registry)


def RegisterAssetFolder(path_to_create: str):
    """ Registers the provided folder path. This must be a partial path with the content directory as the root """
    global asset_registry
    split_path = path_to_create.split("/")
    cur_depth = asset_registry
    for folder in split_path:
        if folder not in cur_depth:
            cur_depth[folder] = {}
        else:
            cur_depth = cur_depth[folder]

    SortRegistry(cur_depth)
    SaveHeartbeatFile(asset_registry)


def DeregisterAsset(source_file_path: str, asset_name: str):
    """
    Removes the registration for 'asset_name' at the provided directory. 'parent_path' must be a partial path with
    the content directory as the root
    """
    global asset_registry
    split_path = os.path.dirname(source_file_path).split("/")
    cur_depth = asset_registry
    for folder in split_path:
        cur_depth = cur_depth[folder]

    if asset_name in cur_depth:
        del cur_depth[asset_name]

    SortRegistry(cur_depth)
    SaveHeartbeatFile(asset_registry)


def DuplicateAssetRegistration(source_file_path: str, asset_name: str, new_name: str):
    """
    Duplicates the registration for 'asset_name', registering it under 'new_name'. 'path_to_clone' must be a
    partial path with the content directory as the root
    """
    global asset_registry
    split_path = os.path.dirname(source_file_path).split("/")
    cur_depth = asset_registry
    for folder in split_path:
        cur_depth = cur_depth[folder]

    if asset_name in cur_depth:
        cur_depth[new_name] = cur_depth[asset_name]

    SortRegistry(cur_depth)
    SaveHeartbeatFile(asset_registry)


def RenameAssetRegistration(source_file_path: str, asset_name: str, new_name: str):
    """ Reregister the provided project path using the new name, removing the registration under the old name """
    global asset_registry
    split_path = os.path.dirname(source_file_path).split("/")
    cur_depth = asset_registry
    for folder in split_path:
        cur_depth = cur_depth[folder]

    if asset_name in cur_depth:
        source = cur_depth[asset_name]
        del cur_depth[asset_name]
        cur_depth[new_name] = source

    SortRegistry(cur_depth)
    SaveHeartbeatFile(asset_registry)


def MoveAssetRegistration(source_file_path: str, asset_name: str, target_path: str):
    """
    Moves the registration for 'asset_name' 'from 'source_file_path' to 'target_path'. Paths must be a partial
    path with the content directory as the root
    """
    global asset_registry

    # Find the source data and cache it before removing it
    split_path = os.path.dirname(source_file_path).split("/")
    cur_depth = asset_registry
    for folder in split_path:
        cur_depth = cur_depth[folder]

    # Only perform the move if we can find the source
    if asset_name in cur_depth:
        source_data = cur_depth[asset_name]
        del cur_depth[asset_name]

        # Find the target directory, and create a new registration there
        split_path = target_path.split("/")
        cur_depth = asset_registry
        for folder in split_path:
            cur_depth = cur_depth[folder]
        cur_depth[asset_name] = source_data

    SortRegistry(cur_depth)
    SaveHeartbeatFile(asset_registry)


def GetAssetRegistryFolder(project_path: str) -> dict:
    """ Returns the asset registry data for the provided project path """
    global asset_registry
    split_path = project_path.split("/")

    cur_depth = asset_registry
    for folder in split_path:
        cur_depth = cur_depth[folder]

    return cur_depth


def SortRegistry(registry_data: dict):
    """
    Given Asset Registry data, sort and modify the data in place. This only applies to the top level of the data.
    This does not recurse if given multiple depths
    """
    folders = {}
    assets = {}

    # Split up assets into Folders and Assets so we can apply sorting rules correctly
    for key, value in registry_data.items():
        if isinstance(value, dict):
            folders[key] = value
        else:
            assets[key] = value

    # Sort assets by value first and then by key
    sorted_assets = {key: value for key, value in sorted(assets.items(), key=lambda item: (str(item[1]), item[0]))}

    # Combine folders and assets before updating the passed-in registry dict
    registry_data.clear()
    registry_data.update({**folders, **sorted_assets})



def LoadHeartbeatFile():
    """ Read in the active project's .heartbeat file, updating the asset registry using what is found"""
    global asset_registry
    global user_project_dir
    global heartbeat_file

    asset_registry = Reader.ReadAll(f"{user_project_dir}/{heartbeat_file}")


def SaveHeartbeatFile(data: dict):
    """ Save the heartbeat file that contains asset registrations for Heartbeat projects """
    Writer.WriteFile(data, f"{user_project_dir}/{heartbeat_file}", GetMetadataString())


def GetActionData(action_name: str) -> dict:
    """ Returns a copy of the 'ACTION_DATA' for an engine action that matches the provided name """
    return copy.deepcopy(_engine_actions[action_name].ACTION_DATA)


root = os.getcwd().replace("\\", "/")
engine_root = f"{root}/HBEngine"
editor_root = f"{root}/HBEditor"
editor_temp_root = f"{editor_root}/Temp"
temp_history_path = f"{editor_temp_root}/history.yaml"
thumbnail_root = "Thumbnails"

heartbeat_file = ".heartbeat"
project_folder_structure = [
    "Content",
    "Config"
]

# A list of tuples for files that are provided in new projects. Format: (<target_folder>, <source_file>)
project_default_files = [
    ("Config", "Config/Game.yaml"),
    ("Config", "Config/Values.yaml"),
]

# The master dict of file types supported by the engine / editor
supported_file_types = {
    ".interface": FileType.Interface,
    ".png": FileType.Asset_Image,
    ".jpg": FileType.Asset_Image,
    ".yaml": FileType.Asset_Data,
    ".ttf": FileType.Asset_Font,
    ".mp3": FileType.Asset_Sound,
    ".wav": FileType.Asset_Sound,
    ".ogg": FileType.Asset_Sound
}

# A dict of types of files, and the individual formats which are supported in the engine / editor. This is a
# categorization of 'supported_file_types' used often in file system browsers
supported_file_types_cat = {
    "Image": "Image Files (*.png *.jpg)",
    "Data": "YAML Files (*.yaml)",
    "Font": "Font Files (*.ttf)",
    "Sound": "Sound Files (*.mp3 *.wav *.ogg)",
}

user_project_name = None
user_project_dir = None
user_project_data = None  # The contents of the project's 'Game.yaml' file

asset_registry = {}  # Loaded when project is loaded
engine_asset_registry = Reader.ReadAll(f"{engine_root}/Config/EngineAssetRegistry.yaml")  # Engine files which are accessible via the asset registration system
editor_data = Reader.ReadAll(f"{editor_root}/Config/Editor.yaml")  # Editor function and style settings

# Contains categorized engine actions and definitions for which editors can use which actions
available_actions = Reader.ReadAll(f"{editor_root}/Config/Actions.yaml")

# A list of action classes available in the HBEngine. This is not meant to be accessed outside this file
_engine_actions = dict(inspect.getmembers(actions, lambda obj: inspect.isclass(obj) and obj.__module__ == actions.__name__))
