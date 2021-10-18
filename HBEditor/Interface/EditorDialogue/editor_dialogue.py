from PyQt5 import QtWidgets
from HBEditor.Interface.BaseClasses.base_editor import EditorBaseUI
from HBEditor.Interface.DetailsPanel.details_panel import DetailsPanel
from HBEditor.Interface.EditorDialogue.dialogue_branches_panel import BranchesPanel
from HBEditor.Interface.EditorDialogue.dialogue_sequence_panel import DialogueSequencePanel


class EditorDialogueUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        # Build the core editor layout object
        self.central_grid_layout = QtWidgets.QGridLayout(self)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        self.CreateBranchesPanel()
        self.CreateDialogueSequencePanel()
        self.CreateDetailsPanel()

        # The dialogue editor makes use of the "Choice" input widget, which requires a reference
        # to the branches list
        self.details.branch_list = self.branches.branches_list

        # Allow the user to resize each column
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Add everything to the editor interface
        self.central_grid_layout.addWidget(self.main_resize_container, 0, 0)
        self.main_resize_container.addWidget(self.branches)
        self.main_resize_container.addWidget(self.dialogue_sequence)
        self.main_resize_container.addWidget(self.details)

        # Adjust the main view so its consuming as much space as possible
        self.main_resize_container.setStretchFactor(1, 10)

    def CreateDialogueSequencePanel(self):
        """
        Create the dialogue sequence panel. Since this panel is fundamental to the dialogue editor,
        it needs a reference to the editor core to access toolbar functions
        """
        self.dialogue_sequence = DialogueSequencePanel(self.core.settings, self.core)

    def CreateBranchesPanel(self):
        """
        Create the branches panel. Since this panel is fundamental to the dialogue editor,
        it needs a reference to the editor core to access toolbar functions
        """
        self.branches = BranchesPanel(self.core.settings, self.core)

    def CreateDetailsPanel(self):
        """
        Create the details panel using the generic details object. Since this panel is generic,
        it functions independently of whether it has a reference to the editor core
        """
        self.details = DetailsPanel(self.core.settings, self.core.logger)

