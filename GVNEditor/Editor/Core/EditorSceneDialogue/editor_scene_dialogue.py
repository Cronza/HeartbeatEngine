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
from Editor.Utilities.yaml_manager import Writer
from Editor.Utilities.yaml_manager import Reader


class EditorSceneDialogue(EditorBase):
    def __init__(self, settings, logger, file_path):
        super().__init__(settings, logger, file_path)

        self.file_type = FileType.Scene_Dialogue

        self.editor_ui = EditorSceneDialogueUI(self)

        self.Export()
        self.logger.Log("Editor initialized")

