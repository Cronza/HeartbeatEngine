from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Primitives.input_entry_base import InputEntryBase

class InputEntryInt(InputEntryBase):
    def __init__(self, settings, refresh_func=None, global_toggle_func=None):
        super().__init__(settings, refresh_func, global_toggle_func)

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
        self.input_widget.setReadOnly(True)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color)

