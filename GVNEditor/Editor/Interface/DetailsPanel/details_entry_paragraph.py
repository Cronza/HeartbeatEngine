from PyQt5 import QtWidgets
from Editor.Interface.DetailsPanel.details_entry_base import DetailsEntryBase

class DetailsEntryParagraph(DetailsEntryBase):
    def __init__(self, settings, refresh_func=None, global_toggle_func=None):
        super().__init__(settings, refresh_func, global_toggle_func)

        self.input_widget = QtWidgets.QPlainTextEdit()
        self.input_widget.setMaximumHeight(100)

        self.input_widget.setFont(self.settings.paragraph_font)
        self.input_widget.setStyleSheet(settings.paragraph_color)
        self.input_widget.textChanged.connect(self.InputValueUpdated)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> str:
        return self.input_widget.toPlainText()

    def Set(self, data) -> None:
        # Disconnect the input change signal to allow us to perform the change without flipping the global toggle
        self.input_widget.disconnect()

        # Change the data without causing any signal calls
        #self.input_widget.setPlainText("This is a test string\nI wonder if the line break worked") # DEBUG
        self.input_widget.setPlainText(data)

        # Now that the input is changed, reconnect
        self.input_widget.textChanged.connect(self.InputValueUpdated)

    def MakeUneditable(self):
        self.input_widget.setReadOnly(True)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color)


