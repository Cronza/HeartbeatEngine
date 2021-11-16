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
from HBEditor.Core.BaseClasses.base_editor import EditorBase
from HBEditor.Utilities.DataTypes.file_types import FileType
from HBEditor.Interface.EditorPointAndClick.editor_pointandclick import EditorPointAndClickUI


class EditorPointAndClick(EditorBase):
    def __init__(self, settings, logger, file_path):
        super().__init__(settings, logger, file_path)

        self.file_type = FileType.Scene_Point_And_Click

        self.editor_ui = EditorPointAndClickUI(self)
        self.logger.Log("Editor initialized")
