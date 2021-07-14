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
from Editor.Interface.EditorSceneDialogue.editor_scene_dialogue import EditorSceneDialogueUI
from Editor.Utilities.DataTypes.file_types import FileType
from Editor.Utilities.DataTypes.parameter_types import ParameterType
from Editor.Utilities.yaml_manager import Writer
from Editor.Utilities.yaml_manager import Reader

#@TODO: Deprecate the Dialogue Scene Editor

class EditorSceneDialogue(EditorBase):
    def __init__(self, settings, logger, file_path):
        super().__init__(settings, logger, file_path)

        self.file_type = FileType.Scene_Dialogue

        self.editor_ui = EditorSceneDialogueUI(self)
        self.logger.Log("Editor initialized")

    def Export(self):
        super().Export()
        self.logger.Log(f"Exporting Dialogue Scene data for: {self.file_path}")

        data_to_export = self.editor_ui.GetSceneData()

        # *** PRE-EXPORT ADJUSTMENTS ***
        data_to_export["type"] = "Dialogue"

        # Write the data out
        self.logger.Log("Writing data to file...")
        try:
            Writer.WriteFile(
                data_to_export,
                self.file_path,
                f"# Type: {FileType.Scene_Dialogue.name}\n" +
                f"# {self.settings.editor_data['EditorSettings']['version_string']}"
            )
            self.logger.Log("File Exported!", 2)
        except:
            self.logger.Log("Failed to Export!", 4)

    def Import(self):
        super().Import()
        self.logger.Log(f"Importing Dialogue Scene data for: {self.file_path}")

        file_data = Reader.ReadAll(self.file_path)
        root = self.editor_ui.settings_table.invisibleRootItem()
        root.child(0).Set(file_data["dialogue"])
        root.child(1).Set(file_data["starting_background"])
