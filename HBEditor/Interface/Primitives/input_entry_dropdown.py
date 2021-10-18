from PyQt5 import QtWidgets
from HBEditor.Interface.Primitives.input_entry_base import InputEntryBase

class InputEntryDropdown(InputEntryBase):
    def __init__(self, settings, options, refresh_func=None):
        """ A variant of the details entry that uses a pre-set list of options, instead of accepting anything """
        super().__init__(settings, refresh_func)

        self.input_widget = QtWidgets.QComboBox()
        self.input_widget.setFont(self.settings.paragraph_font)
        self.input_widget.setStyleSheet(settings.paragraph_color)

        self.options = options

        # Pre-load the list of dropdown options
        for option in self.options:
            self.input_widget.addItem(str(option))

        self.input_widget.currentIndexChanged.connect(self.InputValueUpdated)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)



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
        self.input_widget.setEnabled(False)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color)

    def MakeEditable(self):
        self.input_widget.setEnabled(True)
        self.input_widget.setStyleSheet("")
