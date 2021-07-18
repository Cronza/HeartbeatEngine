from PyQt5 import QtWidgets, QtGui, QtCore
from Editor.Utilities.DataTypes.file_types import FileType, FileTypeDescriptions

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
        self.dir_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dir_tree.customContextMenuRequested.connect(self.CreateContextMenu)

        # Add everything to the main container
        self.main_layout.addWidget(self.dir_tree)

    def UpdateRoot(self, new_root):
        """ Updates the root of the dir tree, refreshing the file list """

        self.dir_tree.setRootIndex(self.dir_tree_model.index(new_root))

    def CreateContextMenu(self, position):
        """
        Creates a context menu for the clicked item. 'position' is provided automatically using
        the context menu signal
        """
        # Get the absolute path of the currently selected item
        selected_item = self.dir_tree_model.filePath(self.dir_tree.currentIndex())

        context_menu = QtWidgets.QMenu()
        context_menu.setToolTipsVisible(True)
        context_menu.addAction(self.CreateAction(context_menu, "Rename", "Rename the File", None))
        context_menu.addAction(self.CreateAction(context_menu, "Delete", "Delete the File (A confirmation prompt is shown", None))

        # Directories and files will have different context menu options (The former having create options)
        # Depending on what type the selection is, add additional options
        if self.dir_tree_model.isDir(self.dir_tree.currentIndex()):
            create_menu = QtWidgets.QMenu()
            create_menu.setToolTipsVisible(True)
            create_menu.setTitle("Create")
            for file_type in FileType:

                # Don't allow the user to create a new project settings file
                if file_type is not FileType.Project_Settings:
                    create_menu.addAction(self.CreateAction(
                        create_menu,
                        file_type.name,
                        FileTypeDescriptions.descriptions[file_type],
                        None
                    ))

            context_menu.addMenu(create_menu)

        # Since this menu is launched via a signal (instead of via a button), we need an extra step to spawn
        # it at the right screen location
        context_menu.exec_(self.dir_tree.viewport().mapToGlobal(position))

    def CreateAction(self, menu, action_name, action_tooltip, action_func):
        """ Helper function that simplifies creating menu actions """
        new_option = QtWidgets.QWidgetAction(menu)
        new_option.setText(action_name)
        new_option.setToolTip(action_tooltip)
        print(action_tooltip)

        #new_option.triggered.connect(action_func)
        return new_option
