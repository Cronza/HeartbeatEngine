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
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core.settings import Settings
from HBEditor.Core.Menus.ActionMenu.action_menu import ActionMenu
from HBEditor.Core.EditorPointAndClick.scene_view import SceneView, Scene
from HBEditor.Core.EditorPointAndClick.scene_item import SceneItem


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
        self.title.setFont(Settings.getInstance().header_1_font)
        self.title.setStyleSheet(Settings.getInstance().header_1_color)
        self.title.setText("Scene Viewer")

        # Create a sub layout so the action bar and core view can sit side-by-side
        self.sub_layout = QtWidgets.QHBoxLayout()
        self.sub_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_layout.setSpacing(0)

        self.CreateActionBar()

        # Create the core elements
        self.scene = Scene(QtCore.QRectF(0, 0, self.viewer_size[0], self.viewer_size[1]))
        self.view = SceneView(self.scene)

        # Add the core view components together
        self.sub_layout.addWidget(self.action_toolbar)
        self.sub_layout.addWidget(self.view)

        # Add the top level components together
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.sub_layout)

        self.view.show()

    def CreateActionBar(self):
        """ Create the action bar and populate it with each editing button """

        # Build the action menu which displays the options for creating things in the editor
        self.action_menu = ActionMenu(self.AddRenderable, self.core.action_data)

        # Create the frame container
        self.action_toolbar = QtWidgets.QFrame()
        self.action_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            "    background-color: rgb(44,53,57);\n"
            "}"
        )
        self.action_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.action_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.action_toolbar_layout = QtWidgets.QVBoxLayout(self.action_toolbar)
        self.action_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.action_toolbar_layout.setSpacing(0)

        # Generic button settings
        icon = QtGui.QIcon()
        button_style = (
            f"background-color: rgb({Settings.getInstance().toolbar_button_background_color});\n"
        )

        # Add Entry Button (Popup Menu)
        self.add_entry_button = QtWidgets.QToolButton(self.action_toolbar)
        self.add_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Plus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.add_entry_button.setIcon(icon)
        self.add_entry_button.setMenu(self.action_menu)
        self.add_entry_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.action_toolbar_layout.addWidget(self.add_entry_button)

        # Remove Entry Button
        self.remove_entry_button = QtWidgets.QToolButton(self.action_toolbar)
        self.remove_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Minus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.remove_entry_button.setIcon(icon)
        self.remove_entry_button.clicked.connect(self.RemoveSelectedItems)
        self.action_toolbar_layout.addWidget(self.remove_entry_button)

        # Copy Entry Button
        self.copy_entry_button = QtWidgets.QToolButton(self.action_toolbar)
        self.copy_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Copy.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.copy_entry_button.setIcon(icon)
        #self.copy_entry_button.clicked.connect(self.CopyEntry)
        self.action_toolbar_layout.addWidget(self.copy_entry_button)

        # Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(20, 534, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.action_toolbar_layout.addItem(spacer)

    def AddRenderable(self, action_data):
        # While most renderables have a "sprite" key, text renderables are an exception. Account for both options
        for req in [
            value for value in action_data["requirements"] if any([value["name"] == "sprite", value["name"] == "text"])
        ]:
            if req["name"] == "sprite":
                print("Found Sprite")
                image = QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Sprites/Placeholder.png"))
                sprite = SceneItem(
                    image,
                    action_data,
                    self.ItemHasMoved,
                    self.core.UpdateActiveSceneItem,
                    self.core.UpdateDetails
                )
                self.scene.addItem(sprite)
            else:
                print("Found Text")
            break

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

    def ItemHasMoved(self, new_pos):
        print(new_pos)

