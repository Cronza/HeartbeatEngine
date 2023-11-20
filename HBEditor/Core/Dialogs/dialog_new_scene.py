from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.Dialogs.dialog_new_file import DialogNewFile, FileOption


class DialogNewScene(DialogNewFile):
    def __init__(self):
        super().__init__(":/Icons/AM_Scene.png", "Choose a Scene Type")

        FileOption(
            FileType.Scene_Dialogue,
            "Scene (Dialogue)",
            "A scene containing a sequence of dialogue between characters. These files may contain additional branches",
            self.options_list
        )
        FileOption(
            FileType.Scene_Point_And_Click,
            "Scene (Point & Click)",
            "A scene with interactable objects. Perfect for designing Point & Click scenes, or interactive maps. \n\nThis is also the choice when creating Main Menu scenes, or blank scenes where you wish to show an interface.",
            self.options_list
        )

        # Weird fix: For some reason, QListWidgets don't "select" the first entry by default despite it being
        # considered the "currentitem". This makes for a visual bug, so let's forcefully select it
        self.options_list.setCurrentRow(0)
