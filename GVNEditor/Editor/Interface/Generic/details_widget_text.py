from PyQt5 import QtWidgets
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase

class DetailsEntryText(DetailsEntryBase):
    def __init__(self, settings):
        super().__init__(settings)

        self.input_widget = QtWidgets.QLineEdit()

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> str:
        return self.input_widget.text()

    def Set(self, data) -> None:
        self.input_widget.setText(data)

    def MakeUneditable(self):
        self.input_widget.setReadOnly(True)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color);


