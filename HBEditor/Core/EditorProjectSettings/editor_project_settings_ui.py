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
from PyQt5 import QtWidgets, QtCore
from HBEditor.Core.settings import Settings
from HBEditor.Core.BaseClasses.base_editor_ui import EditorBaseUI
from HBEditor.Core.Primitives.input_entries import *
from HBEditor.Core.EditorProjectSettings.input_entry_resolution import InputEntryResolution
from HBEditor.Core.DataTypes.parameter_types import ParameterType


class EditorProjectSettingsUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        # Track the active category, as we need a reference to it when we switch categories
        self.active_category = None

        # Build the core editor layout object
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Allow the user to resize each column
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Category Section
        self.categories = QtWidgets.QWidget()
        self.category_layout = QtWidgets.QVBoxLayout(self)
        self.category_layout.setContentsMargins(0, 0, 0, 0)
        self.category_layout.setSpacing(0)
        self.categories.setLayout(self.category_layout)

        self.category_title = QtWidgets.QLabel(self)
        self.category_title.setText("Categories")
        self.category_list = QtWidgets.QListWidget()
        self.category_list.itemSelectionChanged.connect(self.SwitchCategory)
        self.category_layout.addWidget(self.category_title)
        self.category_layout.addWidget(self.category_list)

        # Settings Section
        self.settings = QtWidgets.QWidget()
        self.settings_layout = QtWidgets.QVBoxLayout(self)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_layout.setSpacing(0)
        self.settings.setLayout(self.settings_layout)
        self.settings_title = QtWidgets.QLabel(self)
        self.settings_title.setText("Settings")
        self.settings_table = QtWidgets.QTreeWidget(self)
        self.settings_table.setColumnCount(2)
        self.settings_table.setHeaderLabels(['Name', 'Input'])
        self.settings_table.setAutoScroll(False)
        self.settings_table.header().setStretchLastSection(False)  # Disable to allow custom sizing
        self.settings_table.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.settings_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.settings_layout.addWidget(self.settings_title)
        self.settings_layout.addWidget(self.settings_table)

        # Assign everything to the main widget
        self.main_layout.addWidget(self.main_resize_container)
        self.main_resize_container.addWidget(self.categories)
        self.main_resize_container.addWidget(self.settings)

        # Adjust the space allocation to favor the settings section
        self.main_resize_container.setStretchFactor(0, 0)
        self.main_resize_container.setStretchFactor(1, 1)

        #TODO: Investigate how to improve the sizing for the first col. It should be a percentage of the available space
        self.settings_table.header().setDefaultSectionSize(self.settings_table.header().defaultSectionSize() * 2)

        self.PopulateCategories()

    def PopulateCategories(self):
        """ Populates the list of category options using the available project settings data in the core """

        self.category_list.clear()

        for category in self.core.project_settings:
            self.category_list.addItem(QtWidgets.QListWidgetItem(category))

        self.category_list.setCurrentRow(0)
        self.active_category = self.category_list.item(0)

    def SwitchCategory(self):
        """ Switch the active category by saving the current settings data, then repopulating the settings list """

        # Only update the previous category if there is one
        if self.active_category:
            self.UpdateProjectSettingsData()

        self.active_category = self.category_list.currentItem()
        self.PopulateSettings()

    def UpdateProjectSettingsData(self):
        """
        Updates the project settings data currently loaded in the editor with the values from all active settings widgets
        """
        current_category_name = self.active_category.text()

        root = self.settings_table.invisibleRootItem()
        for index in range(0, root.childCount()):
            setting_entry = root.child(index)
            self.UpdateSetting(setting_entry, self.core.project_settings[current_category_name])

    def UpdateSetting(self, setting_entry, parent):
        """
        Given a setting widget, update the corresponding data in the project settings currently loaded by the editor.
        Recursively update all children
        """
        #@TODO: Validate this eventually when the settings have more depths
        setting_name = setting_entry.name_widget.text()
        setting_data = setting_entry.Get()

        # Use the provided base to target for the key (This compounds every time recursion happens)
        parent[setting_name] = setting_data

        # If there are any children, recurse for all of them
        if setting_entry.childCount() > 0:
            for index in range(0, setting_entry.childCount()):
                child_entry = setting_entry.child(index)
                self.UpdateSetting(child_entry, parent[setting_name])

    def PopulateSettings(self):
        """ Populates the settings list based on the selected category """

        # Clear the existing list
        self.settings_table.clear()

        # Loop through the selected and begin adding the settings that are found. Double up the search by parsing the
        # schema as well for the data types of each setting
        selected_category = self.category_list.currentItem().text()
        for setting_name, setting_data in self.core.project_settings[selected_category].items():
            self.AddSetting(setting_name, setting_data, self.core.project_settings_schema[selected_category])

    def AddSetting(self, name, data, schema_data, parent=None):
        """ Creates a widget representing the name and inputs for the given setting. Recursively adds all children """

        # If there is explicitly no matching schema, then don't show the input widget
        if schema_data[name]:
            # Convert the scheme type string into an actual parameter type
            data_type = ParameterType[schema_data[name]]

            # Create the widget, and update it's info
            new_entry = self.CreateEntryWidget(data, data_type)
            new_entry.name_widget.setText(name)

            # Dropdown widgets initialize earlier with a list, and accept single strings through 'Set'. Skip this init
            if data_type != ParameterType.CUST_Resolution:
                new_entry.Set(data)

            if not parent:
                self.settings_table.addTopLevelItem(new_entry)
            else:
                self.settings_table.parent.addChild(new_entry)

            # Assign the appropriate components to the right columns
            self.settings_table.setItemWidget(new_entry, 0, new_entry.name_widget)
            self.settings_table.setItemWidget(new_entry, 1, new_entry.input_container)

            # Only recurse if there is data to recurse through
            if isinstance(data, dict):
                for child_name, child_data in data:
                    self.AddSetting(child_name, child_data, schema_data[name], new_entry)

    def CreateEntryWidget(self, data, data_type):
        """ Create a specialized entry widget based on the provided ParameterType """
        if data_type == ParameterType.String:
            return InputEntryText(None)
        elif data_type == ParameterType.Bool:
            return InputEntryBool(None)
        elif data_type == ParameterType.Int:
            return InputEntryInt(None)
        elif data_type == ParameterType.Vector2:
            return InputEntryTuple(None)
        elif data_type == ParameterType.Paragraph:
            return InputEntryParagraph(None)
        elif data_type == ParameterType.Color:
            return InputEntryColor(None)
        elif data_type == ParameterType.File:
            return InputEntryFileSelector(self, "", None)
        elif data_type == ParameterType.File_Font:
            return InputEntryFileSelector(self, Settings.getInstance().supported_content_types['Font'], None)
        elif data_type == ParameterType.File_Image:
            return InputEntryFileSelector(self, Settings.getInstance().supported_content_types['Image'], None)
        elif data_type == ParameterType.Dropdown:
            return InputEntryDropdown(data, None)
        elif data_type == ParameterType.CUST_Resolution:
            return InputEntryResolution(data, self.core.project_settings)
        else:
            return None
