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
from enum import Enum
from functools import partial
from PyQt6 import QtWidgets, QtGui, QtCore
from HBEditor.Core.DataTypes.file_types import FileType, FileTypeIcons
from HBEditor.Core import settings
from HBEditor.Core.Logger.logger import Logger


class OutlinerUI(QtWidgets.QWidget):
    def __init__(self, core):
        super().__init__()

        self.core = core

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Toolbar
        self.toolbar = QtWidgets.QToolBar(self)
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toolbar.setObjectName("vertical")

        # Toolbar - Import Button
        self.import_button = QtWidgets.QToolButton(self)
        self.import_button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.import_button.setText(" Import")
        self.import_button.setIcon(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Import")))
        self.import_button.clicked.connect(self.core.ImportAsset)
        self.toolbar.addWidget(self.import_button)
        self.toolbar.addSeparator()

        # Toolbar - Quick Access Buttons
        self.CreateQuickAccessButtons()

        # Asset View
        self.asset_list = AssetList(self)
        self.asset_list.customContextMenuRequested.connect(self.CreateContextMenu)
        self.asset_list.itemDoubleClicked.connect(self.ProcessAssetDoubleClick)
        self.asset_list.SIG_DROP_INT.connect(self.core.MoveAsset)
        self.asset_list.SIG_DROP_EXT.connect(self.core.ImportAsset)

        # Add everything to the main container
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.asset_list)

    def CreateContextMenu(self, pos):
        use_asset_menu = self.asset_list.itemAt(pos)  # Alter the menu if the user triggers it while hovering an asset
        asset_is_selected = len(self.asset_list.selectedItems()) > 0

        context_menu = OutlinerContextMenu(self, self.core, use_asset_menu, asset_is_selected)
        context_menu.a_import.triggered.connect(self.core.ImportAsset)
        context_menu.a_rename.triggered.connect(self.core.RenameAsset)
        context_menu.a_delete.triggered.connect(self.core.DeleteAsset)
        context_menu.a_duplicate.triggered.connect(self.core.DuplicateAsset)
        context_menu.a_create_folder.triggered.connect(self.core.CreateFolder)
        context_menu.a_new_scene.triggered.connect(self.core.CreateScene)
        context_menu.a_new_dialogue.triggered.connect(self.core.CreateDialogue)
        context_menu.a_new_interface.triggered.connect(self.core.CreateInterface)
        context_menu.a_details.triggered.connect(self.ShowDetails)

        # Reveal the context menu, translating the local widget pos to a global pos
        context_menu.popup(self.asset_list.mapToGlobal(pos))

    def CreateQuickAccessButtons(self):
        """
        Create buttons representing the currently used directory tree. Clicking each button will allow the user
        to navigate back to any folder in the hierachy
        """
        # Create the initial content directory
        split_path = self.core.cur_directory.split("/")
        qa_button = QuickAccessButton(self, split_path[0])
        qa_button.setText(f"{split_path[0]}")
        qa_button.clicked.connect(partial(self.ProcessQABClick, split_path[0]))
        qa_button.SIG_DROP.connect(self.ProcessQABDrop)
        self.toolbar.addWidget(qa_button)

        # Create all other folders if applicable with an arrow seperator between them
        if len(split_path) > 1:
            for dir_index in range(1, len(split_path)):
                arrow_separator = QtWidgets.QToolButton(self.toolbar)
                arrow_separator.setArrowType(QtCore.Qt.RightArrow)
                arrow_separator.setEnabled(False)
                self.toolbar.addWidget(arrow_separator)

                qa_button = QuickAccessButton(self, "/".join(split_path[:dir_index+1]))
                qa_button.setText(f"{split_path[dir_index]}")
                qa_button.clicked.connect(partial(self.ProcessQABClick, "/".join(split_path[:dir_index+1])))
                qa_button.SIG_DROP.connect(self.ProcessQABDrop)
                self.toolbar.addWidget(qa_button)

    def ProcessQABClick(self, path: str):
        """ When a user clicks a quick access button, switch to the corresponding directory """
        self.MoveToDirectory(path)

    def ProcessQABDrop(self, paths: list, ext_files: bool):
        """
        When the user drops an asset on the Quick Access Buttons, invoke the 'Move' action if it's a project file
        or request an import if external
        """
        if ext_files:
            self.core.ImportAsset(paths)
        else:
            selection = self.asset_list.selectedItems()[0]  # Multi-select not currently supported
            self.core.MoveAssetUsingQAB(f"{self.core.cur_directory}/{selection.text()}", paths[0])

    def ProcessAssetDoubleClick(self, item: QtWidgets.QListWidgetItem):
        if item.asset_type == FileType.Folder:
            self.MoveToDirectory(f"{self.core.cur_directory}/{item.text()}")
        else:
            self.core.OpenFile(item.text())

    def AddAsset(self, asset_name: str, asset_type: FileType, thumbnail_path: str = ""):
        new_asset = OutlinerAsset(asset_name, asset_type, thumbnail_path)
        self.asset_list.addItem(new_asset)

        # Allow folders to be drop targets so assets can be rearranged in the editor
        if asset_type == FileType.Folder:
            new_asset.setFlags(new_asset.flags() | QtCore.Qt.ItemFlag.ItemIsDropEnabled)

    def RemoveAsset(self, name: str):
        asset = self.asset_list.findItems(name, QtCore.Qt.MatchFlag.MatchExactly)[0]
        self.asset_list.takeItem(self.asset_list.row(asset))
        #@TODO: Add sort update here...

    def MoveToDirectory(self, path_to_dir: str):
        self.ClearAssets()
        self.core.cur_directory = path_to_dir

        for action in self.toolbar.actions()[2:]:  # Start from after the Import button and Separator
            self.toolbar.removeAction(action)

        self.CreateQuickAccessButtons()
        self.core.Populate()

    def ClearAssets(self):
        self.asset_list.clear()

    def ShowDetails(self):
        selected_asset = self.asset_list.currentItem()
        print(selected_asset)
        info_dialog = DialogAssetInfo(
            file_name=selected_asset.asset_name,
            file_type=selected_asset.asset_type,
            rel_file_path=self.core.cur_directory,
            abs_file_path=f"{settings.user_project_dir}/{self.core.cur_directory}"
        )
        info_dialog.exec()


