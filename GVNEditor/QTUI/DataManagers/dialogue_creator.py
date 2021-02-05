from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from Editor.DataManagers.dialogue_creator import DialogueCreator

class UI_DialogueCreator(QWidget):
    def __init__(self, parent, tab_manager):
        QWidget.__init__(self, parent)

        self.tab_manager = tab_manager

        # ********** Define the tab container for the dialogue creator **********
        self.TabDEditor = QtWidgets.QWidget()
        self.TabDEditor.setObjectName("TabDEditor")
        self.DEditorTabLayout = QtWidgets.QVBoxLayout(self.TabDEditor)
        self.DEditorTabLayout.setObjectName("DEditorTabLayout")

        # ********** Build the toolbar for the dialogue creator **********
        self.DEditorToolBar = QtWidgets.QFrame(self.TabDEditor)
        self.DEditorToolBar.setObjectName("DEditorToolBar")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DEditorToolBar.sizePolicy().hasHeightForWidth())
        self.DEditorToolBar.setSizePolicy(sizePolicy)
        self.DEditorToolBar.setAutoFillBackground(False)
        self.DEditorToolBar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            "    background-color: rgb(44,53,57);\n"
            "}"
        )
        self.DEditorToolBar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.DEditorToolBar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.DEditorToolbarMainLayout = QtWidgets.QHBoxLayout(self.DEditorToolBar)
        self.DEditorToolbarMainLayout.setContentsMargins(2, 2, 2, 2)
        self.DEditorToolbarMainLayout.setSpacing(0)
        self.DEditorToolbarMainLayout.setObjectName("DEditorToolbarMainLayout")

        # ********* Define each of the toolbar buttons *********
        #self.DEditorToolbarButtons = QtWidgets.QButtonGroup(self.DEditorToolbarMainLayout)
        #self.DEditorToolbarButtons.setObjectName("DEditorToolbarButtons")

        # Add Entry Button
        self.AddEntryButton = QtWidgets.QToolButton(self.DEditorToolBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AddEntryButton.sizePolicy().hasHeightForWidth())
        self.AddEntryButton.setSizePolicy(sizePolicy)
        self.AddEntryButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../EditorGraphics/Plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.AddEntryButton.setIcon(icon)
        self.AddEntryButton.setObjectName("AddEntryButton")
        #self.DEditorToolbarButtons.addButton(self.AddEntryButton)
        self.DEditorToolbarMainLayout.addWidget(self.AddEntryButton)

        # Remove Entry Button
        self.RemoveEntryButton = QtWidgets.QToolButton(self.DEditorToolBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RemoveEntryButton.sizePolicy().hasHeightForWidth())
        self.RemoveEntryButton.setSizePolicy(sizePolicy)
        self.RemoveEntryButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../../EditorGraphics/Minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.RemoveEntryButton.setIcon(icon1)
        self.RemoveEntryButton.setObjectName("RemoveEntryButton")
        #self.DEditorToolbarButtons.addButton(self.RemoveEntryButton)
        self.DEditorToolbarMainLayout.addWidget(self.RemoveEntryButton)

        # Move Entry Up Button
        self.MoveEntryUpButton = QtWidgets.QToolButton(self.DEditorToolBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MoveEntryUpButton.sizePolicy().hasHeightForWidth())
        self.MoveEntryUpButton.setSizePolicy(sizePolicy)
        self.MoveEntryUpButton.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("../../EditorGraphics/Up.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.MoveEntryUpButton.setIcon(icon2)
        self.MoveEntryUpButton.setObjectName("MoveEntryUpButton")
        self.DEditorToolbarMainLayout.addWidget(self.MoveEntryUpButton)

        # Move Entry Down Button
        self.MoveEntryDownButton = QtWidgets.QToolButton(self.DEditorToolBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MoveEntryDownButton.sizePolicy().hasHeightForWidth())
        self.MoveEntryDownButton.setSizePolicy(sizePolicy)
        self.MoveEntryDownButton.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("../../EditorGraphics/Down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.MoveEntryDownButton.setIcon(icon3)
        self.MoveEntryDownButton.setObjectName("MoveEntryDownButton")
        self.DEditorToolbarMainLayout.addWidget(self.MoveEntryDownButton)

        # ********** Create Dialogue Table Container **********
        spacerItem = QtWidgets.QSpacerItem(534, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.DEditorToolbarMainLayout.addItem(spacerItem)
        self.DialogueTable = QtWidgets.QTableView(self.TabDEditor)
        self.DialogueTable.setObjectName("DialogueTable")

        # ********** Add All Major Pieces to Dialogue Tab **********
        self.DEditorTabLayout.addWidget(self.DEditorToolBar)
        self.DEditorTabLayout.addWidget(self.DialogueTable)

        # ********** Add the Dialogue Tab to the Tab Manager **********
        self.tab_manager.addTab(self.TabDEditor, "")
