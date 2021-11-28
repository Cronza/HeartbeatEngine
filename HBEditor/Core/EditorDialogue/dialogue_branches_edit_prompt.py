"""
    The Heartbeat Engine is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The Heartbeat Engine is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with the Heartbeat Engine. If not, see <https://www.gnu.org/licenses/>.
"""
from PyQt5 import QtWidgets


class EditBranchPrompt(QtWidgets.QDialog):
    def __init__(self, branch_name, branch_description, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Branch Configuration")

        # Create layout and add widgets
        self.main_layout = QtWidgets.QVBoxLayout()

        # Branch name
        self.branch_name_header = QtWidgets.QLabel("Branch Name:")
        self.branch_name_input = QtWidgets.QLineEdit(branch_name)

        # Branch description
        self.branch_description_header = QtWidgets.QLabel("Branch Description:")
        self.branch_description_input = QtWidgets.QPlainTextEdit(branch_description)

        # Cancel & Accept
        self.button_layout = QtWidgets.QHBoxLayout()
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.accept_button = QtWidgets.QPushButton("Accept")
        self.button_layout.addWidget(self.accept_button)
        self.button_layout.addWidget(self.cancel_button)

        # Add everything together
        self.main_layout.addWidget(self.branch_name_header)
        self.main_layout.addWidget(self.branch_name_input)
        self.main_layout.addWidget(self.branch_description_header)
        self.main_layout.addWidget(self.branch_description_input)
        self.main_layout.addLayout(self.button_layout)
        # Set dialog layout
        self.setLayout(self.main_layout)

        # Connect buttons
        self.accept_button.clicked.connect(self.Accept)
        self.cancel_button.clicked.connect(self.Cancel)


    def Cancel(self):
        self.reject()

    def Accept(self):
        if self.branch_name_input.text() == "":
            print("No branch name provided - Cancelling prompt")
            self.reject()
        else:
            self.accept()

    def Get(self):
        """ Returns the branch name and description as a tuple """
        return self.branch_name_input.text(), self.branch_description_input.toPlainText()
