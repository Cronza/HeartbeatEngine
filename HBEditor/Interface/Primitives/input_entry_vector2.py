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
from HBEditor.Core.settings import Settings
from HBEditor.Interface.Primitives.input_entry_base import InputEntryBase

class InputEntryTuple(InputEntryBase):
    def __init__(self, refresh_func=None):
        super().__init__(refresh_func)

        #@TODO: Make this two floats, not two ints
        self.input_widget_title = QtWidgets.QLabel('X')
        self.input_widget_title.setFont(Settings.getInstance().paragraph_font)
        self.input_widget_title.setStyleSheet(Settings.getInstance().paragraph_color)
        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.setFont(Settings.getInstance().paragraph_font)
        self.input_widget.setStyleSheet(Settings.getInstance().paragraph_color)
        self.input_widget.textChanged.connect(self.InputValueUpdated)

        self.input_widget_alt_title = QtWidgets.QLabel('Y')
        self.input_widget_alt_title.setFont(Settings.getInstance().paragraph_font)
        self.input_widget_alt_title.setStyleSheet(Settings.getInstance().paragraph_color)
        self.input_widget_alt = QtWidgets.QLineEdit()
        self.input_widget_alt.setFont(Settings.getInstance().paragraph_font)
        self.input_widget_alt.setStyleSheet(Settings.getInstance().paragraph_color)
        self.input_widget_alt.textChanged.connect(self.InputValueUpdated)

        # Limit entered values to int only
        validator = QtGui.QDoubleValidator(0, 1, 8)
        self.input_widget.setValidator(validator)
        self.input_widget_alt.setValidator(validator)

        # Assign default value
        self.input_widget.setText("0")
        self.input_widget_alt.setText("0")

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget_title)
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.input_widget_alt_title)
        self.main_layout.addWidget(self.input_widget_alt)

    def Get(self):
        text_x = self.input_widget.text()
        text_y = self.input_widget_alt.text()

        if text_x == "":
            text_x = 0
        if text_y == "":
            text_y = 0

        return [float(text_x), float(text_y)]

    def Set(self, data) -> None:
        # Disconnect the input change signal to allow us to perform the change without flipping the global toggle
        self.input_widget.disconnect()
        self.input_widget_alt.disconnect()

        # Change the data without causing any signal calls
        self.input_widget.setText(str(data[0]))
        self.input_widget_alt.setText(str(data[1]))

        # Now that the input is changed, reconnect
        self.input_widget.textChanged.connect(self.InputValueUpdated)
        self.input_widget_alt.textChanged.connect(self.InputValueUpdated)

    def MakeUneditable(self):
        self.input_widget.setEnabled(False)
        self.input_widget_alt.setEnabled(False)
        self.input_widget.setStyleSheet(Settings.getInstance().read_only_background_color)
        self.input_widget_alt.setStyleSheet(Settings.getInstance().read_only_background_color)

    def MakeEditable(self):
        self.input_widget.setEnabled(True)
        self.input_widget.setStyleSheet("")
        self.input_widget_alt.setEnabled(True)
        self.input_widget_alt.setStyleSheet("")



