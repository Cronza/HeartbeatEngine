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
from PyQt6 import QtWidgets, QtGui, QtCore
from HBEditor.Core import settings


class DialogNewFileFromTemplate(QtWidgets.QDialog):
    def __init__(self, icon: str, window_title: str = "Choose a Template"):
        super().__init__()

        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(icon)))
        self.setWindowTitle(window_title)

        self.resize(640, 360)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.sub_layout = QtWidgets.QHBoxLayout(self)
        self.details_layout = QtWidgets.QVBoxLayout(self)

        # List of options
        self.options_list = QtWidgets.QListWidget()

        # Description / thumbnail
        self.thumbnail = QtWidgets.QLabel()
        self.thumbnail.setScaledContents(True)
        self.details_layout.addWidget(self.thumbnail, 1, QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignCenter)
        self.description = QtWidgets.QLabel()
        self.description.setWordWrap(True)
        self.details_layout.addWidget(self.description, 1, QtCore.Qt.AlignmentFlag.AlignTop)

        # Name selection
        self.name_layout = QtWidgets.QHBoxLayout(self)
        self.name_input_header = QtWidgets.QLabel("Name:")
        self.name_input = QtWidgets.QLineEdit()
        self.name_layout.addWidget(self.name_input_header)
        self.name_layout.addWidget(self.name_input)

        # Buttons
        self.buttons_layout = QtWidgets.QHBoxLayout(self)
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.buttons_layout.addWidget(self.button_box)

        # Compile the full layout
        self.sub_layout.addWidget(self.options_list, 2)
        self.sub_layout.addLayout(self.details_layout, 1)
        self.main_layout.addLayout(self.sub_layout)
        self.main_layout.addLayout(self.name_layout)
        self.main_layout.addLayout(self.buttons_layout)

        # Signals
        self.options_list.currentItemChanged.connect(self.UpdateDetails)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def UpdateDetails(self):
        """ Updates the displayed details for the selected option """
        cur_item: FileOption = self.options_list.currentItem()
        if cur_item:
            self.description.setText(cur_item.GetDescription())
            self.thumbnail.setPixmap(
                QtGui.QPixmap(cur_item.GetPreviewImage()).scaled(
                    round(self.width() / 2), self.thumbnail.height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio
                )
            )

    def GetSelection(self):
        """ Returns the template file path for the selected template """
        return self.options_list.currentItem().GetTemplatePath()

    def GetName(self):
        """ Returns the inputted name """
        return self.name_input.text()


class FileOption(QtWidgets.QListWidgetItem):
    def __init__(self, display_text: str, description_text: str, template_path: str, preview_image: str, parent):
        super().__init__(display_text, parent)

        self.description_text = description_text
        self.template_path = template_path
        self.preview_image = preview_image

    def GetDescription(self):
        """ Returns the description text for this entry """
        return self.description_text

    def GetTemplatePath(self):
        """ Returns the path to the template file stored in this class """
        return self.template_path

    def GetPreviewImage(self):
        """ Returns the preview image stored in this class """
        return self.preview_image
