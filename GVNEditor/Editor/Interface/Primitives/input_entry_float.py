from PyQt5 import QtWidgets, QtGui
from GVNEditor.Editor.Interface.Primitives.input_entry_base import InputEntryBase

class InputEntryFloat(InputEntryBase):
    def __init__(self, settings, refresh_func=None):
        super().__init__(settings, refresh_func)

        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.setFont(self.settings.paragraph_font)
        self.input_widget.setStyleSheet(settings.paragraph_color)
        self.input_widget.textChanged.connect(self.InputValueUpdated)

        # Limit entered values to float only
        self.validator = QtGui.QDoubleValidator()
        self.input_widget.setValidator(self.validator)

        # Assign default value
        self.input_widget.setText("0.0")

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> float:
        value = self.input_widget.text()
        if value:
            return float(value)
        else:
            return 0.0

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

