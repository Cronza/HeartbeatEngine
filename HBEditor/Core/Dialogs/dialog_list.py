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
from PyQt6 import QtWidgets


class DialogList(QtWidgets.QDialog):
    def __init__(self, title: str, body: str, items: list):
        super().__init__()

        self.setWindowTitle(title)

        self.resize(400, 300)
        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.description = QtWidgets.QLabel(body)
        self.description.setWordWrap(True)
        self.main_layout.addWidget(self.description)

        self.list = QtWidgets.QListWidget(self)
        self.main_layout.addWidget(self.list)

        self.buttons_layout = QtWidgets.QHBoxLayout(self)
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttons_layout.addWidget(self.button_box)
        self.main_layout.addLayout(self.buttons_layout)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        for item in items:
            self.list.addItem(QtWidgets.QListWidgetItem(item))
