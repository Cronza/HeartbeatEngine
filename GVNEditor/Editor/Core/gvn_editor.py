import os
import sys
import shutil
from PyQt5 import QtWidgets
from Editor.Utilities.settings import Settings
from Editor.Interface import gvn_editor as gvne
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

        # State Tracking
        self.active_editor = None

        # DEBUG - SKIPS HAVING TO CHOOSE A PROJECT EACH TIME
        self.SetActiveProject("To Infinity", "D:/GVNENGINE_PROJECTS/Testing")

        # Show the interface. This suspends execution until the interface is closed, meaning the proceeding exit command
        # will be ran only then
        self.main_window.show()

        sys.exit(self.app.exec_())

    # ****** INTERFACE MENU ACTIONS ******

    def NewProject(self):
        # Ask the user to choose a directory to create a project in
        self.logger.Log("Requesting directory for the new project...'")
        new_project_dir = QtWidgets.QFileDialog.getExistingDirectory()

        # Has the user provided a project directory?
        if new_project_dir == "":
            self.logger.Log("Error: Project directory was not provided - Cancelling 'New Project' action")
            QtWidgets.QMessageBox.about(self.e_ui.central_widget, "No Value Provided!",
                                        "No project directory was provided"
                                        )
        else:
            # Ask the user for a project name
            # [0] = user_input: str, [1] = value_provided: bool
            self.logger.Log("Requesting a name for the new project...'")
            user_project_name = QtWidgets.QInputDialog.getText(self.e_ui.central_widget,
                                                                             "New Project",
                                                                             "Please Enter a Project Name:")[0]

            # Has the user provided a project name?
            if user_project_name == "":
                self.logger.Log("Error: Project name was not provided - Cancelling 'New Project' action")
                QtWidgets.QMessageBox.about(self.e_ui.central_widget, "No Value Provided!",
                                            "No project name was provided"
                                            )
            else:
                # Check if the project folder exists. If so, inform the user that this is already a project dir
                if os.path.exists(os.path.join(new_project_dir, user_project_name)):
                    self.logger.Log("Error: Chosen project directory already exists - Cancelling 'New Project' action")
                    QtWidgets.QMessageBox.about(self.e_ui.central_widget, "Project Already Exists!",
                                                "The chosen directory already contains a project of the chosen name.\n"
                                                "Please either delete this project, or choose another directory"
                                                )
                # Everything is good to go. Create a new project!
                else:
                    self.logger.Log("Creating project folder structure...")
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

                    self.logger.Log(f"Project Created at: {project_path}")

                    # Set this as the active project
                    self.SetActiveProject(user_project_name, project_path)

    def OpenProject(self):
        self.logger.Log("Requesting path to project root...")
        existing_project_dir = QtWidgets.QFileDialog.getExistingDirectory()

        # Validate that a value was provided, and that the path is a proper GVN project
        if not existing_project_dir:
            self.logger.Log("Error: Project directory was not provided - Cancelling 'Open Project' action")
            QtWidgets.QMessageBox.about(self.e_ui.central_widget, "No Value Provided!",
                                        "No project directory was provided"
                                        )
        else:
            if os.path.exists(os.path.join(existing_project_dir, self.settings.PROJECT_ADMIN_DIR)):
                self.logger.Log("Valid project selected - Setting as Active Project...")

                # Since we aren't asking for the project name, let's infer it from the path
                project_name = os.path.basename(existing_project_dir)
                self.SetActiveProject(project_name, existing_project_dir)

            else:
                self.logger.Log("Error: An invalid GVN project was selected - Cancelling 'Open Project' action")
                QtWidgets.QMessageBox.about(self.e_ui.central_widget, "Not a Valid Project Directory!",
                                            "The chosen directory is not a valid GVN Project.\n"
                                            "Please either choose a different project, or create a new project."
                                            )

    def OpenDialogueEditor(self):
        """ Creates a 'Dialogue Editor' tab """

        # Check if a project is actively open
        if self.settings.user_project_name:

            if not self.CheckTabLimit():

                # Initialize the Dialogue Editor
                self.active_editor = EditorDialogue(self.settings, self.logger)

                # Add it to the tab list (If we're not at the tab limit)
                self.e_ui.main_tab_editor.addTab(self.active_editor.ed_ui, "Dialogue Editor")
            else:
                QtWidgets.QMessageBox.about(self.e_ui.central_widget, "Tab Limit Reached!",
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
        self.settings.user_project_dir = project_dir
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
