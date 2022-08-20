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
import sys
import shutil
import re
from pathlib import Path
from PyQt5 import QtWidgets

from HBEditor import hb_editor_ui as hbe
from HBEditor.Content import content
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core import settings
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.play_manager import PlayManager
from HBEditor.Core.Menus.NewFileMenu.new_file_menu import NewFileMenu
from HBEditor.Core.Prompts.file_system_prompt import FileSystemPrompt
from HBEditor.Core.EditorDialogue.editor_dialogue import EditorDialogue
from HBEditor.Core.EditorPointAndClick.editor_pointandclick import EditorPointAndClick
from HBEditor.Core.EditorProjectSettings.editor_project_settings import EditorProjectSettings
from Tools.HBBuilder.hb_builder import HBBuilder
from Tools.HBYaml.hb_yaml import Reader, Writer


class HBEditor:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)

        self.main_window = QtWidgets.QMainWindow()
        self.e_ui = hbe.HBEditorUI(self)
        self.e_ui.setupUi(self.main_window)

        self.outliner = None  # Assignment happens once a project is loaded
        self.active_editor = None

        # Show the interface. This suspends execution until the interface is closed, meaning the proceeding exit command
        # will be ran only then
        self.main_window.show()

        sys.exit(self.app.exec_())

    def NewProject(self):
        """
        Prompts the user for a directory to create a new project, and for a project name. Then creates the
        chosen project
        """
        Logger.getInstance().Log("Requesting directory for the new project...'")
        prompt = FileSystemPrompt(self.main_window)
        new_project_dir = prompt.GetDirectory(
            self.GetLastSearchPath(),
            "Choose a Directory to Create a Project",
            False
        )
        self.UpdateSearchHistory(new_project_dir)

        if not new_project_dir:
            Logger.getInstance().Log("Project directory was not provided - Cancelling 'New Project' action", 3)
        else:
            # [0] = user_input: str, [1] = value_provided: bool
            Logger.getInstance().Log("Requesting a name for the new project...'")
            user_project_name = QtWidgets.QInputDialog.getText(
                self.e_ui.central_widget,
                "New Project",
                "Please Enter a Project Name:"
            )[0]

            if not user_project_name:
                Logger.getInstance().Log("Project name was not provided - Cancelling 'New Project' action", 3)
            else:
                # Check if the project folder exists. If so, inform the user that this is already a project dir
                if os.path.exists(new_project_dir + "/" + user_project_name):
                    Logger.getInstance().Log("Chosen project directory already exists - Cancelling 'New Project' action", 4)
                    QtWidgets.QMessageBox.about(
                        self.e_ui.central_widget,
                        "Project Already Exists!",
                        "The chosen directory already contains a project of the chosen name.\n"
                        "Please either delete this project, or choose another directory"
                    )

                # Everything is good to go. Create a new project!
                else:
                    Logger.getInstance().Log("Valid project destination chosen! Creating project folder structure...")

                    # Create the project directory
                    project_path = new_project_dir + "/" + user_project_name
                    os.mkdir(project_path)

                    # Create the pre-requisite project folders
                    for main_dir in settings.project_folder_structure:
                        main_dir_path = project_path + "/" + main_dir
                        os.mkdir(main_dir_path)

                    # Create the project file
                    project_file = project_path + "/" + settings.project_file
                    with open(project_file, "w"):
                        pass

                    # Clone project default files
                    for key, rel_path in settings.project_default_files.items():
                        shutil.copy(
                            settings.engine_root + "/" + rel_path,
                            project_path + "/" + rel_path
                        )

                    Logger.getInstance().Log(f"Project Created at: {project_path}", 2)

                    # Set this as the active project
                    self.SetActiveProject(user_project_name, project_path)

    def OpenProject(self):
        """ Prompts the user for a project directory, then loads that file in the respective editor """
        Logger.getInstance().Log("Requesting path to project root...")
        prompt = FileSystemPrompt(self.main_window)
        existing_project_dir = prompt.GetDirectory(
            self.GetLastSearchPath(),
            "Choose a Project Directory",
            False
         )
        self.UpdateSearchHistory(existing_project_dir)

        if not existing_project_dir:
            Logger.getInstance().Log("Project directory was not provided - Cancelling 'Open Project' action", 3)
        else:
            # Does the directory already have a project in it (Denoted by the admin folder's existence)
            if os.path.exists(existing_project_dir + "/" + settings.project_file):
                Logger.getInstance().Log("Valid project selected - Setting as Active Project...")

                # Since we aren't asking for the project name, let's infer it from the path
                project_name = os.path.basename(existing_project_dir)
                self.SetActiveProject(project_name, existing_project_dir)
            else:
                Logger.getInstance().Log("An invalid Heartbeat project was selected - Cancelling 'Open Project' action", 4)
                QtWidgets.QMessageBox.about(
                    self.e_ui.central_widget,
                    "Not a Valid Project Directory!",
                    "The chosen directory is not a valid Heartbeat project.\n"
                    "Please either choose a different project, or create a new project."
                )

    def NewFile(self):
        """
        Prompts the user for a type of file to create, and a location & name for the new file. Then creates that
        file, and loads the respective editor
        """
        # Only allow this is there is an active project
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            new_file_prompt = NewFileMenu(
                ":/Icons/Engine_Logo.png",
                "Choose a File Type"
            )

            # Did the user successfully choose something?
            if new_file_prompt.exec():

                selected_type = new_file_prompt.GetSelection()
                prompt = FileSystemPrompt(self.main_window)
                result = prompt.SaveFile(
                    settings.supported_content_types['Data'],
                    settings.GetProjectContentDirectory(),
                    "Save File As"
                )

                # Did the user choose a place and a name for the new file?
                if result:
                    with open(result, 'w') as new_file:
                        pass
                        Logger.getInstance().Log(f"File created - {result}", 2)

                    # Create the editor, then export to initially populate the new file
                    self.OpenEditor(result, selected_type)
                    self.active_editor.Export()
                else:
                    Logger.getInstance().Log("File information was not provided - Cancelling 'New File' action", 3)

    def OpenFile(self, target_file_path=None):
        """ Prompt the user to choose a file, then load the respective editor using the data found """
        # Only allow this is there is an active project
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            existing_file = None

            # Validate whether the selected file is capable of being opened
            if ".yaml" not in target_file_path:
                Logger.getInstance().Log("File type does not have any interact functionality", 3)
                return
            """
            # *** Re-enable this code when the supported file types all have open functionality ***
            split_path = target_file_path.split(".")
            if len(split_path) > 1:
                extension = split_path[-1]
                is_supported = False
                for type_string in self.settings.supported_content_types.values():
                    if f".{extension}" in type_string:
                        is_supported = True
                        break

            if not is_supported:
                Logger.getInstance().Log("File type does not have any interact functionality", 3)
                pass
            """

            # Is the user opening a file through the main "File->Open" mechanism?
            if not target_file_path:
                prompt = FileSystemPrompt(self.main_window)
                existing_file = prompt.GetFile(
                    settings.GetProjectContentDirectory(),
                    settings.supported_content_types['Data'],
                    "Choose a File to Open"
                )
            # Most likely the outliner requested a file be opened. Use the provided path
            else:
                existing_file = target_file_path

            # Does the file actually exist?
            if not existing_file:
                Logger.getInstance().Log("File path was not provided - Cancelling 'Open File' action", 3)
            else:
                # Read the first line to determine the type of file
                with open(existing_file) as f:

                    # Check the metadata at the top of the file to see which file type this is
                    line = f.readline()
                    search = re.search("# Type: (.*)", line)

                    # Was the expected metadata found?
                    if search:
                        file_type = FileType[search.group(1)]
                        self.OpenEditor(existing_file, file_type, True)
                    else:
                        Logger.getInstance().Log("An invalid file was selected - Cancelling 'Open File' action", 4)
                        QtWidgets.QMessageBox.about(
                            self.e_ui.central_widget,
                            "Not a Valid File!",
                            "The chosen file was not created by the HBEditor.\n"
                            "Please either choose a different file, or create a new one.\n\n"
                            "If you authored this file by hand, please add the correct metadata to the top of the file"
                        )

    def Play(self):
        """ Launches the HBEngine, temporarily suspending the HBEditor """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        elif not settings.user_project_data["Game"]["starting_scene"]:
            self.ShowNoStartingScenePrompt()
        else:
            p_manager = PlayManager()
            p_manager.Play(self.e_ui.central_widget, settings.user_project_dir, settings.root)

    def Build(self):
        """ Launches the HBBuilder in order to generate an executable from the active project """
        # Only allow this is there is an active project
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        elif not settings.user_project_data["Game"]["starting_scene"]:
            self.ShowNoStartingScenePrompt()
        else:
            HBBuilder.Build(
                Logger.getInstance(),
                settings.engine_root,
                settings.user_project_dir,
                settings.user_project_name
            )

    def Clean(self):
        """ Cleans the active project's build folder """
        # Only allow this is there is an active project
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            HBBuilder.Clean(
                Logger.getInstance(),
                settings.user_project_dir
            )

    def Save(self):
        """ Requests the active editor to save it's data """
        # Only allow this is there is an active project
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            if self.active_editor:
                self.active_editor.Export()

    def SaveAs(self):
        """ Prompts the user for a new location and file name to save the active editor's data """
        # Only allow this is there is an active project
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            # The user is not allowed to rename the project settings file due to the number of dependencies on it
            if self.active_editor.file_type is FileType.Project_Settings:
                Logger.getInstance().Log("Project Settings can not be renamed or saved to a new location", 3)
            else:
                prompt = FileSystemPrompt(self.main_window)
                new_file_path = prompt.SaveFile(
                    settings.supported_content_types['Data'],
                    self.active_editor.GetFilePath(),
                    "Choose a Location to Save the File",
                    True
                )

                if not new_file_path:
                    Logger.getInstance().Log("File path was not provided - Cancelling 'SaveAs' action", 3)
                else:
                    can_save = self.ValidateNewFileLocation(new_file_path)
                    if can_save:
                        self.active_editor.file_path = new_file_path
                        self.e_ui.main_tab_editor.setTabText(
                            self.e_ui.main_tab_editor.currentIndex(),
                            self.active_editor.GetFileName()
                        )
                        self.active_editor.Export()

    def OpenEditor(self, target_file_path, editor_type, import_file=False):
        """ Creates an editor tab based on the provided file information """
        if not settings.editor_data["EditorSettings"]["max_tabs"] <= self.e_ui.main_tab_editor.count():
            editor_classes = {
                FileType.Scene_Dialogue: EditorDialogue,
                FileType.Scene_Point_And_Click: EditorPointAndClick,
                FileType.Project_Settings: EditorProjectSettings
             }

            # Let's check if we already have an editor open for this file
            result = self.CheckIfFileOpen(target_file_path)
            if result:
                #@TODO: Should there be a reimport if the user tries to open an opened file? Or maybe a refesh button?
                Logger.getInstance().Log("An editor for the selected file is already open - Switching to the open editor ", 3)
                self.e_ui.main_tab_editor.setCurrentWidget(result)
            else:
                # Initialize the Editor
                self.active_editor = editor_classes[editor_type](target_file_path)

                # Allow the caller to load the provided file instead of just marking it as the export target
                if import_file:
                    self.active_editor.Import()

                self.e_ui.AddTab(
                    self.active_editor.GetUI(),
                    os.path.basename(target_file_path),
                    self.e_ui.main_tab_editor
                )
        else:
            QtWidgets.QMessageBox.about(
                self.e_ui.central_widget,
                "Tab Limit Reached!",
                "You have reached the maximum number of open tabs. Please close "
                "a tab before attempting to open another"
            )

    def SetActiveProject(self, project_name, project_dir):
        """ Sets the active project, pointing the editor to the new location, and refreshing the interface """
        settings.user_project_name = project_name
        settings.user_project_dir = project_dir.replace("\\", "/")
        settings.LoadProjectSettings()

        # If this is the first time a user is loading a project after opening the editor, delete the 'Getting Started'
        # display
        if self.e_ui.getting_started_container:
            target = self.e_ui.main_resize_container.widget(0)
            target.deleteLater()
            self.e_ui.getting_started_container = None

            self.e_ui.CreateMainTabContainer()
            self.e_ui.CreateOutliner()

        # Clear any open editor tabs
        self.e_ui.main_tab_editor.clear()

        # Refresh U.I text using any active translations
        self.e_ui.retranslateUi(self.main_window)

        # Update the outliner with the new project root
        self.outliner.UpdateRoot(settings.GetProjectContentDirectory())

    def OpenProjectSettings(self):
        """ Opens the 'Project Settings' editor """
        # Normally we would have loaded this editor like the others, but since we need to bind loading this to a menu
        # button, we need it in the form of a function
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            self.OpenEditor(
                settings.user_project_dir + "/" + settings.project_default_files['Config'],
                FileType.Project_Settings,
                True
            )

    def ShowNoActiveProjectPrompt(self):
        """ Shows a simple dialog informing the user that no project is currently active """
        QtWidgets.QMessageBox.about(
            self.e_ui.central_widget,
            "No Active Project",
            "There is currently no project open.\n"
            "Please either open an existing project, or create a new one."
        )

    def ShowNoStartingScenePrompt(self):
        """ Shows a simple dialog informing the user that the active project has no assigned starting scene """
        QtWidgets.QMessageBox.about(
            self.e_ui.central_widget,
            "No Starting Scene",
            "There is currently no starting scene.\n"
            "Please open the project settings and choose a starting scene."
        )

    def CheckIfFileOpen(self, file_path):
        """ Checks all open editor tabs for the provided file. Returns a bool if already open """
        for tab_index in range(0, self.e_ui.main_tab_editor.count()):
            open_editor = self.e_ui.main_tab_editor.widget(tab_index)

            if open_editor.core.file_path == file_path:
                return open_editor

        return None

    def ValidateNewFileLocation(self, file_path) -> bool:
        """ Given a file path, validate and return a bool for whether it's a valid path based on the active editor """
        if settings.user_project_dir not in file_path:
            QtWidgets.QMessageBox.about(
                self.e_ui.central_widget,
                "Invalid Directory",
                "The chosen path is outside the Content folder. \n\n"
                "Please choose another location inside the Content folder"
            )
            return False
        else:
            return True

    def UpdateSearchHistory(self, new_search_dir):
        """ Updates the record for the last location searched for in a file browser"""
        if new_search_dir:
            self.WriteToTemp(settings.temp_history_path, {"search_dir": new_search_dir})

    def GetLastSearchPath(self):
        """ Returns the current search path record, or if there is none, return the system home"""
        search_dir = self.ReadFromTemp(settings.temp_history_path, "search_dir")
        if search_dir:
            return search_dir
        else:
            return str(Path.home())

    def WriteToTemp(self, temp_file: str, data: dict) -> bool:
        """ Write to the provided temp file, creating it if it doesn't already exist """
        if not os.path.exists(temp_file):
            try:
                if not os.path.exists(settings.editor_temp_root):
                    os.mkdir(settings.editor_temp_root)
                with open(temp_file, "w"):
                    pass
            except Exception as exc:
                Logger.getInstance().Log(f"Unable to create '{temp_file}'", 4)
                Logger.getInstance().Log(str(exc), 4)
                return False
        temp_data = Reader.ReadAll(temp_file)
        if not temp_data:
            temp_data = {}
        try:
            for key, val in data.items():
                temp_data[key] = val
        except Exception as exc:
            Logger.getInstance().Log(f"Failed to update '{temp_file}'", 4)
            Logger.getInstance().Log(str(exc), 4)
            return False
        Writer.WriteFile(temp_data, temp_file)
        return True

    def ReadFromTemp(self, temp_file: str, key: str) -> str:
        """ Read from the provided temp file using the provided key, returning the results if found """
        if not os.path.exists(temp_file):
            Logger.getInstance().Log(f"The temp file '{temp_file}' was not found")
            return ""
        try:
            req_data = Reader.ReadAll(temp_file)[key]
            return req_data
        except Exception as exc:
            Logger.getInstance().Log(f"Failed to read '{temp_file}'")
            Logger.getInstance().Log(str(exc), 4)
            return ""

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


sys.excepthook = except_hook

print(sys.excepthook)
if __name__ == "__main__":
    editor = HBEditor()
