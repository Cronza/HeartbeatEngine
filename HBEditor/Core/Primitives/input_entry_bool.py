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
from HBEditor.Core.Primitives.input_entry_base import InputEntryBase


class InputEntryBool(InputEntryBase):
    def __init__(self, refresh_func=None):
        super().__init__(refresh_func)

        self.input_widget = QtWidgets.QCheckBox()

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

        # Connect Signals
        self.input_widget.stateChanged.connect(self.InputValueUpdated)

    def Get(self) -> bool:
        return self.input_widget.isChecked()

    def Set(self, data) -> None:
        # Disconnect the input change signal to allow us to perform the change without flipping the global toggle
        self.input_widget.disconnect()

        # Change the data without causing any signal calls
        self.input_widget.setChecked(data)

        # Now that the input is changed, reconnect
        self.input_widget.stateChanged.connect(self.InputValueUpdated)

    def MakeUneditable(self):
        self.input_widget.setEnabled(False)

    def MakeEditable(self):
        self.input_widget.setEnabled(True)


