from PyQt5 import QtWidgets, QtGui, QtCore
from Editor.Interface.EditorDialogue.dialogue_branches_entry import BranchesEntry
from Editor.Interface.EditorDialogue.dialogue_branches_edit_prompt import EditBranchPrompt

class BranchesPanel(QtWidgets.QWidget):
    def __init__(self, settings, ed_core):
        super().__init__()

        self.ed_core = ed_core
        self.settings = settings

        self.branches_layout = QtWidgets.QVBoxLayout(self)
        self.branches_layout.setContentsMargins(0, 0, 0, 0)
        self.branches_layout.setSpacing(0)

        # Create title
        self.branches_title = QtWidgets.QLabel(self)
        self.branches_title.setFont(self.settings.header_1_font)
        self.branches_title.setStyleSheet(settings.header_1_color)
        self.branches_title.setText("Branches")

        # Create the toolbar
        self.branches_toolbar = QtWidgets.QFrame(self)
        self.branches_toolbar.setAutoFillBackground(False)
        self.branches_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            f"   background-color: rgb({self.settings.toolbar_background_color});\n"
            "}"
        )
        self.branches_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.branches_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.branches_toolbar_layout = QtWidgets.QHBoxLayout(self.branches_toolbar)
        self.branches_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.branches_toolbar_layout.setSpacing(0)

        # Generic button settings
        icon = QtGui.QIcon()
        button_style = (
            f"background-color: rgb({self.settings.toolbar_button_background_color});\n"
        )

        # Add Branch Button
        self.add_entry_button = QtWidgets.QToolButton(self.branches_toolbar)
        self.add_entry_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_entry_button.setIcon(icon)
        self.add_entry_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.branches_toolbar_layout.addWidget(self.add_entry_button)

        # Remove Branch Button
        self.remove_entry_button = QtWidgets.QToolButton(self.branches_toolbar)
        self.remove_entry_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_entry_button.setIcon(icon)
        self.remove_entry_button.clicked.connect(self.ed_core.RemoveEntry)
        self.branches_toolbar_layout.addWidget(self.remove_entry_button)

        # Create search filter
        #self.branches_filter = QtWidgets.QLineEdit(self.branches_toolbar)
        #self.branches_filter.setPlaceholderText("filter...")
        #self.branches_toolbar_layout.addWidget(self.branches_filter)

        # Create Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.branches_toolbar_layout.addItem(spacer)

        # Create Details List
        self.branches_list = QtWidgets.QListWidget(self)
        self.branches_list.itemDoubleClicked.connect(self.EditBranch)

        # ********** Add All Major Pieces to details layout **********
        self.branches_layout.addWidget(self.branches_title)
        self.branches_layout.addWidget(self.branches_toolbar)
        self.branches_layout.addWidget(self.branches_list)

        self.TestPopulate()

    def TestPopulate(self):
        for i in range(0, 3):
            # Create the list item container
            list_item = QtWidgets.QListWidgetItem()
            self.branches_list.addItem(list_item)

            # Create the core part of the entry
            new_entry = BranchesEntry("test", self.settings, None)
            self.branches_list.setItemWidget(list_item, new_entry)

            # Adjust the size hint of the item container to match the contents
            list_item.setSizeHint(new_entry.sizeHint())

    def EditBranch(self):
        print('Oh yeah, its dev time')
        selection = self.branches_list.selectedItems()[0]
        branch_entry = self.branches_list.itemWidget(selection)

        # Retrieves the tuple data of 'branch name' and 'branch description'
        data = self.branches_list.itemWidget(selection).Get()

        # Create the prompt object, providing the selected branch's data
        prompt = EditBranchPrompt(data[0], data[1])

        # 0 = dialog was cancelled, 1 = dialogue was accepted
        if prompt.exec() == 1:
            new_data = prompt.Get()
            branch_entry.Set(new_data)

            self.ResizeListEntry(selection, branch_entry)




        # Resize the row to fit any contents it has
        #self.branches_list.resizeRowToContents(new_entry_row)
        #self.branches_list.updateGeometry()
        #self.branches_list.setResizeMode(QtWidgets.QListWidget.Fixed)
        #self.branches_list.resizeMode()

    def ResizeListEntry(self, list_item_container, list_item_object):
        """ Resize the provided list entry to match the size of it's contents """

        list_item_container.setSizeHint(list_item_object.sizeHint())