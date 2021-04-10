from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.action_menu import ActionMenu


class DialogueSequencePanel(QtWidgets.QWidget):
    def __init__(self, settings, ed_core):
        super().__init__()

        self.ed_core = ed_core
        self.settings = settings

        # Create an action menu to be used later on for adding entries to the sequence
        self.action_menu = ActionMenu(self.ed_core.settings, self.ed_core.AddEntry)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the View title
        self.title = QtWidgets.QLabel(self)
        self.title.setFont(self.settings.header_1_font)
        self.title.setStyleSheet(self.settings.header_1_color)
        self.title.setText("Dialogue Sequence")

        # Create the toolbar
        self.main_toolbar = QtWidgets.QFrame()
        self.main_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            "    background-color: rgb(44,53,57);\n"
            "}"
        )
        self.main_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.main_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_toolbar_layout = QtWidgets.QHBoxLayout(self.main_toolbar)
        self.main_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.main_toolbar_layout.setSpacing(0)

        # Generic button settings
        icon = QtGui.QIcon()
        button_style = (
            f"background-color: rgb({self.settings.toolbar_button_background_color});\n"
        )

        # Add Entry Button (Popup Menu)
        self.add_entry_button = QtWidgets.QToolButton(self.main_toolbar)
        self.add_entry_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_entry_button.setIcon(icon)
        self.add_entry_button.setMenu(self.action_menu)
        self.add_entry_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.main_toolbar_layout.addWidget(self.add_entry_button)

        # Remove Entry Button
        self.remove_entry_button = QtWidgets.QToolButton(self.main_toolbar)
        self.remove_entry_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_entry_button.setIcon(icon)
        self.remove_entry_button.clicked.connect(self.ed_core.RemoveEntry)
        self.main_toolbar_layout.addWidget(self.remove_entry_button)

        # Copy Entry Button
        self.copy_entry_button = QtWidgets.QToolButton(self.main_toolbar)
        self.copy_entry_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Copy.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.copy_entry_button.setIcon(icon)
        self.copy_entry_button.clicked.connect(self.ed_core.CopyEntry)
        self.main_toolbar_layout.addWidget(self.copy_entry_button)

        # Move Entry Up Button
        self.move_entry_up_button = QtWidgets.QToolButton(self.main_toolbar)
        self.move_entry_up_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Up.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.move_entry_up_button.setIcon(icon)
        self.move_entry_up_button.clicked.connect(self.ed_core.MoveEntryUp)
        self.main_toolbar_layout.addWidget(self.move_entry_up_button)

        # Move Entry Down Button
        self.move_entry_down_button = QtWidgets.QToolButton(self.main_toolbar)
        self.move_entry_down_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.move_entry_down_button.setIcon(icon)
        self.move_entry_down_button.clicked.connect(self.ed_core.MoveEntryDown)
        self.main_toolbar_layout.addWidget(self.move_entry_down_button)

        # Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(534, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.main_toolbar_layout.addItem(spacer)

        # Build the Action Sequence
        self.dialogue_table = QtWidgets.QTableWidget(self)
        self.dialogue_table.setColumnCount(1)
        self.dialogue_table.horizontalHeader().hide()
        self.dialogue_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.dialogue_table.verticalHeader().setStyleSheet(self.settings.selection_color)
        self.dialogue_table.setStyleSheet(self.settings.selection_color)
        self.dialogue_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Disable editing
        self.dialogue_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # Disable multi-selection
        self.dialogue_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Disables cell selection
        self.dialogue_table.itemSelectionChanged.connect(self.ed_core.UpdateActiveEntry)

        # ********** Add All Major Pieces to main view layout **********
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.main_toolbar)
        self.main_layout.addWidget(self.dialogue_table)

    def Clear(self):
        """ Deletes all data in the dialogue table """
        for row in range(self.dialogue_table.rowCount(), 0, -1):
            self.dialogue_table.removeRow(row - 1)
