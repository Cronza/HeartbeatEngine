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
import copy
from HBEditor.Core.settings import Settings
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.BaseClasses.base_editor import EditorBase
from HBEditor.Core.EditorDialogue.editor_dialogue_ui import EditorDialogueUI
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.EditorUtilities import action_data_handler as adh
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
            self.editor_ui.details.Populate(selected_entry)

        # No entries left to select. Wipe remaining details
        else:
            self.editor_ui.details.Clear()

    def SwitchBranches(self, cur_branch, new_branch):
        """ Switches the active branch, storing all existing dialogue sequence entries in the old branch """

        # If there is no source branch, then there is nothing to store
        if cur_branch:
            self.StoreActiveData(cur_branch)
            self.editor_ui.dialogue_sequence.Clear()

        # Load any entries in the new branch (if applicable)
        if new_branch.branch_data:
            for entry in new_branch.branch_data:
                self.editor_ui.dialogue_sequence.AddEntry(entry, None, True)

    def StoreActiveData(self, cur_branch):
        """ Updates the active branch with all active dialogue entries """
        # Clear the contents of the current branch since we're forcefully updating it
        cur_branch.branch_data.clear()

        dialogue_table = self.editor_ui.dialogue_sequence.dialogue_table
        num_of_entries = dialogue_table.rowCount()
        for entry_index in range(num_of_entries):
            dialogue_entry = dialogue_table.cellWidget(entry_index, 0)
            cur_branch.branch_data.append(dialogue_entry.action_data)

    def GetAllDialogueData(self) -> dict:
        """ Collects all dialogue data in the loaded file, including all branches, and returns them as a dict """
        data_to_export = {}
        branch_count = self.editor_ui.branches.branches_list.count()
        for index in range(0, branch_count):
            # Get the actual branch entry widget instead of the containing item widget
            branch = self.editor_ui.branches.branches_list.itemWidget(self.editor_ui.branches.branches_list.item(index))

            # Before we save, let's be double sure the current information in the details panel is cached properly
            self.editor_ui.details.StoreData()

            # If a branch is currently active, then it's likely to of not updated its cached branch data (Only
            # happens when the active branch is switched). To account for this, make sure the active branch is checked
            # differently by scanning the current dialogue entries
            if branch is self.editor_ui.branches.active_branch:
                Logger.getInstance().Log("Scanning dialogue entries...")
                self.StoreActiveData(branch)

            branch_name, branch_description = branch.Get()
            branch_data = branch.GetData()
            new_entry = {
                "description": branch_description,
                "entries": branch_data
            }

            data_to_export[branch_name] = new_entry

        return data_to_export

    def Export(self):
        super().Export()
        Logger.getInstance().Log(f"Exporting Dialogue data for: {self.file_path}")
        data_to_export = self.GetAllDialogueData()
        data_to_export = {
            "type": FileType.Scene_Dialogue.name,
            "dialogue": self.ConvertDialogueFileToEngineFormat(data_to_export)
        }

        # Write the data out
        Logger.getInstance().Log("Writing data to file...")
        try:
            Writer.WriteFile(
                data=data_to_export,
                file_path=self.file_path,
                metadata=f"# Type: {FileType.Scene_Dialogue.name}\n" +
                f"# {Settings.getInstance().editor_data['EditorSettings']['version_string']}"
            )
            Logger.getInstance().Log("File Exported!", 2)
        except Exception as exc:
            Logger.getInstance().Log(f"Failed to Export: {exc}", 4)

    def Import(self):
        super().Import()
        Logger.getInstance().Log(f"Importing Dialogue data for: {self.file_path}")

        file_data = Reader.ReadAll(self.file_path)

        # Skip importing if the file has no data to load
        if file_data:
            converted_data = self.ConvertDialogueFileToEditorFormat(file_data["dialogue"])

            # The main branch is treated specially since we don't need to create it
            for branch_name, branch_data in converted_data.items():
                if not branch_name == "Main":
                    self.editor_ui.branches.CreateBranch(branch_name, branch_data["description"])

                for action in branch_data["entries"]:
                    self.editor_ui.dialogue_sequence.AddEntry(action, None, True)

            # Select the main branch by default
            self.editor_ui.branches.ChangeBranch(0)

    def ConvertDialogueFileToEngineFormat(self, action_data: dict):
        """
        Given a full dict of dialogue file data in editor format (branches and all), convert it to the engine format
        Return the converted dict
        """
        new_dialogue_data = {}
        for branch_name, branch_data in action_data.items():
            converted_branch = {
                "description": branch_data["description"]
            }

            converted_entries = []
            for editor_action in branch_data["entries"]:
                converted_action = {"action": editor_action["action_name"]}

                # Collect a converted dict of all requirements for this action (If any are present)
                converted_requirements = adh.ConvertActionRequirementsToEngineFormat(editor_action)
                if converted_requirements:
                    converted_action.update(converted_requirements)

                # Add the newly converted action
                converted_entries.append(converted_action)

            # Complete the converted branch, and add it to the new dialogue data
            converted_branch["entries"] = converted_entries
            new_dialogue_data[branch_name] = converted_branch

        return new_dialogue_data

    def ConvertDialogueFileToEditorFormat(self, action_data):
        """
        Given a full dict of dialogue file data in engine format (branches and all), convert it to the editor format by
        rebuilding the structure based on lookups in the ActionDatabase
        """
        #@TODO: Investigate how to speed this up. The volume of O(n) searching is worrying
        new_dialogue_data = {}

        for branch_name, branch_data in action_data.items():
            converted_entries = []
            for action in branch_data["entries"]:
                action_name = action["action"]

                # Using the name of the action, look it up in the ActionDatabase. If found, clone it
                database_entry = None
                for cat_name, cat_data in Settings.getInstance().action_database.items():
                    for option in cat_data["options"]:
                        if action_name == option['action_name']:
                            database_entry = copy.deepcopy(option)
                            break
                    if database_entry:
                        break
                # Pass the entry by ref, and let the convert func edit it directly
                adh.ConvertActionRequirementsToEditorFormat(
                    editor_req=database_entry,
                    engine_req=action
                )
                converted_entries.append(database_entry)

            branch_data["entries"] = converted_entries
            new_dialogue_data[branch_name] = branch_data

        return new_dialogue_data
