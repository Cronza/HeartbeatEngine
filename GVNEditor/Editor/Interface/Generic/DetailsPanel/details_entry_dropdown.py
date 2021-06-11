from PyQt5 import QtWidgets
from Editor.Interface.Generic.DetailsPanel.details_entry_base import DetailsEntryBase

class DetailsEntryDropdown(DetailsEntryBase):
    def __init__(self, settings, options, refresh_func=None, global_toggle_func=None):
        """ A variant of the details entry that uses a pre-set list of options, instead of accepting anything """
        super().__init__(settings, refresh_func, global_toggle_func)

        self.input_widget = QtWidgets.QComboBox()
        self.input_widget.setFont(self.settings.paragraph_font)
        self.input_widget.setStyleSheet(settings.paragraph_color)

        for option in options:
            self.input_widget.addItem(option)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

        self.input_widget.currentIndexChanged.connect(self.InputValueUpdated)

    def Get(self):
        return self.input_widget.currentText()

    def Set(self, data) -> None:
        # Disconnect the input change signal to allow us to perform the change without flipping the global toggle
        self.input_widget.disconnect()

        # Change the data without causing any signal calls
        self.input_widget.setCurrentIndex(self.input_widget.findText(data))

        # Now that the input is changed, reconnect
        self.input_widget.currentIndexChanged.connect(self.InputValueUpdated)

    def MakeUneditable(self):
        self.input_widget.setReadOnly(True)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color);
