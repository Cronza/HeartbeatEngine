from PyQt6 import QtWidgets


class EditEntryPrompt(QtWidgets.QDialog):
    def __init__(self, name, description, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Entry Configuration")

        # Create layout and add widgets
        self.main_layout = QtWidgets.QVBoxLayout()

        # Name
        self.entry_name_header = QtWidgets.QLabel("Name:")
        self.entry_name_input = QtWidgets.QLineEdit(name)

        # Description
        self.entry_description_header = QtWidgets.QLabel("Description:")
        self.entry_description_input = QtWidgets.QPlainTextEdit(description)

        # Cancel & Accept
        self.button_layout = QtWidgets.QHBoxLayout()
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.accept_button = QtWidgets.QPushButton("Accept")
        self.button_layout.addWidget(self.accept_button)
        self.button_layout.addWidget(self.cancel_button)

        # Add everything together
        self.main_layout.addWidget(self.entry_name_header)
        self.main_layout.addWidget(self.entry_name_input)
        self.main_layout.addWidget(self.entry_description_header)
        self.main_layout.addWidget(self.entry_description_input)
        self.main_layout.addLayout(self.button_layout)

        # Set dialog layout
        self.setLayout(self.main_layout)

        # Connect buttons
        self.accept_button.clicked.connect(self.Accept)
        self.cancel_button.clicked.connect(self.Cancel)

    def Cancel(self):
        self.reject()

    def Accept(self):
        if self.entry_name_input.text() == "":
            logger.Log("No entry name provided - Cancelling prompt")
            self.reject()
        else:
            self.accept()

    def Get(self):
        """ Returns the name and description as a tuple """
        return self.entry_name_input.text(), self.entry_description_input.toPlainText()


