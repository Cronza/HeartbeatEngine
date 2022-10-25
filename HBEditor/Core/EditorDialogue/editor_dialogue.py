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
from HBEditor.Core import settings
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

    def UpdateDetails(self, selected_item):
        """
        Refreshes the details panel with the details from the selected item. Clears all details if None is provided
        """
        if selected_item:
            self.editor_ui.details.Populate(selected_item)

        else:
            # No entries left to select. Wipe remaining details
            self.editor_ui.details.ClearActiveItem()

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

            # Before we save, let's be extra sure the current information in the details panel is cached properly
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

        # Store any active changes in the details panel
        self.editor_ui.details.StoreData()

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
                f"# {settings.editor_data['EditorSettings']['version_string']}"
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
            for entry in branch_data["entries"]:
                # Convert the requirements for this action to the engine format before rebuilding the full entry,
                # recreating the top level action name key in the process
                conv_requirements = adh.ConvertActionRequirementsToEngineFormat(entry[adh.GetActionName(entry)])
                converted_entries.append({adh.GetActionName(entry): conv_requirements})

            # Complete the converted branch, and add it to the new dialogue data
            converted_branch["entries"] = converted_entries
            new_dialogue_data[branch_name] = converted_branch

        return new_dialogue_data

    def ConvertDialogueFileToEditorFormat(self, action_data):
        """
        Given a full dict of dialogue file data in engine format (branches and all), convert it to the editor format by
        rebuilding the structure based on lookups in the ActionDatabase
        """
        new_dialogue_data = {}

        for branch_name, branch_data in action_data.items():
            converted_entries = []
            for entry in branch_data["entries"]:
                # Entries are dicts with only one top level key, which is the name of the action. Use it to look up
                # the matching metadata entry and clone it
                name = adh.GetActionName(entry)
                metadata_entry = copy.deepcopy(settings.action_metadata[name])

                # Pass the entry by ref, and let the convert func edit it directly
                adh.ConvertActionRequirementsToEditorFormat(
                    metadata_entry=metadata_entry,
                    engine_entry=entry[name]
                )

                converted_entries.append({name: metadata_entry})

            # Update the branch entries with the newly converted ones
            branch_data["entries"] = converted_entries
            new_dialogue_data[branch_name] = branch_data

        return new_dialogue_data