class AssetList(QtWidgets.QListWidget):
    SIG_DROP_INT = QtCore.pyqtSignal(object, object)
    SIG_DROP_EXT = QtCore.pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.setViewMode(QtWidgets.QListView.ViewMode.IconMode)
        self.setIconSize(QtCore.QSize(
            settings.editor_data["Outliner"]["icon_size"][0],
            settings.editor_data["Outliner"]["icon_size"][1]
        ))
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragDrop)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.setWordWrap(True)

        # We need very specific control over the rendering for 'IconMode' in order to improve the 'tile' look. This
        # requires the use of a delegate which lets us override and expand the painting
        delegate = TileDelegate(parent)
        self.setItemDelegate(delegate)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        event.acceptProposedAction()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:  # Only external files use URLs
            # Process all files to ensure they're local files (Further processing is done elsewhere). This is a list
            # of absolute paths
            processed_files = []
            for url in urls:
                if url.isLocalFile():
                    processed_files.append(url.toLocalFile())

            if processed_files:
                self.SIG_DROP_EXT.emit(processed_files)

        else:
            drop_source = self.selectedItems()[0]  # Multi-select is not currently supported
            drop_target = self.itemAt(event.pos())
            if drop_source is not None and drop_target is not None and drop_source is not drop_target:
                self.SIG_DROP_INT.emit(drop_source, drop_target)


