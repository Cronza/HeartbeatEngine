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
import copy
from PyQt6 import QtWidgets, QtGui, QtCore
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.ActionMenu.action_menu import ActionMenu
from HBEditor.Core.EditorCommon.DetailsPanel.base_source_entry import SourceEntry
from HBEditor.Core.EditorUtilities import action_data as ad
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core import settings


class DialogueSequencePanel(QtWidgets.QWidget):
    """
    The core U.I class for the dialogue sequence panel. This contains all logic for generating, moving and removing
    any and all child widgets pertaining to the panel.

    Attributes
        SIG_USER_UPDATE: - Signal that fires whenever something was modified by the user in this panel
    """
    SIG_USER_UPDATE = QtCore.pyqtSignal()

    def __init__(self, ed_core):
        super().__init__()

        self.ed_core = ed_core

        # Create an action menu to be used later on for adding entries to the sequence
        self.action_menu = ActionMenu(self.AddEntry, FileType.Dialogue)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the View title
        self.title = QtWidgets.QLabel(self)
        self.title.setText("Dialogue Sequence")
        self.title.setObjectName("h1")

        # Create the toolbar
        self.main_toolbar = QtWidgets.QToolBar()

        # Add Entry Button (Popup Menu)
        self.add_entry_button = QtWidgets.QToolButton(self.main_toolbar)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("EditorContent:Icons/Plus.png"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off
        )
        self.add_entry_button.setIcon(icon)
        self.add_entry_button.setMenu(self.action_menu)
        self.add_entry_button.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.main_toolbar.addWidget(self.add_entry_button)

        # Remove Entry Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Minus.png")),
            "Remove Entry",
            self.RemoveEntry
        )

        # Copy Entry Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Copy.png")),
            "Copy Entry",
            self.CopyEntry
        )

        # Build the Sequence
        self.sequence_list = DialogueSequence(self)
        self.sequence_list.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable editing
        self.sequence_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)  # Disable multi-selection
        self.sequence_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)  # Disables cell selection
        self.sequence_list.setResizeMode(QtWidgets.QListWidget.ResizeMode.Adjust)
        self.sequence_list.setDragEnabled(True)
        self.sequence_list.setDragDropMode(QtWidgets.QTableWidget.DragDropMode.InternalMove)
        self.sequence_list.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.sequence_list.setDropIndicatorShown(False)
        self.sequence_list.setAcceptDrops(True)
        self.sequence_list.itemSelectionChanged.connect(self.ed_core.UpdateActiveEntry)

        # 'outline: none;' doesn't work for table widgets seemingly, so I can't use CSS to disable the
        # focus border. Thus, we do it the slightly more tragic way
        self.sequence_list.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        # ********** Add All Major Pieces to main view layout **********
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.main_toolbar)
        self.main_layout.addWidget(self.sequence_list)
        
    def Clear(self):
        """ Deletes all data in the sequence """
        self.sequence_list.clear()

    def AddEntry(self, action_name: str, action_data: dict = None, index: int = None, skip_select: bool = False) -> 'DialogueEntry':
        """
        Given an action name, create a new entry in the dialogue sequence populating with the ACTION_DATA for that
        action. If 'action_data' is provided, populate the entry using it instead
        """
        if not action_data:
            # Load a fresh copy of the ACTION_DATA
            action_data = settings.GetActionData(action_name)
            self.SIG_USER_UPDATE.emit()

        new_item = QtWidgets.QListWidgetItem()
        if index:
            self.sequence_list.insertItem(index, new_item)
        else:
            self.sequence_list.addItem(new_item)

        new_entry = DialogueEntry(action_name, action_data, self.ed_core.UpdateActiveEntry)
        # Add unique dialogue-only parameters that wouldn't be found in the 'ACTION_DATA'
        if 'post_wait' not in new_entry.action_data:
            new_entry.action_data['post_wait'] = {
                "type": "Dropdown",
                "value": 'wait_for_input',
                "options": ["wait_for_input", "wait_until_complete", "no_wait"],
                "flags": ["editable"]
            }
        new_item.setSizeHint(new_entry.sizeHint())
        self.sequence_list.setItemWidget(new_item, new_entry)

        return new_entry

    def RemoveEntry(self):
        """ If an entry is selected, delete it from the table """
        selected_indexes = self.sequence_list.selectedIndexes()

        if selected_indexes:
            self.sequence_list.takeItem(selected_indexes[0].row())
            self.SIG_USER_UPDATE.emit()

    def CopyEntry(self):
        """ If an entry is selected, clone it and add it to the sequence """
        selection = self.GetSelectedEntry()

        if selection:
            # Get the selected index so we can place the clone next to it
            selected_index = self.sequence_list.selectedIndexes()[0].row()
            self.AddEntry(selection.action_name, selection.action_data, selected_index)
            self.SIG_USER_UPDATE.emit()

    def GetSelectedEntry(self):
        """ Returns the currently selected dialogue entry. If there isn't one, returns None """
        selected_items = self.sequence_list.selectedItems()

        if selected_items:
            # Only single selection is allowed, so only first index will be valid
            return self.sequence_list.itemWidget(selected_items[0])
        else:
            return None


