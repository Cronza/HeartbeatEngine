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
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from HBEditor.Core.settings import Settings
from HBEditor.Interface.Menus.base_popup_menu import BasePopupMenu
from HBEditor.Interface.Menus.NewFileMenu.file_option import FileOption
from HBEditor.Utilities.DataTypes.file_types import FileType


class NewFileMenu(BasePopupMenu):
    def __init__(self, logger, window_icon_path, window_name):
        super().__init__(logger, window_icon_path, window_name)

        self.resize(400, 300)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.options_layout = QtWidgets.QHBoxLayout(self)
        self.description_layout = QtWidgets.QVBoxLayout(self)
        self.buttons_layout = QtWidgets.QHBoxLayout(self)

        self.options_list = QtWidgets.QListWidget()
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Engine_Logo.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        FileOption(
            icon,
            FileType.Scene_Dialogue,
            "Scene (Dialogue)",
            "A scene containing a sequence of dialogue between characters. These files may contain additional branches",
            self.options_list
        )
        FileOption(
            icon,
            FileType.Scene_Point_And_Click,
            "Scene (Point & Click)",
            "A scene with interactable objects. Perfect for designing Point & Click scenes, or interactive maps",
            self.options_list
        )
        #FileOption(
        #    settings,
        #    icon,
        #    FileType.Character,
        #    "Character",
        #    "A file containing details on a character, such as a special font for their name, their unique color, or various sprites representing their moods",
        #    self.options_list
        #)

        self.description = QtWidgets.QLabel()
        self.description.setWordWrap(True)
        self.description.setFont(Settings.paragraph_font)

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