class OutlinerAsset(QtWidgets.QListWidgetItem):
    def __init__(self, asset_name: str, asset_type: FileType, thumbnail_path: str = ""):
        super().__init__()
        self.setText(asset_name)

        self.asset_name = asset_name
        self.asset_type = asset_type
        try:
            if thumbnail_path:
                self.setIcon(QtGui.QIcon(QtGui.QPixmap(thumbnail_path)))
            else:
                self.setIcon(QtGui.QIcon(QtGui.QPixmap(FileTypeIcons.icons[asset_type])))
        except:
            Logger.getInstance().Log(f"Unable to load icon for file type '{self.asset_type}' - Using generic default")
            self.setIcon(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/File")))

    def GetType(self):
        return self.asset_type


class TileDelegate(QtWidgets.QStyledItemDelegate):
    """ A custom style delegate that improves the look of QListView items when in 'IconMode' """
    # https://stackoverflow.com/questions/59063030/qtreeview-cell-selected-highlight-resize
    def paint(self, painter, option, index):
        if not index.isValid():
            return

        # Load the base style data
        self.initStyleOption(option, index)

        # Force the selection to include the full width of the row (tile), instead of only encompassing the minimum
        option.showDecorationSelected = True

        # Paint using the style data stored in 'option'
        style = option.widget.style() if option.widget else QtGui.QApplication.style()
        style.drawControl(QtWidgets.QStyle.ControlElement.CE_ItemViewItem, option, painter, option.widget)

    def sizeHint(self, option, index):
        if not index.isValid():
            return super(TileDelegate, self).sizeHint(option, index)
        else:
            return QtCore.QSize(64, 80)


class OutlinerContextMenu(QtWidgets.QMenu):
    SIG_IMPORT = QtCore.pyqtSignal()
    SIG_RENAME = QtCore.pyqtSignal()
    SIG_DELETE = QtCore.pyqtSignal()
    SIG_DUPLICATE = QtCore.pyqtSignal()
    SIG_CREATE_FOLDER = QtCore.pyqtSignal()
    SIG_CREATE_SCENE = QtCore.pyqtSignal()
    SIG_CREATE_DIALOGUE = QtCore.pyqtSignal()
    SIG_CREATE_INTERFACE = QtCore.pyqtSignal()
    SIG_SHOW_DETAILS = QtCore.pyqtSignal()

    def __init__(self, parent, core, use_asset_menu: bool = False, active_selection: bool = False):
        super().__init__(parent)
        # Store a ref to the window core so we can access pertinent functions
        self.core = core

        # Create each of the possible actions
        self.a_import = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Import.png")), "Import", self)
        self.a_rename = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Rename.png")), "Rename", self)
        self.a_delete = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Close.png")), "Delete", self)
        self.a_duplicate = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Copy.png")), "Duplicate", self)
        self.a_create_folder = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Folder.png")), "Create Folder", self)
        self.a_new_scene = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Scene.png")), "Create Scene", self)
        self.a_new_dialogue = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Dialogue.png")), "Create Dialogue", self)
        self.a_new_interface = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Interface.png")), "Create Interface", self)
        self.a_details = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Information.png")), "Details", self)

        # Only show the contextually relevant options
        if not use_asset_menu:
            self.addAction(self.a_import)
        if active_selection:
            self.addAction(self.a_rename)
            self.addAction(self.a_delete)
            self.addAction(self.a_duplicate)
        if not use_asset_menu:
            self.addAction(self.a_create_folder)
            self.addAction(self.a_new_scene)
            self.addAction(self.a_new_dialogue)
            self.addAction(self.a_new_interface)
        if active_selection:
            self.addAction(self.a_details)


class QuickAccessButton(QtWidgets.QToolButton):
    SIG_DROP = QtCore.pyqtSignal(list, bool)

    def __init__(self, parent, path: str, process_func: object=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.path = path

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        # Accept any and all drops
        event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:  # Only external files use URLs
            # Process all files to ensure they're local files (Further processing is done elsewhere). This is a list
            # of absolute paths
            processed_files = []
            for url in urls:
                if url.isLocalFile():
                    processed_files.append(url.toLocalFile())

            if processed_files:
                self.SIG_DROP.emit(processed_files, True)

        else:
            self.SIG_DROP.emit([self.path], False)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_UnderMouse, False)  # Fix for hover state freeze due to QDialogs
        event.acceptProposedAction()


class DialogAssetInfo(QtWidgets.QDialog):
    def __init__(self, file_name: str, rel_file_path: str, abs_file_path: str, file_type: FileType):
        super().__init__()

        # Hide the OS header to lock its position
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.resize(400, 300)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Header
        self.header = QtWidgets.QLabel("Asset Details")
        self.header.setObjectName("h2")
        self.main_layout.addWidget(self.header)

        # Asset List
        self.details_list = QtWidgets.QTableWidget(self)
        self.details_list.verticalHeader().setObjectName("vertical")
        self.details_list.setColumnCount(2)
        self.details_list.setWordWrap(False)
        self.details_list.setShowGrid(False)
        self.details_list.horizontalHeader().hide()
        self.details_list.verticalHeader().hide()
        self.details_list.setContentsMargins(0,0,0,0)
        self.details_list.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.details_list.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable editing
        self.details_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)  # Disable selection
        self.details_list.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # 'outline: none;' doesn't work for table widgets seemingly, so I can't use CSS to disable the
        # focus border. Thus, we do it the slightly more tragic way
        self.details_list.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.main_layout.addWidget(self.details_list)

        # Info elements
        self.details_list.insertRow(self.details_list.rowCount())
        self.details_list.setItem(0, 0, QtWidgets.QTableWidgetItem("File Name:"))
        file_name_label = QtWidgets.QLabel(file_name)
        file_name_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.details_list.setCellWidget(0, 1, file_name_label)

        self.details_list.insertRow(self.details_list.rowCount())
        self.details_list.setItem(1, 0, QtWidgets.QTableWidgetItem("Project Path:"))
        rel_file_path_label = QtWidgets.QLabel(rel_file_path)
        rel_file_path_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.details_list.setCellWidget(1, 1, rel_file_path_label)

        self.details_list.insertRow(self.details_list.rowCount())
        self.details_list.setItem(2, 0, QtWidgets.QTableWidgetItem("File System Path:"))
        abs_file_path_label = QtWidgets.QLabel(abs_file_path)
        abs_file_path_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.details_list.setCellWidget(2, 1, abs_file_path_label)

        self.details_list.insertRow(self.details_list.rowCount())
        self.details_list.setItem(3, 0, QtWidgets.QTableWidgetItem("File Type:"))
        file_type_label = QtWidgets.QLabel(file_type.name)
        file_type_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.details_list.setCellWidget(3, 1, file_type_label)

        self.details_list.resizeRowsToContents()

        # Confirmation Buttons
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.accept)
        self.main_layout.addWidget(self.button_box)


