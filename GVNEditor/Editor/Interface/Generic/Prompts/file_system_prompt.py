import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox


class FileSystemPrompt(QFileDialog):
    def __init__(self, settings, logger, parent):
        super().__init__(parent)

        self.settings = settings
        self.logger = logger

    def SaveFile(self, type_filter, starting_dir, prompt_title="Save File", project_only=True) -> str:
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

            if project_only:
                if self.settings.user_project_dir in selected_dir:
                    self.logger.Log("Valid file chosen")
                    return selected_dir
                else:
                    self.ShowPathOutsideProjectMessage()
                    return ""
            else:
                self.logger.Log("Valid file chosen")
                return selected_dir
        else:
            self.logger.Log("File name and path not provided", 3)
            return ""

    def GetDirectory(self, starting_dir, prompt_title="Choose a Directory", project_only=True) -> str:
        """ Opens up a prompt for choosing an existing directory """
        self.logger.Log("Requesting directory path...")

        dir_path = self.getExistingDirectory(
            self.parent(),
            prompt_title,
            starting_dir
        )

        if dir_path:
            if project_only:
                if self.settings.user_project_dir in dir_path:
                    self.logger.Log("Valid directory chosen")
                    return dir_path
                else:
                    self.ShowPathOutsideProjectMessage()
                    return ""
            else:
                self.logger.Log("Valid directory chosen")
                return dir_path
        else:
            self.logger.Log("No directory chosen", 3)
            return ""

    def GetFile(self, starting_dir, type_filter, prompt_title="Choose a File", project_only=True) -> str:
        """ Opens up a prompt for choosing an existing file """
        self.logger.Log("Requesting file path...")

        file_path = self.getOpenFileName(
            self.parent(),
            prompt_title,
            starting_dir,
            type_filter
        )

        # Did the user choose a value?
        if file_path[0]:
            selected_dir = file_path[0]

            if project_only:
                if self.settings.user_project_dir in selected_dir:
                    self.logger.Log("Valid file chosen")
                    return selected_dir
                else:
                    self.ShowPathOutsideProjectMessage()
                    return ""
            else:
                self.logger.Log("Valid file chosen")
                return selected_dir
        else:
            self.logger.Log("File name and path not provided", 3)
            return ""

    def ShowPathOutsideProjectMessage(self):
        """ Show a notice to the user that the path they have chosen does not reside in the active project directory """
        QMessageBox.about(
            self.parent(),
            "Invalid Value Provided!",
            "The chosen file path exists outside the active project directory.\n"
            "Please select a path that resides in the active project"
        )
