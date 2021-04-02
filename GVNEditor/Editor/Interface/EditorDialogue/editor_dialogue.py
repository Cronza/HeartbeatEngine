from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.details_panel import Details
from Editor.Interface.EditorDialogue.dialogue_branches_panel import Branches
from Editor.Interface.Generic.action_menu import ActionMenu


class EditorDialogueUI(QtWidgets.QWidget):
    def __init__(self, ed_core):
        super().__init__()

        self.ed_core = ed_core

        # Create an action menu to be used later on
        self.action_menu = ActionMenu(self.ed_core.settings, self.ed_core.AddEntry)

        # Build the core editor layout object
        self.central_grid_layout = QtWidgets.QGridLayout(self)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        #self.CreateOutliner()
        self.CreateBranches()
        self.CreateMainView()
        self.CreateDetails()

        # Allow the user to resize each column
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Add everything to the editor interface
        self.central_grid_layout.addWidget(self.main_resize_container, 0, 0)
        self.main_resize_container.addWidget(self.branches)
        self.main_resize_container.addWidget(self.main_view)
        self.main_resize_container.addWidget(self.details)

        # Adjust the main view so its consuming as much space as possible
        self.main_resize_container.setStretchFactor(1, 10)

    def CreateMainView(self):
        self.main_view = QtWidgets.QWidget()
        self.main_view_layout = QtWidgets.QVBoxLayout(self.main_view)
        self.main_view_layout.setContentsMargins(0,0,0,0)
        self.main_view_layout.setSpacing(0)

        # Create the View title
        self.view_title = QtWidgets.QLabel(self.main_view)
        self.view_title.setFont(self.ed_core.settings.header_1_font)
        self.view_title.setStyleSheet(self.ed_core.settings.header_1_color)
        self.view_title.setText("Dialogue Sequence")

        # Create the toolbar
        self.main_view_toolbar = QtWidgets.QFrame()
        self.main_view_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            "    background-color: rgb(44,53,57);\n"
            "}"
        )
        self.main_view_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.main_view_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_view_toolbar_layout = QtWidgets.QHBoxLayout(self.main_view_toolbar)
        self.main_view_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.main_view_toolbar_layout.setSpacing(0)

        # Generic button settings
        icon = QtGui.QIcon()
        button_style = (
            f"background-color: rgb({self.ed_core.settings.toolbar_button_background_color});\n"
        )

        # Add Entry Button (Popup Menu)
        self.add_entry_button = QtWidgets.QToolButton(self.main_view_toolbar)
        self.add_entry_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_entry_button.setIcon(icon)
        self.add_entry_button.setMenu(self.action_menu)
        self.add_entry_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.main_view_toolbar_layout.addWidget(self.add_entry_button)

        # Remove Entry Button
        self.remove_entry_button = QtWidgets.QToolButton(self.main_view_toolbar)
        self.remove_entry_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_entry_button.setIcon(icon)
        self.remove_entry_button.clicked.connect(self.ed_core.RemoveEntry)
        self.main_view_toolbar_layout.addWidget(self.remove_entry_button)

        # Copy Entry Button
        self.copy_entry_button = QtWidgets.QToolButton(self.main_view_toolbar)
        self.copy_entry_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Copy.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.copy_entry_button.setIcon(icon)
        self.copy_entry_button.clicked.connect(self.ed_core.CopyEntry)
        self.main_view_toolbar_layout.addWidget(self.copy_entry_button)

        # Move Entry Up Button
        self.move_entry_up_button = QtWidgets.QToolButton(self.main_view_toolbar)
        self.move_entry_up_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Up.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.move_entry_up_button.setIcon(icon)
        self.move_entry_up_button.clicked.connect(self.ed_core.MoveEntryUp)
        self.main_view_toolbar_layout.addWidget(self.move_entry_up_button)

        # Move Entry Down Button
        self.move_entry_down_button = QtWidgets.QToolButton(self.main_view_toolbar)
        self.move_entry_down_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.move_entry_down_button.setIcon(icon)
        self.move_entry_down_button.clicked.connect(self.ed_core.MoveEntryDown)
        self.main_view_toolbar_layout.addWidget(self.move_entry_down_button)

        # Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(534, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.main_view_toolbar_layout.addItem(spacer)

        # Build the Action Sequence
        self.dialogue_sequence = QtWidgets.QTableWidget(self.main_view)
        self.dialogue_sequence.setColumnCount(1)
        self.dialogue_sequence.horizontalHeader().hide()
        self.dialogue_sequence.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.dialogue_sequence.verticalHeader().setStyleSheet(self.ed_core.settings.selection_color)
        self.dialogue_sequence.setStyleSheet(self.ed_core.settings.selection_color)
        self.dialogue_sequence.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) # Disable editing
        self.dialogue_sequence.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection) # Disable multi-selection
        self.dialogue_sequence.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows) # Disables cell selection
        self.dialogue_sequence.itemSelectionChanged.connect(self.ed_core.UpdateActiveEntry)

        # ********** Add All Major Pieces to main view layout **********
        self.main_view_layout.addWidget(self.view_title)
        self.main_view_layout.addWidget(self.main_view_toolbar)
        self.main_view_layout.addWidget(self.dialogue_sequence)

    def CreateOutliner(self):
        self.outliner = QtWidgets.QWidget()
        self.outliner_layout = QtWidgets.QVBoxLayout(self.outliner)
        self.outliner_layout.setContentsMargins(0, 0, 0, 0)
        self.outliner_layout.setSpacing(0)

        # Create the outliner title
        self.outliner_title = QtWidgets.QLabel(self.outliner)
        self.outliner_title.setFont(self.ed_core.settings.header_1_font)
        self.outliner_title.setStyleSheet(self.ed_core.settings.header_1_color)
        self.outliner_title.setText("Branches")

        # Generic button settings
        icon = QtGui.QIcon()
        button_style = (
            f"background-color: rgb({self.ed_core.settings.toolbar_button_background_color});\n"
        )

        # Create the outliner toolbar
        self.outliner_toolbar = QtWidgets.QFrame(self)
        self.outliner_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            f"   background-color: rgb({self.ed_core.settings.toolbar_background_color});\n"
            "}"
        )
        self.outliner_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.outliner_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.outliner_toolbar_layout = QtWidgets.QHBoxLayout(self.outliner_toolbar)
        self.outliner_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.outliner_toolbar_layout.setSpacing(0)

        # Add Branch Button
        self.add_branch_button = QtWidgets.QToolButton(self.outliner_toolbar)
        self.add_branch_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_branch_button.setIcon(icon)
        self.outliner_toolbar_layout.addWidget(self.add_branch_button)

        ## Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.outliner_toolbar_layout.addItem(spacer)

        # Create the branch list
        self.branch_list = QtWidgets.QListWidget(self.outliner)

        # ********** Add All Major Pieces to the outliner layout **********
        self.outliner_layout.addWidget(self.outliner_title)
        self.outliner_layout.addWidget(self.outliner_toolbar)
        self.outliner_layout.addWidget(self.branch_list)

    def CreateBranches(self):
        """ Create the branches panel """
        self.branches = Branches(self.ed_core.settings)

    def CreateDetails(self):
        """ Create the details panel using the generic details object """
        self.details = Details(self.ed_core.settings)

