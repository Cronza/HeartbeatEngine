"""
    This file is part of GVNEditor.

    GVNEditor is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GVNEditor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GVNEditor.  If not, see <https://www.gnu.org/licenses/>.
"""
from Editor.Core.BaseClasses.base_editor import EditorBase
from Editor.Interface.EditorProjectSettings.editor_project_settings import EditorProjectSettingsUI
from Editor.Utilities.yaml_manager import Writer
from Editor.Utilities.yaml_manager import Reader


class EditorProjectSettings(EditorBase):
    def __init__(self, settings, logger, file_path):
        super().__init__(settings, logger, file_path)

        # Read this data in first as the U.I will need it to initialize properly
        self.project_settings = Reader.ReadAll(self.file_path)
        self.project_settings_schema = Reader.ReadAll(
            self.settings.ConvertPartialToAbsolutePath("Config/ProjectSettingsSchema.yaml")
        )

        self.editor_ui = EditorProjectSettingsUI(self)
        self.logger.Log("Editor initialized")

    def Export(self):
        super().Export()
        self.logger.Log(f"Exporting Project Settings")

        # Just in case the user has made any changes to the settings, save them
        self.editor_ui.UpdateProjectSettingsData()

        # *** PRE-EXPORT DATA ADJUSTMENTS ***
        self.project_settings["WindowSettings"]

        # Write the data out
        self.logger.Log("Writing data to file...")
        try:
            Writer.WriteFile(
                self.project_settings,
                self.file_path,
                f"# {self.settings.editor_data['EditorSettings']['version_string']}"
            )
            self.logger.Log("File Exported!", 2)
        except:
            self.logger.Log("Failed to Export!", 4)
