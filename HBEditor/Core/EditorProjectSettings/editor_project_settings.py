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
from HBEditor.Core.settings import Settings
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.BaseClasses.base_editor import EditorBase
from HBEditor.Interface.EditorProjectSettings.editor_project_settings import EditorProjectSettingsUI
from HBEditor.Utilities.DataTypes.file_types import FileType
from Tools.HBYaml.hb_yaml import Reader, Writer


class EditorProjectSettings(EditorBase):
    def __init__(self, file_path):
        super().__init__(file_path)

        self.file_type = FileType.Project_Settings

        # Read this data in first as the U.I will need it to initialize properly
        self.project_settings = Reader.ReadAll(self.file_path)
        self.project_settings_schema = Reader.ReadAll(
            Settings.getInstance().ConvertPartialToAbsolutePath("Config/ProjectSettingsSchema.yaml")
        )

        self.editor_ui = EditorProjectSettingsUI(self)
        Logger.getInstance().Log("Editor initialized")

    def Export(self):
        super().Export()
        Logger.getInstance().Log(f"Exporting Project Settings")

        # Just in case the user has made any changes to the settings, save them
        self.editor_ui.UpdateProjectSettingsData()

        # Write the data out
        Logger.getInstance().Log("Writing data to file...")
        try:
            Writer.WriteFile(
                self.project_settings,
                self.file_path,
                f"# Type: {FileType.Project_Settings.name}\n" +
                f"# {Settings.getInstance().editor_data['EditorSettings']['version_string']}"
            )
            Logger.getInstance().Log("File Exported!", 2)
        except:
            Logger.getInstance().Log("Failed to Export!", 4)
