from PyQt5 import QtWidgets, QtCore
from Editor.Interface.BaseClasses.base_editor import EditorBaseUI
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
        self.settings_table.header().setMinimumSectionSize(self.settings_table.header().minimumSectionSize() * 5)

        self.main_layout.addWidget(self.settings_table)

        # Since Dialogue Scene data is riggedly defined and limited on sort of data we need
        # to gather in this editor, let's just manually add the input entries instead of relying on a schema

        # [1] - Dialogue
        new_entry = InputEntryFileSelector(self.core.settings, self.core.logger, self, "", None)
        new_entry.name_widget.setText("Dialogue")
        self.settings_table.addTopLevelItem(new_entry)

        # Add the right components to the right columns
        self.settings_table.setItemWidget(new_entry, 0, new_entry.name_widget)
        self.settings_table.setItemWidget(new_entry, 1, new_entry.input_container)

        # [2] - Starting Background
        new_entry = InputEntryFileSelector(
            self.core.settings,
            self.core.logger,
            self,
            self.core.settings.supported_content_types['Image'],
            None
        )
        new_entry.name_widget.setText("Starting Background")
        self.settings_table.addTopLevelItem(new_entry)

        # Add the right components to the right columns
        self.settings_table.setItemWidget(new_entry, 0, new_entry.name_widget)
        self.settings_table.setItemWidget(new_entry, 1, new_entry.input_container)
