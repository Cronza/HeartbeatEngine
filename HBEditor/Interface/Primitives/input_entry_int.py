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
from HBEditor.Interface.Primitives.input_entry_base import InputEntryBase

class InputEntryInt(InputEntryBase):
    def __init__(self, settings, refresh_func=None):
        super().__init__(settings, refresh_func)

        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.setFont(self.settings.paragraph_font)
        self.input_widget.setStyleSheet(settings.paragraph_color)
        self.input_widget.textChanged.connect(self.InputValueUpdated)

        # Limit entered values to int only
        self.validator = QtGui.QIntValidator()
        self.input_widget.setValidator(self.validator)

        # Assign default value
        self.input_widget.setText("0")

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> int:
        value = self.input_widget.text()
        if value:
            return int(value)
        else:
            return 0

    def Set(self, data) -> None:
        # Disconnect the input change signal to allow us to perform the change without flipping the global toggle
        self.input_widget.disconnect()

        # Change the data without causing any signal calls
        self.input_widget.setText(str(data))

        # Now that the input is changed, reconnect
        self.input_widget.textChanged.connect(self.InputValueUpdated)

    def MakeUneditable(self):
        self.input_widget.setEnabled(False)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color)

    def MakeEditable(self):
        self.input_widget.setEnabled(True)
        self.input_widget.setStyleSheet("")

