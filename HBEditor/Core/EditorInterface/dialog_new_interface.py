from HBEditor.Core.Dialogs.dialog_new_file_from_template import DialogNewFileFromTemplate, FileOption
from HBEditor.Core.DataTypes.file_types import FileType

""" Available templates for users to clone from when creating new interfaces """
REGISTERED_TEMPLATES = [
    # Main Menu
    {
        "display_name": "Main Menu 01",
        "description": "A simple main menu U.I with centered icons, and a project title card which is connected to the 'title' project setting.",
        "template_path": "HBEngine/Content/Interfaces/main_menu_01.interface",
        "preview_image": ":/Images/Template_Interface_Main_Menu.jpg"
    },
    # Pause Menu
    {
        "display_name": "Pause Menu 01",
        "description": "A simple pause menu that splits the screen into two sections:\n\n- The left side is persistent and contains the main buttons\n- The right side is populated as you click certain buttons, such as 'Options' and 'Save'",
        "template_path": "HBEngine/Content/Interfaces/pause_menu_01.interface",
        "preview_image": ":/Images/Template_Interface_Pause_Menu.jpg"
    },
    # Dialogue
    {
        "display_name": "Dialogue 01",
        "description": "A simple dialogue interface resembling ones used often in Western Visual Novels. Contains a Save, Load and Menu button along with a Speaker and Dialogue text frame",
        "template_path": "HBEngine/Content/Interfaces/dialogue_01.interface",
        "preview_image": ":/Images/Template_Interface_Dialogue.jpg"
    }
]


class DialogNewInterface(DialogNewFileFromTemplate):
    def __init__(self):
        super().__init__(":/Icons/Interface.png")

        FileOption(
            "None",
            "Create a blank interface. Perfect if you want to start from scratch.",
            "",
            ":/Images/Template_Blank.jpg",
            self.options_list
        )

        for item in REGISTERED_TEMPLATES:
            FileOption(
                item["display_name"],
                item["description"],
                item["template_path"],
                item["preview_image"],
                self.options_list
            )

        # Weird fix: For some reason, QListWidgets don't "select" the first entry by default despite it being
        # considered the "currentitem". This makes for a visual bug, so let's forcefully select it
        self.options_list.setCurrentRow(0)
