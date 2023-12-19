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
from HBEditor.Core import settings
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.base_editor import EditorBase
from HBEditor.Core.EditorProjectSettings.editor_project_settings_ui import EditorProjectSettingsUI
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.EditorUtilities import path
from Tools.HBYaml.hb_yaml import Reader, Writer


class EditorProjectSettings(EditorBase):
    def __init__(self, file_path):
        super().__init__(file_path)

        # Read this data in first as the U.I will need it to initialize properly
        self.project_settings = Reader.ReadAll(self.file_path)
        self.project_settings_schema = Reader.ReadAll(
            path.ConvertPartialToAbsolutePath("Config/ProjectSettingsSchema.yaml")
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
                f"# {settings.editor_data['EditorSettings']['version_string']}"
            )
            self.editor_ui.SIG_USER_SAVE.emit()
            Logger.getInstance().Log("File Exported!", 2)
        except:
            Logger.getInstance().Log("Failed to Export!", 4)

        # Reload the project settings
        settings.LoadProjectSettings()
