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
from functools import partial
from PyQt5 import QtWidgets, QtCore
from HBEditor.Core.Outliner.icon_provider import FileSystemIconProvider
from HBEditor.Core.DataTypes.file_types import FileType, FileTypeDescriptions


class FileSystemModel(QtWidgets.QFileSystemModel):
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft

        else:
            return QtWidgets.QFileSystemModel.headerData(self, section, orientation, role)


class FileSystemTree(QtWidgets.QTreeView):
    def __init__(self, parent, double_click_func, create_file_func, create_dir_func, delete_file_func, delete_dir_func):
        super().__init__(parent)

        self.setObjectName("outliner")
        self.header().setObjectName("outliner")

        # Signal Functions
        self.double_click_func = double_click_func
        self.create_file_func = create_file_func
        self.create_dir_func = create_dir_func
        self.delete_file_func = delete_file_func
        self.delete_dir_func = delete_dir_func

        # Directory view
        self.model = FileSystemModel()
        self.model.setRootPath(QtCore.QDir.rootPath())
        self.model.setReadOnly(False)
        self.setSortingEnabled(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.viewport().setAcceptDrops(True)  # Enables dragging within the scrollable area
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)
        self.setModel(self.model)
        self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        # Create and use a custom icon provider to override tree icons
        self.model.setIconProvider(FileSystemIconProvider())

        self.customContextMenuRequested.connect(self.CreateContextMenu)
        self.doubleClicked.connect(self.ItemDoubleClicked)

    def UpdateRoot(self, new_root):
        """ Updates the root of the dir tree, refreshing the file list """
        self.setRootIndex(self.model.index(new_root))

    def CreateContextMenu(self, position):
        """
        Creates a context menu for the clicked item. 'position' is provided automatically using
        the context menu signal
        """
        # Assign special options based on whether we've selected a file or folder. Take special precaution if we right
        # click empty space, or we would accidently allow renaming or deleting the content folder / root)
        selected_item = None
        context_menu = QtWidgets.QMenu()
        context_menu.setToolTipsVisible(True)

        if self.indexAt(position).isValid():
            selected_item = self.currentIndex()
            context_menu.addAction(self.CreateAction(context_menu, "Rename", "Rename the Item", partial(self.RenameItem, selected_item)))
            context_menu.addAction(self.CreateAction(context_menu, "Delete", "Delete the Item (A confirmation prompt is shown)", partial(self.DeleteItem, selected_item)))

            if self.model.isDir(selected_item):
                context_menu.addAction(self.CreateAction(context_menu, "New Folder", "Create a New Directory", partial(self.CreateItem, selected_item, None, True)))
        else:
            selected_item = self.rootIndex()
            context_menu.addAction(self.CreateAction(context_menu, "New Folder", "Create a New Directory",  partial(self.CreateItem, selected_item, None, True)))

        if self.model.isDir(selected_item):
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
                        partial(self.CreateItem, selected_item, file_type, False)
                    ))

            context_menu.addMenu(create_menu)

        # Since this menu is launched via a signal (instead of via a button), we need an extra step to spawn
        # it at the right screen location
        context_menu.exec_(self.viewport().mapToGlobal(position))

    def CreateAction(self, menu, action_name, action_tooltip, action_func):
        """ Helper function that simplifies creating menu actions """
        new_option = QtWidgets.QWidgetAction(menu)
        new_option.setText(action_name)
        new_option.setToolTip(action_tooltip)

        if action_func: #debug
            new_option.triggered.connect(action_func)
        return new_option

    def RenameItem(self, selected_item):
        """ Enables renaming for the currently selected item """
        #@TODO: If the user renames a file that has an open editor, update the editor as well
        self.edit(selected_item)

    def CreateItem(self, selected_item, file_type, is_dir):
        """
        Calls the provided 'create<type>_func'. If an item was successfully created, mark it for edit. Since we
        can't properly infer whether to create a directory or a file, explicitly provide it
        """
        new_item_full_path = False
        path = self.model.filePath(selected_item)
        if is_dir:
            new_item_full_path = self.create_dir_func(path)
        else:
            new_item_full_path = self.create_file_func(path, file_type.name)

        # Select the new file, and mark it for renaming
        if new_item_full_path:
            new_item = self.model.index(new_item_full_path)
            self.setCurrentIndex(new_item)
            self.edit(new_item)

    def DeleteItem(self, selected_item):
        """ Prompt the user for confirmation before proceeding with the deletion """
        selected_path = self.model.filePath(selected_item)

        result = QtWidgets.QMessageBox.question(
            self,
            "Please Confirm",
            f"Are you sure you want to delete the following item:\n\n'{selected_path}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result == QtWidgets.QMessageBox.Yes:
            if self.model.isDir(selected_item):
                was_successful = self.delete_dir_func(selected_path)
            else:
                was_successful = self.delete_file_func(selected_path)

    #--------------- Signals ---------------

    def ItemDoubleClicked(self, item: QtCore.QModelIndex):
        """
        If the double clicked item is a file, call the 'Double Click' function provided to this class, providing the
        file_path of the selected item
        """
        if not self.model.isDir(item):
            self.double_click_func(self.model.filePath(item))

    def mousePressEvent(self, event):
        """ Override the click event to clear selection if empty space was clicked """
        if not self.indexAt(event.pos()).isValid():
            self.selectionModel().clear()

        super().mousePressEvent(event)
