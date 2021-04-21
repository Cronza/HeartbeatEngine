from PyQt5 import QtWidgets, QtCore
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase

class DetailsEntryBool(DetailsEntryBase):
    def __init__(self, settings, refresh_func=None, global_toggle_func=None):
        super().__init__(settings, refresh_func, global_toggle_func)

        self.input_widget = QtWidgets.QCheckBox()
        self.input_widget.stateChanged.connect(self.InputValueUpdated)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

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
        self.input_widget.setStyleSheet(self.settings.read_only_background_color)


