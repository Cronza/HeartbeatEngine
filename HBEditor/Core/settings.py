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
from Tools.HBYaml.hb_yaml import Reader


def GetProjectContentDirectory():
    """ Returns the 'Content' folder for the active project """
    global user_project_dir
    return user_project_dir + "/" + "Content"


def GetMetadataString(file_type: FileType):
    """ Return the metadata string used to mark HBEditor-exported files """
    global editor_data
    return f"# Type: {file_type.name}\n# {editor_data['EditorSettings']['version_string']}"


def LoadProjectSettings():
    """ Reads the 'Game.yaml' file for the active project """
    global user_project_dir
    global user_project_data
    global project_default_files
    user_project_data = Reader.ReadAll(user_project_dir + "/" + project_default_files['Config'])


def ConvertPartialToAbsolutePath(self, partial_path):
    """ Given a partial path, return an absolute path using the editor's root """
    global editor_root
    return editor_root + "/" + partial_path


root = os.getcwd().replace("\\", "/")
engine_root = f"{root}/HBEngine"
editor_root = f"{root}/HBEditor"
editor_temp_root = f"{editor_root}/Temp"
temp_history_path = f"{editor_temp_root}/history.yaml"

project_file = ".heartbeat"
project_folder_structure = [
    "Content",
    "Config"
]

# A dict of files that are provided in new projects. Format: <target_folder>: <source_file>
project_default_files = {
    "Config": "Config/Game.yaml"
}

# A dict of types of files, and the individual formats which are supported in the engine / editor
supported_content_types = {
    "Image": "Image Files (*.png *.jpg)",
    "Data": "YAML Files (*.yaml)",
    "Font": "Font Files (*.ttf)",
    "Sound": "Sound Files (*.mp3 *.wav)",
}

user_project_name = None
user_project_dir = None
user_project_data = None  # The contents of the project's 'Game.yaml' file

editor_data = Reader.ReadAll(f"{editor_root}/Config/Editor.yaml")  # Contains data relating to how the editor functions
editor_action_metadata = Reader.ReadAll(f"{editor_root}/Config/Actions.yaml")  # Contains data that categorizes engine actions, and defines which editors can use which actions
action_metadata = Reader.ReadAll(f"{engine_root}/Core/Actions/actions_metadata.yaml")  # Contains data relating to how engine actions operate, including additional editor-specific values for how they appear in the editor

