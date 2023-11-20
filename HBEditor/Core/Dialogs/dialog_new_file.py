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
from HBEditor.Core.DataTypes.file_types import FileType


class DialogNewFile(QtWidgets.QDialog):
    def __init__(self, icon: str, window_title: str = "Choose a File Type"):
        super().__init__()

        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(icon)))
        self.setWindowTitle(window_title)

        self.resize(400, 300)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.options_layout = QtWidgets.QHBoxLayout(self)
        self.description_layout = QtWidgets.QVBoxLayout(self)
        self.name_layout = QtWidgets.QHBoxLayout(self)
        self.buttons_layout = QtWidgets.QHBoxLayout(self)

        self.options_list = QtWidgets.QListWidget()

        self.description = QtWidgets.QLabel()
        self.description.setWordWrap(True)

        self.options_layout.addWidget(self.options_list, 2)
        self.options_layout.addWidget(self.description, 1, Qt.AlignTop)

        self.name_input_header = QtWidgets.QLabel("Name:")
        self.name_input = QtWidgets.QLineEdit()
        self.name_layout.addWidget(self.name_input_header)
        self.name_layout.addWidget(self.name_input)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttons_layout.addWidget(self.button_box)

        # Compile the full layout
        self.main_layout.addLayout(self.options_layout)
        self.main_layout.addLayout(self.name_layout)
        self.main_layout.addLayout(self.buttons_layout)

        # Signals
        self.options_list.currentItemChanged.connect(self.UpdateDescription)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def UpdateDescription(self):
        """ Updates the displayed description for the selected option """
        cur_item = self.options_list.currentItem()
        if cur_item:
            self.description.setText(cur_item.GetDescription())

    def GetSelection(self):
        """ Returns the type of file selected """
        return self.options_list.currentItem().GetFileType()

    def GetName(self):
        """ Returns the inputted name """
        return self.name_input.text()


class FileOption(QtWidgets.QListWidgetItem):
    def __init__(self, file_type, display_text, description_text, parent):
        super().__init__(display_text, parent)

        self.file_type = file_type
        self.description_text = description_text

    def GetDescription(self):
        """ Returns the description text for this entry """
        return self.description_text

    def GetFileType(self):
        """ Returns the file type stored in this class """
        return self.file_type
