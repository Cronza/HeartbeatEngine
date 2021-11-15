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
from HBEditor.Utilities.yaml_manager import Reader
from HBEditor.Utilities.DataTypes.file_types import FileType


class Settings:
    def __init__(self):
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
        self.LoadStyleSettings(f"{self.editor_root}/Config/EditorStyle.yaml")
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

    def LoadStyleSettings(self, data_path):
        """ Load the editor style settings """
        #@TODO: Investigate QPalette use

        self.style_data = Reader.ReadAll(data_path)

        # Text and Font
        self.header_1_font = QtGui.QFont(self.style_data["EditorTextSettings"]["header_1_font"],self.style_data["EditorTextSettings"]["header_1_text_size"],)
        self.header_1_color = f"color: rgb({self.style_data['EditorTextSettings']['header_1_color']})"
        self.header_1_font.setBold(self.style_data["EditorTextSettings"]["header_1_is_bold"])
        self.header_1_font.setItalic(self.style_data["EditorTextSettings"]["header_1_is_italicized"])

        self.header_2_font = QtGui.QFont(self.style_data["EditorTextSettings"]["header_2_font"],self.style_data["EditorTextSettings"]["header_2_text_size"])
        self.header_2_color = f"color: rgb({self.style_data['EditorTextSettings']['header_2_color']})"
        self.header_2_font.setBold(self.style_data["EditorTextSettings"]["header_2_is_bold"])
        self.header_2_font.setItalic(self.style_data["EditorTextSettings"]["header_2_is_italicized"])

        self.editor_info_title_font = QtGui.QFont(self.style_data["EditorTextSettings"]["editor_info_title_font"],self.style_data["EditorTextSettings"]["editor_info_title_text_size"])
        self.editor_info_title_color = f"color: rgb({self.style_data['EditorTextSettings']['editor_info_title_color']})"
        self.editor_info_title_font.setBold(self.style_data["EditorTextSettings"]["editor_info_title_is_bold"])
        self.editor_info_title_font.setItalic(self.style_data["EditorTextSettings"]["editor_info_title_is_italicized"])

        self.paragraph_font = QtGui.QFont(self.style_data["EditorTextSettings"]["paragraph_font"],self.style_data["EditorTextSettings"]["paragraph_text_size"])
        self.paragraph_color = f"color: rgb({self.style_data['EditorTextSettings']['paragraph_color']})"
        self.paragraph_font.setBold(self.style_data["EditorTextSettings"]["paragraph_is_bold"])
        self.paragraph_font.setItalic(self.style_data["EditorTextSettings"]["paragraph_is_italicized"])

        self.editor_info_paragraph_font = QtGui.QFont(self.style_data["EditorTextSettings"]["editor_info_paragraph_font"],self.style_data["EditorTextSettings"]["editor_info_paragraph_text_size"])
        self.editor_info_paragraph_color = f"color: rgb({self.style_data['EditorTextSettings']['editor_info_paragraph_color']})"
        self.editor_info_paragraph_font.setBold(self.style_data["EditorTextSettings"]["editor_info_paragraph_is_bold"])
        self.editor_info_paragraph_font.setItalic(self.style_data["EditorTextSettings"]["editor_info_paragraph_is_italicized"])

        self.subtext_font = QtGui.QFont(self.style_data["EditorTextSettings"]["subtext_font"], self.style_data["EditorTextSettings"]["subtext_text_size"],QtGui.QFont.Bold)
        self.subtext_color = f"color: rgb({self.style_data['EditorTextSettings']['subtext_color']})"
        self.subtext_font.setBold(self.style_data["EditorTextSettings"]["subtext_is_bold"])
        self.subtext_font.setItalic(self.style_data["EditorTextSettings"]["subtext_is_italicized"])

        self.button_font = QtGui.QFont(self.style_data["EditorTextSettings"]["button_font"], self.style_data["EditorTextSettings"]["button_text_size"])
        self.button_color = f"color: rgb({self.style_data['EditorTextSettings']['button_color']})"
        self.button_font.setBold(self.style_data["EditorTextSettings"]["button_is_bold"])
        self.button_font.setItalic(self.style_data["EditorTextSettings"]["button_is_italicized"])

        self.button_font = QtGui.QFont(self.style_data["EditorTextSettings"]["button_font"], self.style_data["EditorTextSettings"]["button_text_size"])
        self.button_color = f"color: rgb({self.style_data['EditorTextSettings']['button_color']})"
        self.button_font.setBold(self.style_data["EditorTextSettings"]["button_is_bold"])
        self.button_font.setItalic(self.style_data["EditorTextSettings"]["button_is_italicized"])

        # Widget Misc
        self.toolbar_background_color = self.style_data["EditorInterfaceSettings"]["toolbar_background_color"]

        # Buttons
        self.general_button_background_color = self.style_data["EditorInterfaceSettings"]["general_button_background_color"]
        self.general_button_border_color = self.style_data["EditorInterfaceSettings"]["general_button_border_color"]

        self.toolbar_button_background_color = self.style_data["EditorInterfaceSettings"]["toolbar_button_background_color"]

        # State
        self.read_only_background_color = f"background-color: rgb({self.style_data['EditorStateSettings']['read_only_background_color']})"
        self.selection_color = f"selection-background-color: rgb({self.style_data['EditorStateSettings']['selection_color']})"

    def ConvertPartialToAbsolutePath(self, partial_path):
        """ Given a parital path, return a absolute path """
        return self.editor_root + "/" + partial_path
