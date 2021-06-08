from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.DetailsPanel.details_entry_base import DetailsEntryBase


class DetailsEntryFileSelector(DetailsEntryBase):
    def __init__(self, settings, type_filter, refresh_func=None, global_toggle_func=None):
        super().__init__(settings, refresh_func, global_toggle_func)

        # Store a type filter to restrict what files can be chosen in the browser
        self.type_filter = type_filter

        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.setFont(self.settings.paragraph_font)
        self.input_widget.setStyleSheet(settings.paragraph_color)
        self.input_widget.setText("None")
        self.input_widget.textChanged.connect(self.InputValueUpdated)

        # Create the file selector button, and style it accordingly
        self.file_select_button = QtWidgets.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.file_select_button.setIcon(icon)
        self.file_select_button.clicked.connect(self.OpenFilePrompt)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.file_select_button)

    def Get(self):
        return self.input_widget.text()

    def Set(self, data) -> None:
        # Disconnect the input change signal to allow us to perform the change without flipping the global toggle
        self.input_widget.disconnect()

        # Change the data without causing any signal calls
        self.input_widget.setText(data)

        # Now that the input is changed, reconnect
        self.input_widget.textChanged.connect(self.InputValueUpdated)

    def MakeUneditable(self):
        self.input_widget.setReadOnly(True)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color);

    def OpenFilePrompt(self) -> str:
        #@TODO: Replace file browser will popup list of files available in the project
        """ Prompts the user with a filedialog, accepting an existing file """
        file_path = QtWidgets.QFileDialog.getOpenFileName(self.input_container,
                                                          "Open File",
                                                          self.settings.GetProjectContentDirectory(),
                                                          self.type_filter
                                                          )
        # Did the user choose a value?
        if file_path[0]:
            selected_dir = file_path[0]

            # Is the path in the active project dir?
            if self.settings.user_project_dir in selected_dir:

                # Remove the project dir from the path, so that the selected dir only contains a relative path
                self.Set(selected_dir.replace(self.settings.user_project_dir + "/", ""))

            # It is not. This is not allowed
            else:
                # @TODO: Can we present the user with an import prompt here
                QtWidgets.QMessageBox.about(self.parent(), "Invalid Value Provided!",
                                            "The chosen file exists outside the active project directory.\n"
                                            "Please either select a file that resides in the active project,\n"
                                            "or move the chosen file into the project's Content directory"
                                            )





