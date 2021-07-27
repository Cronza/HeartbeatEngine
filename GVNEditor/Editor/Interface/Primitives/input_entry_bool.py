from PyQt5 import QtWidgets
from Editor.Interface.Primitives.input_entry_base import InputEntryBase


class InputEntryBool(InputEntryBase):
    def __init__(self, settings, refresh_func=None):
        super().__init__(settings, refresh_func)

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

    def MakeEditable(self):
        self.input_widget.setEnabled(True)


