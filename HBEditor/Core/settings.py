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


class Settings:
    """
    A singleton that holds user project information, editor style settings, and utility functions for navigating
    the project folder structure
    """
    __instance = None

    @staticmethod
    def getInstance():
        """
        Static access method - Used to acquire the singleton instance, or instantiate it if it doesn't already exist
        """
        if Settings.__instance is None:
            Settings()
        return Settings.__instance

    def __init__(self):
        # Enforce the use of the singleton instance
        if Settings.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Settings.__instance = self

        self.root = os.getcwd().replace("\\", "/")
        self.engine_root = f"{self.root}/HBEngine"
        self.editor_root = f"{self.root}/HBEditor"
        self.editor_temp_root = f"{self.editor_root}/Temp"
        self.temp_history_path = f"{self.editor_temp_root}/history.yaml"

        self.project_file = ".heartbeat"
        self.project_folder_structure = [
            "Content",
            "Config"
        ]

        # A dict of files that are provided in new projects. Format: <target_folder>: <source_file>
        self.project_default_files = {
            "Config": "Config/Game.yaml"
        }

        # A dict of types of files, and the individual formats which are supported in the engine / editor
        self.supported_content_types = {
            "Image": "Image Files (*.png *.jpg)",
            "Data": "YAML Files (*.yaml)",
            "Font": "Font Files (*.ttf)",
            "Sound": "Sound Files (*.mp3 *.wav)",
        }

        self.style_data = None
        self.action_database = None

        self.user_project_name = None
        self.user_project_dir = None
        self.user_project_data = None

        self.LoadEditorSettings(f"{self.editor_root}/Config/Editor.yaml")
        self.LoadActionDatabase(f"{self.editor_root}/Config/ActionsDatabase.yaml")

    def GetProjectContentDirectory(self):
        """ Returns the 'Content' folder for the active project """
        return self.user_project_dir + "/" + "Content"

    def GetMetadataString(self, file_type: FileType):
        """ Return the metadata string used to mark HBEditor-exported files """
        return f"# Type: {file_type.name}\n# {self.editor_data['EditorSettings']['version_string']}"

    def LoadProjectSettings(self):
        """ Reads the 'Game.yaml' file for the active project """
        self.user_project_data = Reader.ReadAll(self.user_project_dir + "/" + self.project_default_files['Config'])

    def LoadActionDatabase(self, data_path):
        """ Reads in the 'ActionsDatabase.yaml' file """
        self.action_database = Reader.ReadAll(data_path)

    def LoadEditorSettings(self, data_path):
        """ Reads in the main editor settings """
        self.editor_data = Reader.ReadAll(data_path)

    def ConvertPartialToAbsolutePath(self, partial_path):
        """ Given a parital path, return a absolute path """
        return self.editor_root + "/" + partial_path