class DialogueSequence(QtWidgets.QListWidget):
    """ A custom QListWidget with unique drag rendering """

    def startDrag(self, supportedActions: QtCore.Qt.DropAction) -> None:
        if supportedActions.MoveAction:
            new_drag = QtGui.QDrag(self)
            entry_widget = self.itemWidget(self.item(self.selectedIndexes()[0].row()))
            drag_image = QtGui.QPixmap(entry_widget.size())
            entry_widget.render(drag_image)  # Render the entry widget to a Pixmap
            new_drag.setPixmap(drag_image)
            new_drag.setMimeData(self.mimeData(self.selectedItems()))
            new_drag.exec(supportedActions)
        else:
            super().startDrag(supportedActions)


class DialogueEntry(QtWidgets.QWidget, SourceEntry):
    def __init__(self, action_name, action_data, select_func):
        super().__init__()
        # Allow CSS to stylize the drag visualization for this widget
        self.setObjectName("drag-source")

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store action details
        self.action_name = action_name
        self.action_data = action_data

        # ****** DISPLAY WIDGETS ******
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 0, 4)
        self.main_layout.setSpacing(0)

        self.name_widget = QtWidgets.QLabel()
        self.name_widget.setObjectName("h2")

        self.name_widget.setText(self.action_name)
        self.subtext_widget = QtWidgets.QLabel()
        self.subtext_widget.setObjectName("text-soft-italic")

        # Refresh the subtext
        self.UpdateSubtext()

        # Add everything to the layout
        self.main_layout.addWidget(self.name_widget)
        self.main_layout.addWidget(self.subtext_widget)

    def Get(self) -> dict:
        """ Returns the action data stored in this object """
        return self.action_data

    def GetName(self) -> dict:
        """ Returns the action name stored in this object """
        return self.action_name

    def UpdateSubtext(self):
        """ Updates the subtext displaying entry parameters """
        self.subtext_widget.setText(self.CompileSubtextString(self.action_data))

    def CompileSubtextString(self, req_data):
        """ Given an action_data dict, compile the previewable parameters into a user-friendly string """
        cur_string = ""
        for name, data in req_data.items():
            if "flags" in data:
                if "preview" in data["flags"]:
                    if "children" in data:
                        cur_string += f"{name}: ["
                        cur_string += self.CompileSubtextString(data['children'])
                        cur_string += "], "

                    elif "value" in data:
                        req_value = data["value"]
                        cur_string += f"{name}: {req_value}, "

        # Due to how the comma formatting is, strip it from the end of the string
        return cur_string.strip(', ')

    def Refresh(self, change_tree: list = None):
        self.UpdateSubtext()

