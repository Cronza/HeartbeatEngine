from Editor.Interface.Menus.base_popup_menu import BasePopupMenu
from Editor.Interface.Menus.NewFileMenu.file_option import FileOption
from Editor.Utilities.DataTypes.file_types import FileType
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt


class NewFileMenu(BasePopupMenu):
    def __init__(self, settings, logger, window_icon_path, window_name):
        super().__init__(settings, logger, window_icon_path, window_name)

        self.resize(400, 300)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.options_layout = QtWidgets.QHBoxLayout(self)
        self.description_layout = QtWidgets.QVBoxLayout(self)
        self.buttons_layout = QtWidgets.QHBoxLayout(self)

        self.options_list = QtWidgets.QListWidget()
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/GVNEngine_Logo.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        FileOption(
            icon,
            FileType.Dialogue,
            "Dialogue",
            "A file containing a sequence of dialogue between characters. These files may contain additional branches",
            self.options_list
        )
        FileOption(
            icon,
            FileType.Scene_Point_And_Click,
            "Scene (Point & Click)",
            "A file representing a scene with interactable objects. Perfect for designing Point & Click scenes, or interactive maps",
            self.options_list
        )
        FileOption(
            icon,
            FileType.Scene_Dialogue,
            "Scene (Dialogue)",
            "A simple file representing the scene where dialogue takes place",
            self.options_list
        )
        FileOption(
            icon,
            FileType.Character,
            "Character",
            "A file containing details on a character, such as a special font for their name, their unique color, or various sprites representing their moods",
            self.options_list
        )

        self.description = QtWidgets.QLabel()
        self.description.setWordWrap(True)
        self.options_layout.addWidget(self.options_list, 2)
        self.options_layout.addWidget(self.description, 1, Qt.AlignTop)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttons_layout.addWidget(self.button_box)

        self.main_layout.addLayout(self.options_layout)
        self.main_layout.addLayout(self.buttons_layout)

        # Signals
        self.options_list.currentItemChanged.connect(self.UpdateDescription)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Weird fix: For some reason, QListWidgets don't "select" the first entry by default despite it being
        # considered the "currentitem". This makes for a weird visual bug, so let's forcefully select it
        self.options_list.setCurrentRow(0)

    def UpdateDescription(self):
        """ Updates the displayed description for the selected option """
        cur_item = self.options_list.currentItem()
        if cur_item:
            self.description.setText(cur_item.GetDescription())

    def GetSelection(self):
        """ Returns the type of file selected """
        return self.options_list.currentItem().GetFileType()






