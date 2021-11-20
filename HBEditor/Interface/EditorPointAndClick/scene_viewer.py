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
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Interface.Menus.ActionMenu.action_menu import ActionMenu
from HBEditor.Interface.EditorDialogue.dialogue_sequence_entry import DialogueEntry

"""
The core scene viewer for the Point & Click editor. Allows the user to build scenes with interactable &
non-interactable objects    
"""
class SceneViewer(QtWidgets.QWidget):
    def __init__(self, settings, core):
        super().__init__()

        self.core = core
        self.settings = settings

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the View title
        self.title = QtWidgets.QLabel(self)
        self.title.setFont(self.settings.header_1_font)
        self.title.setStyleSheet(self.settings.header_1_color)
        self.title.setText("Scene Viewer")

        # Create a sub layout so the action bar and core view can sit side-by-side
        self.sub_layout = QtWidgets.QHBoxLayout()
        self.sub_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_layout.setSpacing(0)

        self.CreateActionBar()
        self.CreateSceneView()

        # Add the core view components together
        self.sub_layout.addWidget(self.action_toolbar)
        self.sub_layout.addWidget(self.view)

        # Add the top level components together
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.sub_layout)

        self.view.show()

    def CreateSceneView(self):
        """ Creates the core view object """
        self.scene = QtWidgets.QGraphicsScene(0, 0, 1280, 720)
        self.view = QtWidgets.QGraphicsView(self.scene)

        # DEBUG
        #pixmap = QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Background_Labs2_1280.jpg"))
        #pixmapitem = self.scene.addPixmap(pixmap)
        #pixmapitem.setPos(0, 0)
        #print(self.scene.sceneRect())

    def CreateActionBar(self):
        """ Create the action bar and populate it with each editing button """

        # Create an action menu to be used later on for adding entries to the scene viewer
        self.action_menu = ActionMenu(self.core.settings, None)

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
            f"background-color: rgb({self.core.settings.toolbar_button_background_color});\n"
        )

        # Add Entry Button (Popup Menu)
        self.add_entry_button = QtWidgets.QToolButton(self.action_toolbar)
        self.add_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Plus.png")),
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
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Minus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.remove_entry_button.setIcon(icon)
        #self.remove_entry_button.clicked.connect(self.RemoveEntry)
        self.action_toolbar_layout.addWidget(self.remove_entry_button)

        # Copy Entry Button
        self.copy_entry_button = QtWidgets.QToolButton(self.action_toolbar)
        self.copy_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Copy.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.copy_entry_button.setIcon(icon)
        #self.copy_entry_button.clicked.connect(self.CopyEntry)
        self.action_toolbar_layout.addWidget(self.copy_entry_button)

        # Move Entry Up Button
        self.move_entry_up_button = QtWidgets.QToolButton(self.action_toolbar)
        self.move_entry_up_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Up.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.move_entry_up_button.setIcon(icon)
        #self.move_entry_up_button.clicked.connect(self.MoveEntryUp)
        self.action_toolbar_layout.addWidget(self.move_entry_up_button)

        # Move Entry Down Button
        self.move_entry_down_button = QtWidgets.QToolButton(self.action_toolbar)
        self.move_entry_down_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Down.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.move_entry_down_button.setIcon(icon)
        #self.move_entry_down_button.clicked.connect(self.MoveEntryDown)
        self.action_toolbar_layout.addWidget(self.move_entry_down_button)

        # Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(20, 534, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.action_toolbar_layout.addItem(spacer)

