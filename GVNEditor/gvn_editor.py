import os
import sys
import shutil
import re
from pathlib import Path
from PyQt5 import QtWidgets
from Editor.Utilities.settings import Settings
from Editor.Utilities.DataTypes.file_types import FileType
from Editor.Utilities.play_manager import PlayManager
from Editor.Interface import gvn_editor as gvne
from Editor.Interface.Menus.NewFileMenu.new_file_menu import NewFileMenu
from Editor.Interface.Prompts.file_system_prompt import FileSystemPrompt
from Editor.Core.EditorDialogue.editor_dialogue import EditorDialogue
from Editor.Core.EditorProjectSettings.editor_project_settings import EditorProjectSettings
from Editor.Core.EditorSceneDialogue.editor_scene_dialogue import EditorSceneDialogue


class GVNEditor:
    def __init__(self):

        # The core editor settings object
        self.settings = Settings()

        # Initialize the main window and editor interface
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = QtWidgets.QMainWindow()
        self.e_ui = gvne.GVNEditorUI(self, self.settings)
        self.e_ui.setupUi(self.main_window)

        self.logger = self.e_ui.logger
        self.active_editor = None

        #@TODO: REMOVE EVENTUALLY
        # DEBUG - SKIPS HAVING TO CHOOSE A PROJECT EACH TIME
        #self.SetActiveProject("To Infinity", "PROJECTS/To Infinity") # Machine 1
        self.SetActiveProject("Hello World", "D:/GVNEngine/PROJECTS/Hello World")  # Machine 2

        # Show the interface. This suspends execution until the interface is closed, meaning the proceeding exit command
        # will be ran only then
        self.main_window.show()

        sys.exit(self.app.exec_())

    # ****** INTERFACE MENU ACTIONS ******

    def NewProject(self):
        """
        Prompts the user for a directory to create a new project, and for a project name. Then creates the
        chosen project
        """
        # Ask the user to choose a directory to create a project in
        self.logger.Log("Requesting directory for the new project...'")

        prompt = FileSystemPrompt(self.settings, self.logger, self.main_window)
        new_project_dir = prompt.GetDirectory(
            str(Path.home()),
            "Choose a Directory to Create a Project",
            False
        )

        if not new_project_dir:
            self.logger.Log("Project directory was not provided - Cancelling 'New Project' action", 3)
        else:
            # Ask the user for a project name
            # [0] = user_input: str, [1] = value_provided: bool
            self.logger.Log("Requesting a name for the new project...'")
            user_project_name = QtWidgets.QInputDialog.getText(
                self.e_ui.central_widget,
                "New Project",
                "Please Enter a Project Name:"
            )[0]

            if not user_project_name:
                self.logger.Log("Project name was not provided - Cancelling 'New Project' action", 3)
            else:
                # Check if the project folder exists. If so, inform the user that this is already a project dir
                if os.path.exists(new_project_dir + "/" + user_project_name):
                    self.logger.Log("Chosen project directory already exists - Cancelling 'New Project' action", 4)
                    QtWidgets.QMessageBox.about(
                        self.e_ui.central_widget,
                        "Project Already Exists!",
                        "The chosen directory already contains a project of the chosen name.\n"
                        "Please either delete this project, or choose another directory"
                    )

                # Everything is good to go. Create a new project!
                else:
                    self.logger.Log("Valid project destination chosen! Creating project folder structure...")

                    # Create the project directory
                    project_path = new_project_dir + "/" + user_project_name
                    os.mkdir(project_path)

                    # Create the pre-requisite project folders
                    for main_dir in self.settings.project_folder_structure:
                        main_dir_path = project_path + "/" + main_dir
                        os.mkdir(main_dir_path)

                    # Create the admin folder
                    admin_dir_path = project_path + "/" + self.settings.project_admin_dir
                    os.mkdir(admin_dir_path)

                    # Clone project default files
                    for key, rel_path in self.settings.project_default_files.items():
                        shutil.copy(
                            self.settings.engine_root + "/" + rel_path,
                            project_path + "/" + rel_path
                        )

                    self.logger.Log(f"Project Created at: {project_path}", 2)

                    # Set this as the active project
                    self.SetActiveProject(user_project_name, project_path)

    def OpenProject(self):
        """ Prompts the user for a project directory, then loads that file in the respective editor """
        self.logger.Log("Requesting path to project root...")

        prompt = FileSystemPrompt(self.settings, self.logger, self.main_window)
        existing_project_dir = prompt.GetDirectory(
            str(Path.home()),
            "Choose a Project Directory",
            False
         )

        if not existing_project_dir:
            self.logger.Log("Project directory was not provided - Cancelling 'Open Project' action", 3)
        else:
            # Does the directory already have a project in it (Denoted by the admin folder's existence)
            if os.path.exists(existing_project_dir + "/" + self.settings.project_admin_dir):
                self.logger.Log("Valid project selected - Setting as Active Project...")

                # Since we aren't asking for the project name, let's infer it from the path
                project_name = os.path.basename(existing_project_dir)
                self.SetActiveProject(project_name, existing_project_dir)

            else:
                self.logger.Log("An invalid GVN project was selected - Cancelling 'Open Project' action", 4)
                QtWidgets.QMessageBox.about(
                    self.e_ui.central_widget,
                    "Not a Valid Project Directory!",
                    "The chosen directory is not a valid GVN Project.\n"
                    "Please either choose a different project, or create a new project."
                )
                
    def NewFile(self):
        """
        Prompts the user for a type of file to create, and a location & name for the new file. Then creates that
        file, and loads the respective editor
        """
        # Only allow this is there is an active project
        if not self.settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            new_file_prompt = NewFileMenu(
                self.settings,
                self.logger,
                "Content/Icons/GVNEngine_Logo.png",
                "Choose a File Type"
            )

            # Did the user successfully choose something?
            if new_file_prompt.exec():

                selected_type = new_file_prompt.GetSelection()
                prompt = FileSystemPrompt(self.settings, self.logger, self.main_window)
                result = prompt.SaveFile(
                    self.settings.supported_content_types['Data'],
                    self.settings.GetProjectContentDirectory(),
                    "Save File As"
                )

                # Did the user choose a place and a name for the new file?
                if result:
                    with open(result, 'w') as new_file:
                        pass
                        self.logger.Log(f"File created - {result}", 2)

                    # Create the editor, then export to initially populate the new file
                    self.OpenEditor(result, selected_type)
                    self.active_editor.Export()
                else:
                    self.logger.Log("File information was not provided - Cancelling 'New File' action", 3)

    def OpenFile(self):
        """ Prompt the user to choose a file, then load the respective editor using the data found """
        # Only allow this is there is an active project
        if not self.settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            prompt = FileSystemPrompt(self.settings, self.logger, self.main_window)
            existing_file = prompt.GetFile(
                self.settings.GetProjectContentDirectory(),
                self.settings.supported_content_types['Data'],
                "Choose a File to Open"
            )

            # Does the file actually exist?
            if not existing_file:
                self.logger.Log("File path was not provided - Cancelling 'Open File' action", 3)
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
                        self.logger.Log("An invalid file was selected - Cancelling 'Open File' action", 4)
                        QtWidgets.QMessageBox.about(
                            self.e_ui.central_widget,
                            "Not a Valid File!",
                            "The chosen file was not created by the GVNEditor.\n"
                            "Please either choose a different file, or create a new one.\n\n"
                            "If you authored this file by hand, please add the correct metadata to the top of the file"
                        )

    def Play(self):
        """ Launches the GVNEngine, temporarily suspending the GVNEditor """
        # Only allow this is there is an active project
        if not self.settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            p_manager = PlayManager()
            p_manager.Play(self.e_ui.central_widget, self.logger, self.settings.user_project_dir)

    def Save(self):
        """ Requests the active editor to save it's data """
        # Only allow this is there is an active project
        if not self.settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            if self.active_editor:
                self.active_editor.Export()

    def SaveAs(self):
        """ Prompts the user for a new location and file name to save the active editor's data """
        # Only allow this is there is an active project
        if not self.settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            # The user is not allowed to rename the project settings file due to the number of dependencies on it
            if self.active_editor.file_type is FileType.Project_Settings:
                self.logger.Log("Project Settings can not be renamed or saved to a new location", 3)
            else:
                prompt = FileSystemPrompt(self.settings, self.logger, self.main_window)
                new_file_path = prompt.SaveFile(
                    self.settings.supported_content_types['Data'],
                    self.active_editor.GetFilePath(),
                    "Choose a Location to Save the File",
                    True
                )

                if not new_file_path:
                    self.logger.Log("File path was not provided - Cancelling 'SaveAs' action", 3)
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

        if not self.CheckTabLimit():

            editor_classes = {
                FileType.Dialogue: EditorDialogue,
                FileType.Scene_Dialogue: EditorSceneDialogue,
                #FileType.Scene_Dialogue: EditorScenePointAndClick,
                #FileType.Scene_Point_And_Click: EditorCharacter,
                FileType.Project_Settings: EditorProjectSettings
             }

            # Let's check if we already have an editor open for this file
            result = self.CheckIfFileOpen(target_file_path)
            if result:
                #@TODO: Should there be a reimport if the user tries to open an opened file? Or maybe a refesh button?
                self.logger.Log("An editor for the selected file is already open - Switching to the open editor ", 3)
                self.e_ui.main_tab_editor.setCurrentWidget(result)
            else:
                # Initialize the Editor
                self.active_editor = editor_classes[editor_type](self.settings, self.logger, target_file_path)

                # Allow the caller to load the provided file instead of just marking it as the export target
                if import_file:
                    self.active_editor.Import()

                self.e_ui.AddTab(self.active_editor.GetUI(), os.path.basename(target_file_path))
        else:
            QtWidgets.QMessageBox.about(
                self.e_ui.central_widget,
                "Tab Limit Reached!",
                "You have reached the maximum number of open tabs. Please close "
                "a tab before attempting to open another"
            )

    def OpenProjectSettings(self):
        """ Opens the 'Project Settings' editor """
        if not self.settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            self.OpenEditor(
                self.settings.user_project_dir + "/" + self.settings.project_default_files['Config'],
                FileType.Project_Settings,
                True
            )

    # ****** UTILITY FUNCTIONS ******

    def ShowNoActiveProjectPrompt(self):
        """ Shows a simple dialog informing the user that no project is currently active """
        QtWidgets.QMessageBox.about(
            self.e_ui.central_widget,
            "No Active Project",
            "There is currently no project open.\n"
            "Please either open an existing project, or create a new one."
        )

    def CheckIfFileOpen(self, file_path):
        """ Checks all open editor tabs for the provided file. Returns a bool if already open """
        for tab_index in range(0, self.e_ui.main_tab_editor.count()):
            open_editor = self.e_ui.main_tab_editor.widget(tab_index)

            if open_editor.core.file_path == file_path:
                return open_editor

        return None

    def CheckTabLimit(self):
        """ Returns true or false depending on whether we've reached the maximum number of tabs """
        return self.settings.editor_data['EditorSettings']['max_tabs'] <= self.e_ui.main_tab_editor.count()

    def SetActiveProject(self, project_name, project_dir):
        """ Sets the active project, pointing the editor to the new location, and refreshing the inteface """
        self.settings.user_project_name = project_name
        self.settings.user_project_dir = project_dir.replace("\\", "/")
        self.settings.LoadProjectSettings()

        # If this is the first time a user is loading a project after opening the editor, delete the 'Getting Started'
        # display
        if self.e_ui.getting_started_container:
            target = self.e_ui.main_resize_container.widget(0)
            target.deleteLater()

            self.e_ui.CreateTabEditor()

        # Refresh U.I text using any active translations
        self.e_ui.retranslateUi(self.main_window)

    def ValidateNewFileLocation(self, file_path) -> bool:
        """ Given a file path, validate and return a bool for whether it's a valid path based on the active editor """

        if self.settings.user_project_dir not in file_path:
            QtWidgets.QMessageBox.about(
                self.e_ui.central_widget,
                "Invalid Directory",
                "The chosen path is outside the Content folder. \n\n"
                "Please choose another location inside the Content folder"
            )
            return False
        else:
            return True

if __name__ == "__main__":
    editor = GVNEditor()
