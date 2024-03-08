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
from PyQt6 import QtWidgets
from HBEditor.Core import settings
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.base_editor import EditorBase
from HBEditor.Core.EditorVariables.editor_variables_ui import EditorVariablesUI
from HBEditor.Core.EditorVariables.editor_variables_ui import VariableNameUndefined
from HBEditor.Core.EditorVariables.editor_variables_ui import VariableAlreadyExists

from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.EditorUtilities import path
from Tools.HBYaml.hb_yaml import Reader, Writer


class EditorVariables(EditorBase):
    def __init__(self, file_path):
        super().__init__(file_path)

        # Read this data in first as the U.I will need it to initialize properly
        self.variables_data = Reader.ReadAll(self.file_path)

        self.editor_ui = EditorVariablesUI(self)
        Logger.getInstance().Log("Editor initialized")

    def Export(self):
        Logger.getInstance().Log(f"Exporting Variables")

        # Collect the table data
        data_to_export = {}
        try:
            data_to_export = self.editor_ui.GetData()
        except VariableNameUndefined:
            QtWidgets.QMessageBox.about(
                self.editor_ui,
                "Unable to Save",
                "Variables are required to have a name. Please specify a name for all variables and try again."
            )
            return
        except VariableAlreadyExists:
            QtWidgets.QMessageBox.about(
                self.editor_ui,
                "Unable to Save",
                "Variable names are unique and can not be duplicated. Please ensure all variables have a unique name and try again."
            )
            return

        # Write the data out
        Logger.getInstance().Log("Writing data to file...")
        try:
            Writer.WriteFile(
                data_to_export,
                self.file_path,
                f"# {settings.editor_data['EditorSettings']['version_string']}"
            )
            self.editor_ui.SIG_USER_SAVE.emit()
            Logger.getInstance().Log("File Exported!", 2)
        except Exception as exc:
            print(exc)
            Logger.getInstance().Log("Failed to Export!", 4)

            # Reload the project variables
            settings.LoadVariables()

    def Import(self):
        super().Import()
        Logger.getInstance().Log(f"Importing Variables data for: {self.file_path}")

        file_data = Reader.ReadAll(self.file_path)

        # Skip importing if the file has no data to load
        if file_data:
            # Disable signals to prevent marking the editor as dirty while we're populating it
            self.editor_ui.blockSignals(True)

            for val_name, val_data in file_data.items():
                self.editor_ui.AddValue(val_name, val_data['type'], val_data['value'])

            self.editor_ui.blockSignals(False)
