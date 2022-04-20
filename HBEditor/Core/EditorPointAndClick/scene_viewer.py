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
from enum import Enum
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core.settings import Settings
from HBEditor.Core.Menus.ActionMenu.action_menu import ActionMenu
from HBEditor.Core.EditorPointAndClick.scene_view import SceneView, Scene
from HBEditor.Core.EditorPointAndClick.scene_items import SpriteItem, TextItem


class SceneItemTypes(Enum):
    Sprite = 1
    Text = 2


class SceneViewer(QtWidgets.QWidget):
    """
    The core scene viewer for the Point & Click editor. Allows the user to build scenes with interactable &
    non-interactable objects
    """
    def __init__(self, core):
        super().__init__()

        self.core = core

        self.viewer_size = (1280, 720)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the View title
        self.title = QtWidgets.QLabel(self)
        self.title.setText("Scene Viewer")
        self.title.setObjectName("h1")

        # Create a sub layout so the action bar and core view can sit side-by-side
        self.sub_layout = QtWidgets.QHBoxLayout()
        self.sub_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_layout.setSpacing(0)

        # Build the action menu which displays the options for creating things in the editor
        self.action_menu = ActionMenu(self.AddRenderable, self.core.action_data)
        self.action_toolbar = QtWidgets.QToolBar()
        self.action_toolbar.setOrientation(QtCore.Qt.Vertical)

        # Generic button settings
        icon = QtGui.QIcon()

        # Add Entry Button (Popup Menu)
        self.add_entry_button = QtWidgets.QToolButton(self.action_toolbar)
        icon.addPixmap(
            QtGui.QPixmap(":/Icons/Plus.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.add_entry_button.setIcon(icon)
        self.add_entry_button.setMenu(self.action_menu)
        self.add_entry_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.action_toolbar.addWidget(self.add_entry_button)

        # Remove Entry Button
        self.action_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Minus.png")),
            "Remove Entry",
            self.RemoveSelectedItems
        )

        # Copy Entry Button
        self.action_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Copy.png")),
            "Copy Entry",
            self.CopyRenderable
        )

        # Create the core elements
        self.scene = Scene(QtCore.QRectF(0, 0, self.viewer_size[0], self.viewer_size[1]))
        self.view = SceneView(self.scene)

        # Add everything together
        self.sub_layout.addWidget(self.action_toolbar)
        self.sub_layout.addWidget(self.view)
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.sub_layout)

        self.view.show()

    def AddRenderable(self, action_data) -> bool:
        """ Add an item to the scene view """
        for actions in self.core.possible_actions.values():
            if action_data["action_name"] in actions:
                item_type = actions[action_data["action_name"]]

                if item_type == "sprite":
                    image = QtGui.QPixmap(":/Sprites/Placeholder.png")
                    sprite = SpriteItem(
                        image,
                        action_data,
                        self.core.UpdateActiveSceneItem,
                        self.core.UpdateDetails
                    )
                    self.scene.addItem(sprite)
                    sprite.Refresh()  # Force a refresh as the renderable doesn't use the action data right away
                    return True

                elif item_type == "text":
                    text = TextItem(
                        "Default",
                        action_data,
                        self.core.UpdateActiveSceneItem,
                        self.core.UpdateDetails
                    )
                    self.scene.addItem(text)
                    text.Refresh()  # Force a refresh as the renderable doesn't use the action data right away
                    return True

        return False

    def CopyRenderable(self):
        """ Clones the active renderable, adding it to the scene view. If multiple are selected, clone each one """
        selected_items = self.scene.selectedItems()

        if selected_items:
            for item in selected_items:
                self.AddRenderable(copy.deepcopy(item.action_data))


    def GetSelectedItems(self):
        """ Returns all currently selected QGraphicsItems. If there aren't any, returns None """

        selected_items = self.scene.selectedItems()
        if not selected_items:
            return None

        return selected_items

    def RemoveSelectedItems(self):
        """ Removes all currently selected items """
        selected_items = self.GetSelectedItems()

        if selected_items:
            for item in selected_items:
                self.scene.removeItem(item)

            self.core.UpdateActiveSceneItem()
