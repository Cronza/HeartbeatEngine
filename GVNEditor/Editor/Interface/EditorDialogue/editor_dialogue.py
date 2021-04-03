from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.details_panel import DetailsPanel
from Editor.Interface.EditorDialogue.dialogue_branches_panel import BranchesPanel
from Editor.Interface.EditorDialogue.dialogue_sequence_panel import DialogueSequencePanel


class EditorDialogueUI(QtWidgets.QWidget):
    def __init__(self, ed_core):
        super().__init__()

        self.ed_core = ed_core

        # Build the core editor layout object
        self.central_grid_layout = QtWidgets.QGridLayout(self)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        #self.CreateOutliner()
        self.CreateBranchesPanel()
        self.CreateDialogueSequencePanel()
        self.CreateDetailsPanel()

        # Allow the user to resize each column
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Add everything to the editor interface
        self.central_grid_layout.addWidget(self.main_resize_container, 0, 0)
        self.main_resize_container.addWidget(self.branches)
        self.main_resize_container.addWidget(self.dialogue_sequence)
        self.main_resize_container.addWidget(self.details)

        # Adjust the main view so its consuming as much space as possible
        self.main_resize_container.setStretchFactor(1, 10)


    """
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
    """
    def CreateDialogueSequencePanel(self):
        """
        Create the dialogue sequence panel. Since this panel is fundamental to the dialogue editor,
        it needs a reference to the editor core to access toolbar functions
        """
        self.dialogue_sequence = DialogueSequencePanel(self.ed_core.settings, self.ed_core)

    def CreateBranchesPanel(self):
        """
        Create the branches panel. Since this panel is fundamental to the dialogue editor,
        it needs a reference to the editor core to access toolbar functions
        """
        self.branches = BranchesPanel(self.ed_core.settings, self.ed_core)

    def CreateDetailsPanel(self):
        """
        Create the details panel using the generic details object. Since this panel is generic,
        it functions independently of whether it has a reference to the editor core
        """
        self.details = DetailsPanel(self.ed_core.settings)

