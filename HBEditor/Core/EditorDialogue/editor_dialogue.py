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
from HBEditor.Core.settings import Settings
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.BaseClasses.base_editor import EditorBase
from HBEditor.Core.EditorDialogue.editor_dialogue_ui import EditorDialogueUI
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.database_manager import DBManager
from Tools.HBYaml.hb_yaml import Reader, Writer


class EditorDialogue(EditorBase):
    def __init__(self, file_path):
        super().__init__(file_path)

        self.file_type = FileType.Scene_Dialogue

        self.editor_ui = EditorDialogueUI(self)
        self.editor_ui.branches.CreateBranch(
            "Main",
            "This is the default, main branch\nConsider this the root of your dialogue tree"
        )
        Logger.getInstance().Log("Editor initialized")

    def UpdateActiveEntry(self):
        """ Makes the selected entry the active one, refreshing the details panel """
        selection = self.editor_ui.dialogue_sequence.GetSelectedEntry()

        # Refresh the details panel to reflect the newly chosen row
        self.UpdateDetails(selection)

    def UpdateDetails(self, selected_entry):
        """ Refreshes the details panel with the details from the selected dialogue entry """
        if selected_entry:
            self.editor_ui.details.PopulateDetails(selected_entry)

        # No entries left to select. Wipe remaining details
        else:
            self.editor_ui.details.Clear()

    # @TODO: How to support the initial switch when 'main' is created?
    def SwitchBranches(self, cur_branch, new_branch):
        """ Switches the active branch, storing all existing dialogue sequence entries in the old branch """

        # If there is no source branch, then there is nothing to store
        if cur_branch:
            self.UpdateBranchData(cur_branch)
            self.editor_ui.dialogue_sequence.Clear()

        # Load any entries in the new branch (if applicable)
        if new_branch.branch_data:
            for entry in new_branch.branch_data:
                self.editor_ui.dialogue_sequence.AddEntry(entry, None, True)

    def UpdateBranchData(self, cur_branch):
        """ Updates the active branch with all active dialogue entries """
        # Clear the contents of the current branch since we're forcefully updating whats stored
        cur_branch.branch_data.clear()

        # Store the data from each entry in the branch
        num_of_entries = self.editor_ui.dialogue_sequence.dialogue_table.rowCount()
        for entry_index in range(num_of_entries):

            # Store the data held by the entry
            dialogue_entry = self.editor_ui.dialogue_sequence.dialogue_table.cellWidget(entry_index, 0)
            cur_branch.branch_data.append(dialogue_entry.action_data)

    def GetAllDialogueData(self) -> dict:
        """ Collects all dialogue data in this file, including all branches, and returns them as a dict """
        data_to_export = {}
        branch_count = self.editor_ui.branches.branches_list.count()
        for index in range(0, branch_count):
            # Get the actual branch entry widget instead of the containing item widget
            branch = self.editor_ui.branches.branches_list.itemWidget(self.editor_ui.branches.branches_list.item(index))

            # Before we save, let's be double sure the current information in the details panel is cached properly
            self.editor_ui.details.UpdateCache()

            # If a branch is currently active, then it's likely to of not updated it's cached branch data (Only
            # happens when the active branch is switched). To account for this, make sure the active branch is checked
            # differently by scanning the current dialogue entries
            if branch is self.editor_ui.branches.active_branch:
                Logger.getInstance().Log("Scanning dialogue entries...")
                self.UpdateBranchData(branch)

            branch_name, branch_description = branch.Get()
            branch_data = branch.GetData()
            new_entry = {
                #"name": branch_name,
                "description": branch_description,
                "entries": branch_data
            }

            data_to_export[branch_name] = new_entry

        return data_to_export

    def Export(self):
        super().Export()
        Logger.getInstance().Log(f"Exporting Dialogue data for: {self.file_path}")
        data_to_export = self.GetAllDialogueData()
        db_manager = DBManager()
        data_to_export = {
            "type": FileType.Scene_Dialogue.name,
            "dialogue": db_manager.ConvertDialogueFileToEngineFormat(data_to_export)
        }

        # Write the data out
        Logger.getInstance().Log("Writing data to file...")
        try:
            Writer.WriteFile(
                data_to_export,
                self.file_path,
                f"# Type: {FileType.Scene_Dialogue.name}\n" +
                f"# {Settings.getInstance().editor_data['EditorSettings']['version_string']}"
            )
            Logger.getInstance().Log("File Exported!", 2)
        except:
            Logger.getInstance().Log("Failed to Export!", 4)

    def Import(self):
        super().Import()
        Logger.getInstance().Log(f"Importing Dialogue data for: {self.file_path}")

        file_data = Reader.ReadAll(self.file_path)

        # Skip importing if the file has no data to load
        if file_data:
            db_manager = DBManager()
            converted_data = db_manager.ConvertDialogueFileToEditorFormat(file_data["dialogue"])

            # The main branch is treated specially since we don't need to create it
            for branch_name, branch_data in converted_data.items():
                if not branch_name == "Main":
                    self.editor_ui.branches.CreateBranch(branch_name, branch_data["description"])

                for action in branch_data["entries"]:
                    self.editor_ui.dialogue_sequence.AddEntry(action, None, True)

            # Select the main branch by default
            self.editor_ui.branches.ChangeBranch(0)

