import os
from PyQt5 import QtWidgets
from Editor.Utilities.yaml_manager import Writer


class ExporterDialogue:
    def __init__(self, settings, logger):
        print("Initializing Dialogue Exporter")

        self.settings = settings
        self.logger = logger


    def Export(self, dialogue_ui):
        ui = dialogue_ui
        self.logger.Log("Exporting Dialogue Data")


        # Prompt the user to choose where to save the file
        self.OpenFilePrompt(dialogue_ui, self.settings.SUPPORTED_CONTENT_TYPES['Data'])

        if False:
            data_to_export = []
            branch_count = ui.branches.branches_list.count()
            for index in range(0, branch_count):
                branch = ui.branches.branches_list.itemWidget(ui.branches.branches_list.item(index))

                # If a branch is currently active, then it's likely to of not updated it's cached branch data (Only
                # happens when the active branch is switched). To account for this, make sure the active branch is checked
                # differently by scanning the current dialogue entries
                if branch is ui.branches.active_branch:
                    self.logger.Log("Scanning dialogue entries...")
                    ui.core.UpdateBranchData(branch)

                branch_name = branch.Get()[0]
                branch_data = branch.GetData()




            print(branch.GetData())
            #print(ui.branches.active_branch)
            #print(ui.dialogue_sequence.GetSelectedEntry())
        #print(ui.branches)


    def OpenFilePrompt(self, parent, type_filter):
        """ Prompts the user with a filedialog, accepting an existing file """
        file_path = QtWidgets.QFileDialog.getSaveFileName(
            parent,
            "Save File As",
            os.path.join(self.settings.GetProjectContentDirectory(), "Dialogue"),
            type_filter
        )

        # Did the user choose a value?
        if file_path[0]:
            selected_dir = file_path[0]

            # Is the path in the active project dir?
            print(self.settings.user_project_dir)
            print(selected_dir)
            if self.settings.user_project_dir in selected_dir:
                print(selected_dir)
                # Remove the project dir from the path, so that the selected dir only contains a relative path
                #self.Set(selected_dir.replace(self.settings.user_project_dir + "/", ""))

            # It is not. This is not allowed
            else:
                QtWidgets.QMessageBox.about(
                    parent,
                    "Invalid Value Provided!",
                    "The chosen file path exists outside the active project directory.\n"
                    "Please select a path that resides in the active project"
                )
        else:
            self.logger.Log("File name and path not provided  - Cancelling 'Save' action", 3)
            QtWidgets.QMessageBox.about(parent,
                                        "No Value Provided!",
                                        "No file path was provided"
                                        )

