from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase

class DetailsEntryInt(DetailsEntryBase):
    def __init__(self, settings, refresh_func=None):
        super().__init__(settings, refresh_func)

        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.textChanged.connect(refresh_func)

        # Limit entered values to int only
        self.validator = QtGui.QIntValidator()
        self.input_widget.setValidator(self.validator)


        # Assign default value
        self.input_widget.setText("0")

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> int:
        return self.input_widget.text()

    def Set(self, data) -> None:
        self.input_widget.setText(str(data))

    def MakeUneditable(self):
        self.input_widget.setReadOnly(True)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color)

