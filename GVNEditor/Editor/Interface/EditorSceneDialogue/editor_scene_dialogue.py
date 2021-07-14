from PyQt5 import QtWidgets, QtCore
from Editor.Interface.BaseClasses.base_editor import EditorBaseUI
from Editor.Utilities.DataTypes.parameter_types import ParameterType
from Editor.Interface.Primitives.input_entry_file_selector import InputEntryFileSelector

class EditorSceneDialogueUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        # Build the core editor layout object
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.settings_table = QtWidgets.QTreeWidget(self)
        self.settings_table.setColumnCount(2)
        self.settings_table.setHeaderLabels(['Name', 'Input'])
        self.settings_table.setAutoScroll(False)
        self.settings_table.header().setFont(self.core.settings.button_font)
        self.settings_table.header().setStretchLastSection(False)  # Disable to allow custom sizing
        self.settings_table.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.settings_table.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.settings_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.settings_table.header().setDefaultSectionSize(self.settings_table.header().defaultSectionSize() * 2)

        self.main_layout.addWidget(self.settings_table)

        # Since Dialogue Scene data is riggedly defined and limited on sort of data we need
        # to gather in this editor, let's just manually add the input entries instead of relying on a schema
        self.AddSetting("dialogue", None, ParameterType.File)
        self.AddSetting("starting_background", None, ParameterType.File_Image)

    def GetSceneData(self) -> dict:
        """ Builds and returns a dict of all data stored in the editor entries """
        # Note: This currently does not support recursion if any entries have child entries
        data = {}

        root = self.settings_table.invisibleRootItem()
        for index in range(0, root.childCount()):
            setting_entry = root.child(index)
            data[setting_entry.name_widget.text()] = setting_entry.Get()

        return data

    def AddSetting(self, name, data, data_type):
        """ Creates an input entry using the provided information, and adds it to the settings table """

        # Create the widget, and update it's info
        new_entry = self.CreateEntryWidget(data, data_type)
        new_entry.name_widget.setText(name)

        self.settings_table.addTopLevelItem(new_entry)

        # Assign the appropriate components to the right columns
        self.settings_table.setItemWidget(new_entry, 0, new_entry.name_widget)
        self.settings_table.setItemWidget(new_entry, 1, new_entry.input_container)

    def CreateEntryWidget(self, data, data_type):
        """ Create a specialized entry widget based on the provided ParameterType """
        if data_type == ParameterType.File:
            return InputEntryFileSelector(self.core.settings, self.core.logger, self, "", None)
        elif data_type == ParameterType.File_Image:
            return InputEntryFileSelector(self.core.settings, self.core.logger, self, self.core.settings.supported_content_types['Image'], None)
        else:
            return None
