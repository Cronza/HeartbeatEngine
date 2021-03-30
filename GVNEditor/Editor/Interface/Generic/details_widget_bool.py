from PyQt5 import QtWidgets, QtCore
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase

class DetailsEntryBool(DetailsEntryBase):
    def __init__(self, settings, refresh_func=None):
        super().__init__(settings, refresh_func)

        self.input_widget = QtWidgets.QCheckBox()
        self.input_widget.stateChanged.connect(refresh_func)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> QtCore.Qt.CheckState:
        return self.input_widget.isChecked()

    def Set(self, data) -> None:
        self.input_widget.setCheckState(data)

    def MakeUneditable(self):
        self.input_widget.setEnabled(False)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color)


