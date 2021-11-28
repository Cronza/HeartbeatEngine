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
from PyQt5 import QtWidgets
from HBEditor.Core.settings import Settings
from HBEditor.Core.Primitives.input_entry_base import InputEntryBase

class InputEntryParagraph(InputEntryBase):
    def __init__(self, refresh_func=None):
        super().__init__(refresh_func)

        self.input_widget = QtWidgets.QPlainTextEdit()
        self.input_widget.setMaximumHeight(100)

        self.input_widget.setFont(Settings.getInstance().paragraph_font)
        self.input_widget.setStyleSheet(Settings.getInstance().paragraph_color)
        self.input_widget.textChanged.connect(self.InputValueUpdated)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> str:
        return self.input_widget.toPlainText()

    def Set(self, data) -> None:
        # Disconnect the input change signal to allow us to perform the change without flipping the global toggle
        self.input_widget.disconnect()

        # Change the data without causing any signal calls
        #self.input_widget.setPlainText("This is a test string\nI wonder if the line break worked") # DEBUG
        self.input_widget.setPlainText(data)

        # Now that the input is changed, reconnect
        self.input_widget.textChanged.connect(self.InputValueUpdated)

    def MakeUneditable(self):
        self.input_widget.setEnabled(False)
        self.input_widget.setStyleSheet(Settings.getInstance().read_only_background_color)

    def MakeEditable(self):
        self.input_widget.setEnabled(True)
        self.input_widget.setStyleSheet("")
