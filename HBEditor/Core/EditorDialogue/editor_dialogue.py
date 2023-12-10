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
from HBEditor.Core.base_editor import EditorBase
from HBEditor.Core.EditorDialogue.editor_dialogue_ui import EditorDialogueUI
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.EditorUtilities import action_data as ad
from Tools.HBYaml.hb_yaml import Reader, Writer


class EditorDialogue(EditorBase):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.editor_ui = EditorDialogueUI(self)
        self.editor_ui.branches_panel.CreateEntry(
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
        if new_branch.data:
            for entry in new_branch.data:
                action_name, action_data = next(iter(entry.items()))
                self.editor_ui.dialogue_sequence.AddEntry(action_name, action_data, None, True)

    def StoreActiveData(self, cur_branch):
        """ Updates the active branch with the data from all active dialogue entries """
        # Clear the contents of the current branch since we're forcefully updating it
        cur_branch.data.clear()

        dialogue_table = self.editor_ui.dialogue_sequence.dialogue_table
        num_of_entries = dialogue_table.rowCount()
        for entry_index in range(num_of_entries):
            dialogue_entry = dialogue_table.cellWidget(entry_index, 0)
            cur_branch.data.append({dialogue_entry.GetName(): dialogue_entry.Get()})

    def GetAllDialogueData(self) -> dict:
        """ Collects all dialogue data in the loaded file, including all branches, and returns them as a dict """
        data_to_export = {}
        branch_count = self.editor_ui.branches_panel.GetCount()
        for index in range(0, branch_count):
            # Get the actual branch entry widget instead of the container
            branch = self.editor_ui.branches_panel.GetEntryItemWidget(index)

            # Before we save, let's be extra sure the current information in the details panel is cached properly
            self.editor_ui.details.StoreData()

            # If a branch is currently active, then it's likely to of not updated its cached branch data (Only
            # happens when the active branch is switched). To account for this, make sure the active branch is checked
            # differently by scanning the current dialogue entries
            if branch is self.editor_ui.branches_panel.active_entry:
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

        # Collect the scene settings
        conv_scene_data = ad.ConvertParamDataToEngineFormat(self.editor_ui.scene_settings.GetData(), force_when_no_change=True)

        # Collect everything for the "dialogue" key
        data_to_export = self.GetAllDialogueData()

        # Merge the collected data
        data_to_export = {
            "type": FileType.Dialogue.name,
            "settings": conv_scene_data,
            "dialogue": self.ConvertDialogueToEngineFormat(data_to_export)
        }

        # Write the data out
        Logger.getInstance().Log("Writing data to file...")
        try:
            Writer.WriteFile(
                data=data_to_export,
                file_path=self.file_path,
                metadata=settings.GetMetadataString()
            )
            self.editor_ui.SIG_USER_SAVE.emit()
            Logger.getInstance().Log("File Exported!", 2)
        except Exception as exc:
            Logger.getInstance().Log(f"Failed to Export: {exc}", 4)

    def Import(self):
        super().Import()
        Logger.getInstance().Log(f"Importing Dialogue data for: {self.file_path}")

        file_data = Reader.ReadAll(self.file_path)

        # Skip importing if the file has no data to load
        if file_data:
            # Populate the scene settings
            self.editor_ui.scene_settings.Populate(file_data["settings"])

            # Populate the branches and dialogue sequence
            converted_data = self.ConvertDialogueToEditorFormat(file_data["dialogue"])
            for branch_name, branch_data in converted_data.items():
                # The main branch is treated uniquely since we don't need to create it
                if not branch_name == "Main":
                    self.editor_ui.branches_panel.CreateEntry(branch_name, branch_data["description"])

                for entry in branch_data["entries"]:
                    action_name, action_data = next(iter(entry.items()))
                    self.editor_ui.dialogue_sequence.AddEntry(action_name, action_data, None, True)

            # Select the main branch by default
            self.editor_ui.branches_panel.ChangeEntry(0)

    def ConvertDialogueToEngineFormat(self, action_data: dict):
        """
        Given a dict of dialogue branches and their actions in editor format, convert them to the engine format.
        Return the converted dict
        """
        new_dialogue_data = {}
        for branch_name, branch_data in action_data.items():
            converted_branch = {
                "description": branch_data["description"]
            }

            converted_entries = []
            for entry in branch_data["entries"]:
                # Convert the data for this action to the engine format before rebuilding the full entry
                action_name, action_data = next(iter(entry.items()))
                conv_ad = ad.ConvertParamDataToEngineFormat(action_data)
                converted_entries.append({action_name: conv_ad})

            # Complete the converted branch, and add it to the new dialogue data
            converted_branch["entries"] = converted_entries
            new_dialogue_data[branch_name] = converted_branch

        return new_dialogue_data

    def ConvertDialogueToEditorFormat(self, action_data):
        """
        Given a full dict of dialogue file data in engine format (branches and all), convert it to the editor format by
        rebuilding the structure based on lookups in the ActionDatabase
        """
        new_dialogue_data = {}

        for branch_name, branch_data in action_data.items():
            converted_entries = []
            for entry in branch_data["entries"]:
                # Entries are dicts with only one top level key, which is the name of the action. Use it to look up
                # the matching ACTION_DATA and clone it
                action_name, action_data = next(iter(entry.items()))
                base_ad_clone = copy.deepcopy(settings.GetActionData(action_name))

                # Pass the entry by ref, and let the convert func edit it directly
                ad.ConvertActionDataToEditorFormat(
                    base_action_data=base_ad_clone,
                    action_data=action_data
                )

                # Add unique dialogue-only parameters that wouldn't be found in the 'ACTION_DATA'
                base_ad_clone['post_wait'] = {
                    "type": "Dropdown",
                    "value": action_data['post_wait'],
                    "options": ["wait_for_input", "wait_until_complete", "no_wait"],
                    "flags": ["editable", "preview"]
                }

                converted_entries.append({action_name: base_ad_clone})

            # Update the branch entries with the newly converted ones
            branch_data["entries"] = converted_entries
            new_dialogue_data[branch_name] = branch_data

        return new_dialogue_data
