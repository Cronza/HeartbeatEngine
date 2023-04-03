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
from typing import List
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core.ActionMenu.action_menu import ActionMenu
from HBEditor.Core.EditorPointAndClick.scene_view import SceneView, Scene
from HBEditor.Core.EditorPointAndClick.scene_items import RootItem
from HBEditor.Core.Primitives.toggleable_menu_action import ToggleableAction
from HBEditor.Core.Primitives.input_entries import InputEntryAssetSelector
from HBEditor.Core.DataTypes.file_types import FileType


class SceneViewer(QtWidgets.QWidget):
    """
    The core scene viewer for the Point & Click editor. Allows the user to build scenes with interactable &
    non-interactable objects
    """
    def __init__(self, core):
        super().__init__()

        #@TODO: Rename this to 'owner' to be more explicit
        self.core = core
        self.viewer_size = (1280, 720)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sub_layout = QtWidgets.QHBoxLayout()  # Sub layout so the action bar and core view can sit side-by-side
        self.sub_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_layout.setSpacing(0)

        # Title Bar
        self.title_bar_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.addLayout(self.title_bar_layout)

        # Title Bar - Title
        self.title = QtWidgets.QLabel(self)
        self.title.setText("Scene Viewer")
        self.title.setObjectName("h1")
        self.title_bar_layout.addWidget(self.title)
        #self.title_bar_layout.addSpacerItem(QtWidgets.QSpacerItem())

        # Title Bar - Scene Settings Button (DISABLED)
        #self.title_bar_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding))
        #self.scene_settings_button = QtWidgets.QToolButton(self)
        #self.scene_settings_button.setIcon(QtGui.QIcon(QtGui.QPixmap(":/Icons/Information.png")))
        #self.scene_settings_button.clicked.connect(self.ShowSceneSettings)
        #self.title_bar_layout.addWidget(self.scene_settings_button)

        # Toolbar
        self.action_toolbar = QtWidgets.QToolBar()
        self.action_toolbar.setOrientation(QtCore.Qt.Vertical)
        self.action_toolbar.setObjectName("horizontal")
        self.sub_layout.addWidget(self.action_toolbar)

        # Toolbar - Add Entry Button
        self.add_entry_button = QtWidgets.QToolButton(self.action_toolbar)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/Icons/Plus.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.add_entry_button.setIcon(icon)
        self.action_menu = ActionMenu(self.AddRenderable, self.core.file_type)
        self.add_entry_button.setMenu(self.action_menu)
        self.add_entry_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.action_toolbar.addWidget(self.add_entry_button)

        # Toolbar - Remove Button
        self.action_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Minus.png")),
            "Remove Entry",
            self.RemoveSelectedItems
        )

        # Toolbar - Copy Button
        self.action_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Copy.png")),
            "Copy Entry",
            self.CopyRenderable
        )
        self.action_toolbar.addSeparator()

        # Toolbar - Lock button
        self.lock_button = ToggleableAction(
            "Lock Entry",
            QtGui.QIcon(":/Icons/Lock.png")
        )
        self.lock_button.clicked.connect(self.LockRenderable)
        self.action_toolbar.addWidget(self.lock_button)

        self.scene = Scene(QtCore.QRectF(0, 0, self.viewer_size[0], self.viewer_size[1]))
        self.scene.selectionChanged.connect(self.UpdateActiveSceneItem)
        self.view = SceneView(self.scene)
        self.sub_layout.addWidget(self.view)
        self.main_layout.addLayout(self.sub_layout)


        
        self.view.show()

    def AddRenderable(self, action_data, skip_selection: bool = False) -> RootItem:
        """ Add an item to the scene view. Return the newly created item """
        new_item = RootItem(
            action_data=action_data,
            select_func=self.UpdateActiveSceneItem
        )

        self.scene.addItem(new_item)

        # Generate after adding to the scene so children have the scene transform context
        new_item.GenerateChildren()

        # The root item dictates the tree's general z-order. It needs to inherit the z-order of the top-most child
        # Note: The root only ever has a single child
        new_item.UpdateZValue()

        # Select the new item instead of waiting for the user to do it
        if not skip_selection:
            self.scene.clearSelection()
            new_item.setSelected(True)

        return new_item

    def CopyRenderable(self):
        """ Clones the active renderable, adding it to the scene view. If multiple are selected, clone each one """
        selected_items = self.scene.selectedItems()

        if selected_items:
            for item in selected_items:
                self.AddRenderable(copy.deepcopy(item.action_data))

    def LockRenderable(self):
        """ Toggles the locked state of the selected items, preventing their movement with the cursor """
        selected_items = self.scene.selectedItems()
        lock = True
        skip_toggle = False
        if selected_items:
            # Since locking multiple objects at once is supported,  there is a possibility where each selected object
            # has a different lock state (Some locked, some not). In these cases, we need to preprocess the selected
            # items and see if any are locked. If any are locked, then we should unlock them all
            for item in selected_items:
                if item.GetLocked():
                    lock = False
                    break

            for item in selected_items:
                success = item.SetLocked(lock)
                if not success:
                    skip_toggle = True

            if not skip_toggle:
                # Refresh the lock button state
                if lock:
                    self.lock_button.Toggle(True)
                else:
                    self.lock_button.Toggle(False)

    def RemoveSelectedItems(self):
        """ Removes all currently selected items """
        selected_items = self.scene.selectedItems()

        if selected_items:
            for item in selected_items:
                self.scene.removeItem(item)

            self.core.UpdateActiveSceneItem(None)

    def GetSceneItems(self) -> List[RootItem]:
        """ Returns a list of all RootItems in the SceneView """
        return [item for item in self.scene.items() if isinstance(item, RootItem)]

    def UpdateActiveSceneItem(self):
        selected_items = self.scene.selectedItems()
        lock = False
        if selected_items:
            for item in selected_items:
                if item.GetLocked():
                    lock = True
                    break

        self.lock_button.Toggle(lock)

        # Inform the core so it can take additional actions
        self.core.UpdateActiveSceneItem(selected_items)


class DialogSceneSettings(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        # Hide the OS header to lock its position
        self.setWindowTitle("Scene Settings")
        self.setWindowIcon(QtGui.QIcon(":/Icons/Engine_Logo.png"))
        self.resize(400, 300)
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Background
        self.background_layout = QtWidgets.QHBoxLayout(self)
        self.background_label = QtWidgets.QLabel("Background")
        self.background_layout.addWidget(self.background_label)
        self.background_input = InputEntryAssetSelector({}, None, {FileType.Asset_Image})
        self.background_layout.addWidget(self.background_input)
        self.main_layout.addLayout(self.background_layout)

        # Description
        self.description_label = QtWidgets.QLabel("Description")
        self.main_layout.addWidget(self.description_label)
        self.description_input = QtWidgets.QPlainTextEdit(self)
        self.description_input.setPlaceholderText("A place to put a high-level description of the scene...")
        self.main_layout.addWidget(self.description_input)

        # Confirmation Buttons
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)
