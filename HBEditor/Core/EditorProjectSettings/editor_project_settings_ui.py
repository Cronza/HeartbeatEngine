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
from HBEditor.Core.base_editor_ui import EditorBaseUI
from HBEditor.Core.EditorCommon.input_entries import *
from HBEditor.Core.EditorCommon import input_entry_handler as ieh


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
        self.category_title.setObjectName("h1")
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
        self.settings_title.setObjectName("h1")
        self.settings_tree = QtWidgets.QTreeWidget(self)
        self.settings_tree.setColumnCount(2)
        self.settings_tree.setHeaderLabels(['Name', 'Input'])
        self.settings_tree.setAutoScroll(False)
        self.settings_tree.header().setStretchLastSection(False)  # Disable to allow custom sizing
        self.settings_tree.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.settings_tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.settings_tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.settings_layout.addWidget(self.settings_title)
        self.settings_layout.addWidget(self.settings_tree)

        # Assign everything to the main widget
        self.main_layout.addWidget(self.main_resize_container)
        self.main_resize_container.addWidget(self.categories)
        self.main_resize_container.addWidget(self.settings)

        # Adjust the space allocation to favor the settings section
        self.main_resize_container.setStretchFactor(0, 0)
        self.main_resize_container.setStretchFactor(1, 1)

        #TODO: Investigate how to improve the sizing for the first col. It should be a percentage of the available space
        self.settings_tree.header().setDefaultSectionSize(self.settings_tree.header().defaultSectionSize() * 2)

        # Generate entries for each project setting and category
        self.PopulateCategories()

    def PopulateCategories(self):
        """ Populates the list of category options using the available project settings data in the core """
        self.category_list.clear()

        for category in self.core.project_settings:
            self.category_list.addItem(QtWidgets.QListWidgetItem(category))

        self.category_list.setCurrentRow(0)
        self.active_category = self.category_list.item(0)

    def SwitchCategory(self):
        """ Switch the active category by saving the current settings data, then repopulates the settings list """
        if self.active_category:
            self.UpdateProjectSettingsData()

        self.active_category = self.category_list.currentItem()
        self.PopulateSettings()

    def UpdateProjectSettingsData(self):
        """
        This updates the project settings data currently loaded by the editor, but does not save the file. If the user
        wishes to avoid saving their changes, they just need to close this editor
        """
        current_category_name = self.active_category.text()
        root = self.settings_tree.invisibleRootItem()
        for index in range(0, root.childCount()):
            name = self.settings_tree.itemWidget(root.child(index), 0).text()
            input_type = self.settings_tree.itemWidget(root.child(index), 1).GetType()
            value = self.settings_tree.itemWidget(root.child(index), 1).Get()["value"]

            self.core.project_settings[current_category_name][name]['type'] = input_type.name
            self.core.project_settings[current_category_name][name]['value'] = value

    def PopulateSettings(self):
        """ Populates the settings list based on the selected category """

        self.settings_tree.clear()

        # Loop to add all settings for the selected category. Double up the search by parsing the
        # schema as well for the data types of each setting
        selected_category = self.category_list.currentItem().text()
        for setting_name, setting_data in self.core.project_settings[selected_category].items():
            ieh.Add(
                owner=self,
                view=self.settings_tree,
                name=setting_name,
                data=setting_data,
                signal_func=self.ConnectSignals
            )

    def ConnectSignals(self, tree_item):
        """ Connects the InputEntry signals to slots within this class """
        input_widget = self.settings_tree.itemWidget(tree_item, 1)
        input_widget.SIG_USER_UPDATE.connect(self.UserUpdatedInputWidget)

    def UserUpdatedInputWidget(self, owning_tree_item: QtWidgets.QTreeWidgetItem):
        self.SIG_USER_UPDATE.emit()
