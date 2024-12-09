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
from PyQt6 import QtWidgets
from HBEditor.Core import settings
from HBEditor.Core.Logger import logger
from HBEditor.Core.base_editor import EditorBase
from HBEditor.Core.EditorVariables.editor_variables_ui import EditorVariablesUI
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.EditorUtilities import path
from Tools.HBYaml.hb_yaml import Reader, Writer


class EditorVariables(EditorBase):
    def __init__(self, file_path):
        super().__init__(file_path)

        # Read this data in first as the U.I will need it to initialize properly
        self.variables = Reader.ReadAll(self.file_path)

        self.editor_ui = EditorVariablesUI(self)
        logger.Log("Editor initialized")

    def SwitchCategories(self, cur_cat, new_cat):
        """ Switches the active category, storing all existing variable entries in the old branch """
        # If there is no source category, then there is nothing to store
        if cur_cat:
            self.StoreActiveData(cur_cat)

        # Load any entries in the new branch (if applicable)
        if new_cat.data:
            self.editor_ui.PopulateVariables(new_cat.data)
        else:
            self.editor_ui.variables_table.setRowCount(0)

    def StoreActiveData(self, cur_group):
        """ Updates the active group with the data from all active variable entries """
        # Clear the contents of the current group since we're forcefully updating it
        cur_group.data.clear()

        var_table = self.editor_ui.variables_table
        for row_index in range(0, var_table.rowCount()):
            var_name = var_table.cellWidget(row_index, var_table.name_column).Get()['value']
            var_type = var_table.cellWidget(row_index, var_table.type_column).Get()['value']
            var_input = var_table.cellWidget(row_index, var_table.input_column).Get()['value']

            cur_group.data.append({var_name: {'type': var_type, 'value': var_input}})

    def GetAllVariableData(self) -> dict:
        """ Collects all variable data, including all categories, and returns them as a dict """
        data_to_export = {}
        cat_count = self.editor_ui.categories.GetCount()
        for index in range(0, cat_count):
            # Get the actual category entry widget instead of the container
            category = self.editor_ui.categories.GetEntryItemWidget(index)

            # If a category is currently active, then it's likely to of not updated its cached category data (Only
            # happens when the active category is switched). To account for this, make sure the active category is
            # checked differently by scanning the current variable entries
            if category is self.editor_ui.categories.active_entry:
                logger.Log("Scanning variables...")
                self.StoreActiveData(category)

            cat_name, cat_description = category.Get()

            # Since we store the variable entries as a list while editing, we need to convert it back into
            # a dict which is a more suitable representation
            cat_data = {}
            for entry in category.GetData():
                cat_data.update(entry)

            data_to_export[cat_name] = cat_data

        return data_to_export

    def Export(self):
        logger.Log(f"Exporting Variables")

        # Collect the table data
        data_to_export = self.GetAllVariableData()

        # Write the data out
        logger.Log("Writing data to file...")
        try:
            Writer.WriteFile(
                data_to_export,
                self.file_path,
                f"# {settings.editor_data['EditorSettings']['version_string']}"
            )
            self.editor_ui.SIG_USER_SAVE.emit()
            logger.Log("File Exported!", 2)
        except Exception as exc:
            print(exc)
            logger.Log("Failed to Export!", 4)

        # Reload the project variables
        settings.LoadVariables()

    def Import(self):
        super().Import()
        logger.Log(f"Importing Variables data for: {self.file_path}")

        file_data = Reader.ReadAll(self.file_path)

        if file_data:
            # Generate entries for each category
            self.editor_ui.blockSignals(True)
            for cat_name, cat_data in file_data.items():

                # Sinc vars are stored as a dict, we need to convert them into a list for use in the editor
                var_list = []
                for var_name, var_data in cat_data.items():
                    var_list.append({var_name: var_data})
                self.editor_ui.categories.CreateEntry(cat_name, "", var_list, False, True)

            # Select the Default category by default
            self.editor_ui.categories.ChangeEntry(0)
            self.editor_ui.blockSignals(False)


