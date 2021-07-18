from PyQt5 import QtWidgets, QtGui, QtCore


class OutlinerUI(QtWidgets.QWidget):
    def __init__(self, core):
        super().__init__()

        self.core = core

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(0)

        # Toolbar
        self.outliner_toolbar = QtWidgets.QFrame(self)
        self.outliner_toolbar.setAutoFillBackground(False)
        self.outliner_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            f"   background-color: rgb({self.core.settings.toolbar_background_color});\n"
            "}")
        self.outliner_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.outliner_toolbar.setFrameShadow(QtWidgets.QFrame   .Raised)
        self.outliner_toolbar_layout = QtWidgets.QHBoxLayout(self.outliner_toolbar)
        self.outliner_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.outliner_toolbar_layout.setSpacing(0)

        # Generic Button Settings
        icon = QtGui.QIcon()
        button_style = (
            f"background-color: rgb({self.core.settings.toolbar_button_background_color});\n"
        )

        # Clear Log Button
        self.import_button = QtWidgets.QToolButton(self.outliner_toolbar)
        self.import_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.core.settings.ConvertPartialToAbsolutePath("Content/Icons/Plus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.import_button.setIcon(icon)

        # Add buttons to toolbar
        self.outliner_toolbar_layout.addWidget(self.import_button)
        toolbar_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.outliner_toolbar_layout.addItem(toolbar_spacer)

        # Directory view
        self.dir_tree_model = QtWidgets.QFileSystemModel()
        self.dir_tree_model.setRootPath(QtCore.QDir.rootPath())
        self.dir_tree_model.setReadOnly(False)
        self.dir_tree = QtWidgets.QTreeView()
        self.dir_tree.setSortingEnabled(True)
        self.dir_tree.setDragEnabled(True)
        self.dir_tree.setDropIndicatorShown(True)
        self.dir_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.dir_tree.viewport().setAcceptDrops(True)  # Enables dragging within the scrollable area
        self.dir_tree.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.dir_tree.setModel(self.dir_tree_model)

        # Add everything to the main container
        self.main_layout.addWidget(self.outliner_toolbar)
        self.main_layout.addWidget(self.dir_tree)

    def UpdateRoot(self, new_root):
        """ Updates the root of the dir tree, refreshing the file list """

        self.dir_tree.setRootIndex(self.dir_tree_model.index(new_root))
