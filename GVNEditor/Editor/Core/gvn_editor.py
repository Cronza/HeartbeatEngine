import os
import sys
import shutil
from pathlib import Path
from PyQt5 import QtWidgets
from Editor.Utilities.settings import Settings
from Editor.Utilities.DataTypes.file_types import FileType
from Editor.Interface import gvn_editor as gvne
from Editor.Interface.Menus.NewFileMenu.new_file_menu import NewFileMenu
from Editor.Interface.Generic.Prompts.file_system_prompt import FileSystemPrompt
from Editor.Core.EditorDialogue.editor_dialogue import EditorDialogue


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
        self.SetActiveProject("To Infinity", "D:\Scripts\GVNEngine\PROJECTS\To Infinity")

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
            "Choose a Directory to Create a Project"
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

            if user_project_name:
                self.logger.Log("Project name was not provided - Cancelling 'New Project' action", 3)
            else:
                # Check if the project folder exists. If so, inform the user that this is already a project dir
                if os.path.exists(os.path.join(new_project_dir, user_project_name)):
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
                    project_path = os.path.join(new_project_dir, user_project_name)
                    os.mkdir(project_path)

                    # Create the pre-requisite project folders
                    for main_dir in self.settings.PROJECT_FOLDER_STRUCTURE.items():

                        # Create the main dir (.../Content)
                        main_dir_path = os.path.join(project_path, main_dir[0])
                        os.mkdir(main_dir_path)

                        # Loop deeper if necessary
                        if not main_dir[1] is None:
                            for sub_dir in main_dir[1]:
                                sub_dir_path = os.path.join(main_dir_path, sub_dir)
                                os.mkdir(sub_dir_path)

                    # Create the admin folder
                    admin_dir_path = os.path.join(project_path, self.settings.PROJECT_ADMIN_DIR)
                    os.mkdir(admin_dir_path)

                    # Clone project default files
                    for key, rel_path in self.settings.PROJECT_DEFAULT_FILES.items():
                        shutil.copy(
                            os.path.join(self.settings.BASE_ENGINE_DIR, rel_path),
                            os.path.join(project_path, rel_path))

                    self.logger.Log(f"Project Created at: {project_path}", 2)

                    # Set this as the active project
                    self.SetActiveProject(user_project_name, project_path)

    def OpenProject(self):
        """ Prompts the user for a project directory, then loads that file in the respective editor """
        self.logger.Log("Requesting path to project root...")

        prompt = FileSystemPrompt(self.settings, self.logger, self.main_window)
        existing_project_dir = prompt.GetDirectory(
            str(Path.home()),
            "Choose a Project Directory"
         )

        if not existing_project_dir:
            self.logger.Log("Project directory was not provided - Cancelling 'Open Project' action", 4)
        else:
            # Does the directory already have a project in it (Denoted by the admin folder's existence)
            print(os.path.join(existing_project_dir, self.settings.PROJECT_ADMIN_DIR))
            if os.path.exists(os.path.join(existing_project_dir, self.settings.PROJECT_ADMIN_DIR)):
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
        new_file_prompt = NewFileMenu(self.settings, self.logger, "Content/Icons/GVNEngine_Logo.png", "Choose a File Type")

        # Did the user successfully choose something?
        if new_file_prompt.exec():

            selected_type = new_file_prompt.GetSelection()
            sub_dir = self.settings.FILE_TYPE_LOCATIONS[selected_type]

            prompt = FileSystemPrompt(self.settings, self.logger, self.main_window)
            result = prompt.SaveFile(
                self.settings.SUPPORTED_CONTENT_TYPES['Data'],
                os.path.join(self.settings.GetProjectContentDirectory(), sub_dir),
                "Save File As"
            )

            # Did the user choose a place and a name for the new file?
            if result:
                with open(result, 'w') as new_file:
                    pass
                    self.logger.Log(f"File created - {result}", 2)

            self.OpenEditor(result, selected_type)

    def Save(self):
        """ Requests the active editor to save it's data """
        self.active_editor.Save()
        self.active_editor.Export()
        """
        cur_editor_ui = self.e_ui.main_tab_editor.currentWidget()

        if cur_editor_ui:
            # TODO: Make this not awful
            # Each type of editor follows a different export / save process, so split off for each here
            # So uh, how do we differentiate editors?

            cur_editor_type = cur_editor_ui.core.editor_type

            if cur_editor_type == "Dialogue":
                exporter = ExporterDialogue(self.settings, self.logger)
                exporter.Export(cur_editor_ui)
        """

    def OpenEditor(self, target_file_path, editor_type):
        """ Creates an editor tab based on the provided file information """

        if not self.CheckTabLimit():

            editor_classes = {
                FileType.Dialogue: EditorDialogue
                #FileType.Scene_Dialogue: EditorSceneDialogue,
                #FileType.Scene_Dialogue: EditorScenePointAndClick,
                #FileType.Scene_Point_And_Click: EditorCharacter,
             }

            # Initialize the Editor
            self.active_editor = editor_classes[editor_type](self.settings, self.logger, target_file_path)

            # Add it to the tab list
            self.e_ui.main_tab_editor.addTab(self.active_editor.ed_ui, os.path.basename(target_file_path))
        else:
            QtWidgets.QMessageBox.about(
                self.e_ui.central_widget,
                "Tab Limit Reached!",
                "You have reached the maximum number of open tabs. Please close "
                "a tab before attempting to open another"
            )

    # ****** UTILITY FUNCTIONS ******

    def CheckTabLimit(self):
        """ Returns true or false depending on whether we've reached the maximum number of tabs """
        return self.settings.settings['EditorSettings']['max_tabs'] <= self.e_ui.main_tab_editor.count()

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


if __name__ == "__main__":
    editor = GVNEditor()
