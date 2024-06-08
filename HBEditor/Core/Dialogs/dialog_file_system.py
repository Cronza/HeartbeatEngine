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
import os
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core import settings
from PyQt6.QtWidgets import QFileDialog, QMessageBox


class DialogFileSystem(QFileDialog):
    def __init__(self, parent):
        super().__init__(parent)

    def SaveFile(self, type_filter, starting_dir, prompt_title="Save File", project_only=True) -> str:
        """
        Prompts the user with a filedialog which has them specify a file to create or write to. If nothing
        is selected, return an empty string
        """

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
                if settings.user_project_dir in selected_dir:
                    Logger.getInstance().Log("Valid file chosen")
                    return selected_dir
                else:
                    self.ShowPathOutsideProjectMessage()
                    return ""
            else:
                Logger.getInstance().Log("Valid file chosen")
                return selected_dir
        else:
            Logger.getInstance().Log("File name and path not provided", 3)
            return ""

    def GetDirectory(self, starting_dir, prompt_title="Choose a Directory", project_only=True) -> str:
        """ Opens up a prompt for choosing an existing directory. If nothing is selected, return an empty string"""
        Logger.getInstance().Log("Requesting directory path...")

        dir_path = self.getExistingDirectory(
            self.parent(),
            prompt_title,
            starting_dir
        )

        if dir_path:
            if project_only:
                if settings.user_project_dir in dir_path:
                    Logger.getInstance().Log("Valid directory chosen")
                    return dir_path
                else:
                    self.ShowPathOutsideProjectMessage()
                    return ""
            else:
                Logger.getInstance().Log("Valid directory chosen")
                return dir_path
        else:
            Logger.getInstance().Log("No directory chosen", 3)
            return ""

    def GetFile(self, starting_dir, type_filter, prompt_title="Choose a File", project_only=True) -> str:
        """ Opens up a prompt for choosing an existing file. If nothing is selected, return an empty string"""
        Logger.getInstance().Log("Requesting file path...")

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
                if settings.user_project_dir in selected_dir:
                    Logger.getInstance().Log("Valid file chosen")
                    return selected_dir
                else:
                    self.ShowPathOutsideProjectMessage()
                    return ""
            else:
                Logger.getInstance().Log("Valid file chosen")
                return selected_dir
        else:
            Logger.getInstance().Log("File name and path not provided", 3)
            return ""

    def ShowPathOutsideProjectMessage(self):
        """ Show a notice to the user that the path they have chosen does not reside in the active project directory """
        QMessageBox.about(
            self.parent(),
            "Invalid Value Provided!",
            "The chosen file path exists outside the active project directory.\n"
            "Please select a path that resides in the active project"
        )
