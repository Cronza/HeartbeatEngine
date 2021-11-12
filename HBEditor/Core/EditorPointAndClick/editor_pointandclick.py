from HBEditor.Core.BaseClasses.base_editor import EditorBase
from HBEditor.Utilities.DataTypes.file_types import FileType
from HBEditor.Interface.EditorPointAndClick.editor_pointandclick import EditorPointAndClickUI


class EditorPointAndClick(EditorBase):
    def __init__(self, settings, logger, file_path):
        super().__init__(settings, logger, file_path)

        self.file_type = FileType.Scene_Point_And_Click

        self.editor_ui = EditorPointAndClickUI(self)
        self.logger.Log("Editor initialized")
