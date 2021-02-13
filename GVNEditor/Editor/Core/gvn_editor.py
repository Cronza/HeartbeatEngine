import os
import sys
from Editor.Utilities.yaml_reader import Reader
from PyQt5 import QtWidgets
from Editor.Interface import gvn_editor as gvne
from Editor.Core.EditorDialogue.editor_dialogue import EditorDialogue


class GVNEditor:
    # Where does the editor store data needed to track and handle project directories?
    PROJECT_ADMIN_DIR = ".gvn"
    PROJECT_FOLDER_STRUCTURE = {
        "Content": [
            "Audio",
            "Characters",
            "Dialogue",
            "Fonts",
            "Objects",
            "Scenes",
            "Sprites",
            "Styles",
            "Values"
        ]

    }
    def __init__(self):
        # Read in editor settings
        self.settings = Reader.ReadAll("editor.yaml")

        # Initialize the main window and editor interface
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = QtWidgets.QMainWindow()
        self.e_ui = gvne.GVNEditorUI(self)
        self.e_ui.setupUi(self.main_window)

        self.logger = self.e_ui.logger

        # State Tracking
        self.active_editor = None

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
            self.logger.Log("Requesting a name for the new project...'")
            user_project_name = QtWidgets.QInputDialog.getText(self.e_ui.central_widget,
                                                               "New Project",
                                                               "Please Enter a Project Name:")

            # Has the user provided a project name?
            if user_project_name[0] == "":
                self.logger.Log("Error: Project name was not provided - Cancelling 'New Project' action")
                QtWidgets.QMessageBox.about(self.e_ui.central_widget, "No Value Provided!",
                                            "No project name was provided"
                                            )
            else:
                # Check if the project folder exists. If so, inform the user that this is already a project dir

                if os.path.exists(os.path.join(new_project_dir, user_project_name[0])):
                    self.logger.Log("Error: Chosen project directory already exists - Cancelling 'New Project' action")
                    QtWidgets.QMessageBox.about(self.e_ui.central_widget, "Project Already Exists!",
                                                "The chosen directory already contains a project of the chosen name.\n"
                                                "Please either delete this project, or choose another directory"
                                                )
                else:
                    self.logger.Log("Creating project folder structure...")
                    # Create the project directory
                    project_path = os.path.join(new_project_dir, user_project_name[0])
                    os.mkdir(project_path)

                    # Create the pre-requisite project folders
                    for main_dir in self.PROJECT_FOLDER_STRUCTURE.items():
                        # Create the main dir (.../Content
                        main_dir_path = os.path.join(project_path, main_dir[0])
                        os.mkdir(main_dir_path)

                        for sub_dir in main_dir[1]:
                            sub_dir_path = os.path.join(main_dir_path, sub_dir)
                            os.mkdir(sub_dir_path)

                    self.logger.Log(f"Project Created at: {project_path}")

    def OpenProject(self):
        print("Open New Project")

    # ****** EDITOR FUNCTIONS ******

    def OpenDialogueEditor(self):
        print("Open Dialogue Editor")
        if not self.check_tab_limit():

            # Initialize the Dialogue Editor
            self.active_editor = EditorDialogue(self.e_ui)

            # Add it to the tab list (If we're not at the tab limit)
            self.e_ui.main_editor_container.addTab(self.active_editor.ed_ui, "Dialogue Editor")
        else:
            QtWidgets.QMessageBox.about(self.e_ui.central_widget, "Tab Limit Reached!",
                                        "You have reached the maximum number of open tabs. Please close "
                                        "a tab before attempting to open another"
                                        )


    # ****** UTILITY FUNCTIONS ******

    def check_tab_limit(self):
        """ Returns true or false depending on whether we've reached the maximum number of tabs """
        return self.settings['EditorSettings']['max_tabs'] <= self.e_ui.main_editor_container.count()

if __name__ == "__main__":
    editor = GVNEditor()

