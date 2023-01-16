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
from PyQt5 import QtGui
from HBEditor.Core.DataTypes.file_types import FileType
from Tools.HBYaml.hb_yaml import Reader, Writer


def GetProjectContentDirectory():
    """ Returns the 'Content' folder for the active project """
    global user_project_dir
    return f"{user_project_dir}/Content"


def GetMetadataString(file_type: FileType = None):
    """ Return the metadata string used to mark HBEditor-authored files """
    global editor_data
    metadata_str = f"# {editor_data['EditorSettings']['version_string']}"

    if file_type:
        metadata_str = f"# Type: {file_type.name}\n{metadata_str}"

    return metadata_str


def LoadProjectSettings():
    """ Reads the 'Game.yaml' file for the active project """
    global user_project_dir
    global user_project_data
    global project_default_files
    user_project_data = Reader.ReadAll(user_project_dir + "/" + project_default_files['Config'])


def ConvertPartialToAbsolutePath(partial_path):
    """ Given a partial path, return an absolute path using the editor's root """
    global editor_root
    return editor_root + "/" + partial_path


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

    SaveHeartbeatFile(asset_registry)

def RegisterAssetFolder(path_to_create: str):
    """ Registers the provided folder path. This must be a partial path with the content directory as the root """
    global asset_registry
    split_path = path_to_create.split("/")
    cur_depth = asset_registry
    for folder in split_path:
        if folder not in cur_depth:
            cur_depth[folder] = {}

        cur_depth = cur_depth[folder]

    SaveHeartbeatFile(asset_registry)


def DeregisterAsset(parent_path: str, asset_name: str):
    """
    Removes the registration for 'asset_name' at the provided directory. 'parent_path' must be a partial path with
    the content directory as the root
    """
    global asset_registry
    split_path = parent_path.split("/")
    cur_depth = asset_registry
    for folder in split_path:
        cur_depth = cur_depth[folder]
        if asset_name in cur_depth:
            break

    del cur_depth[asset_name]

    SaveHeartbeatFile(asset_registry)


def DuplicateAssetRegistration(path_to_clone: str, asset_name: str, new_name: str):
    """
    Duplicates the registration for 'asset_name', registering it under 'new_name'. 'path_to_clone' must be a partial path
    with the content directory as the root
    """
    global asset_registry
    split_path = path_to_clone.split("/")
    cur_depth = asset_registry
    clone_source = None
    for folder in split_path:
        cur_depth = cur_depth[folder]
        if asset_name in cur_depth:
            clone_source = cur_depth[asset_name]
            break

    cur_depth[new_name] = clone_source

    SaveHeartbeatFile(asset_registry)


def RenameAssetRegistration(path_to_clone: str, asset_name: str, new_name: str):
    """ Reregister the provided project path using the new name, removing the registration under the old name """
    global asset_registry
    split_path = path_to_clone.split("/")
    cur_depth = asset_registry
    clone_source = None
    for folder in split_path:
        cur_depth = cur_depth[folder]
        if asset_name in cur_depth:
            clone_source = cur_depth[asset_name]
            break

    del cur_depth[asset_name]
    cur_depth[new_name] = clone_source

    SaveHeartbeatFile(asset_registry)


def MoveAssetRegistration(source_path: str, asset_name: str, target_path: str):
    """
    Moves the registration for 'asset_name' 'from 'source_path' to 'target_path'. Paths must be a partial path with
    the content directory as the root
    """
    global asset_registry

    # Find the source data and cache it before removing it
    split_path = source_path.split("/")
    cur_depth = asset_registry
    source_data = None
    for folder in split_path:
        cur_depth = cur_depth[folder]
        if asset_name in cur_depth:
            source_data = cur_depth[asset_name]
            break
    del cur_depth[asset_name]

    # Find the target directory, and create a new registration there
    split_path = target_path.split("/")
    cur_depth = asset_registry
    for folder in split_path:
        cur_depth = cur_depth[folder]

    cur_depth[asset_name] = source_data

    SaveHeartbeatFile(asset_registry)


def GetAssetRegistryFolder(project_path: str) -> dict:
    """ Returns the asset registry data for the provided project path """
    global asset_registry
    split_path = project_path.split("/")

    cur_depth = asset_registry
    for folder in split_path:
        cur_depth = cur_depth[folder]

    return cur_depth


def LoadHeartbeatFile():
    """ Read in the active project's .heartbeat file, updating the asset registry using what is found"""
    global asset_registry
    global user_project_dir
    global heartbeat_file

    asset_registry = Reader.ReadAll(f"{user_project_dir}/{heartbeat_file}")


def SaveHeartbeatFile(data: dict):
    """ Save the heartbeat file that contains asset registrations for Heartbeat projects """
    Writer.WriteFile(data, f"{user_project_dir}/{heartbeat_file}", GetMetadataString())


root = os.getcwd().replace("\\", "/")
engine_root = f"{root}/HBEngine"
editor_root = f"{root}/HBEditor"
editor_temp_root = f"{editor_root}/Temp"
temp_history_path = f"{editor_temp_root}/history.yaml"

heartbeat_file = ".heartbeat"
project_folder_structure = [
    "Content",
    "Config"
]

# A dict of files that are provided in new projects. Format: <target_folder>: <source_file>
project_default_files = {
    "Config": "Config/Game.yaml"
}

# The master dict of file types supported by the engine / editor
supported_file_types = {
    ".png": FileType.Asset_Image,
    ".jpg": FileType.Asset_Image,
    ".yaml": FileType.Asset_Data,
    ".ttf": FileType.Asset_Font,
    ".mp3": FileType.Asset_Sound,
    ".wav": FileType.Asset_Sound,
    ".ogg": FileType.Asset_Sound,
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

editor_data = Reader.ReadAll(f"{editor_root}/Config/Editor.yaml")  # Contains data relating to how the editor functions
editor_action_metadata = Reader.ReadAll(f"{editor_root}/Config/Actions.yaml")  # Contains data that categorizes engine actions, and defines which editors can use which actions
action_metadata = Reader.ReadAll(f"{engine_root}/Core/Actions/actions_metadata.yaml")  # Contains data relating to how engine actions operate, including additional editor-specific values for how they appear in the editor

asset_registry = {}  # Loaded when project is loaded
engine_asset_registry = Reader.ReadAll(f"{engine_root}/Config/EngineAssetRegistry.yaml")

