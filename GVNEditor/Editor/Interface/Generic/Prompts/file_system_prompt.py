import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox


class FileSystemPrompt(QFileDialog):
    def __init__(self, settings, logger, parent):
        super().__init__(parent)

        self.settings = settings
        self.logger = logger

    def SaveFile(self, type_filter, starting_dir, prompt_title="Save File") -> str:
        """ Prompts the user with a filedialog which has them specify a file to create or write to """
        file_path = self.getSaveFileName(
            self.parent(),
            prompt_title,
            starting_dir,
            type_filter
        )

        # Did the user choose a value?
        if file_path[0]:
            selected_dir = file_path[0]

            # Is the path in the active project dir? Make sure to account for the potential slash difference
            if self.settings.user_project_dir in selected_dir:

                # Remove the project dir from the path, so that the selected dir only contains a relative path
                return selected_dir

            # It is not. This is not allowed
            else:
                self.ShowPathOutsideProjectMessage()
                return ""
        else:
            self.logger.Log("File name and path not provided", 3)

    def GetDirectory(self, starting_dir, prompt_title="Choose a Directory") -> str:
        """ Opens up a prompt for choosing an existing directory """
        self.logger.Log("Requesting directory path...")
        print(starting_dir)
        dir_path = self.getExistingDirectory(
            self.parent(),
            starting_dir
        )

        # Did the user choose a value?
        if dir_path:
            return dir_path[0]
        else:
            self.logger.Log("No directory chosen", 3)
            return ""

    def ShowPathOutsideProjectMessage(self):
        """ Show a notice to the user that the path they have chosen does not reside in the active project directory """
        QMessageBox.about(
            self.parent(),
            "Invalid Value Provided!",
            "The chosen file path exists outside the active project directory.\n"
            "Please select a path that resides in the active project"
        )
