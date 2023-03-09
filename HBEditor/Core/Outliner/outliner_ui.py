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
from PyQt5 import QtWidgets, QtGui, QtCore
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
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolbar.setObjectName("vertical")

        # Toolbar - Import Button
        self.import_button = QtWidgets.QToolButton(self)
        self.import_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.import_button.setText(" Import")
        self.import_button.setIcon(QtGui.QIcon(QtGui.QPixmap(":/Icons/Import.png")))
        self.import_button.clicked.connect(self.core.ImportAsset)
        self.toolbar.addWidget(self.import_button)
        self.toolbar.addSeparator()

        # Toolbar - Quick Access Buttons
        self.CreateQuickAccessButtons()

        # Asset View
        self.asset_list = AssetList(self)
        self.asset_list.customContextMenuRequested.connect(self.CreateContextMenu)
        self.asset_list.itemDoubleClicked.connect(self.ProcessAssetDoubleClick)
        self.asset_list.SIG_DROP.connect(self.core.MoveAsset)

        # Add everything to the main container
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.asset_list)

    def CreateContextMenu(self, pos):
        use_asset_menu = self.asset_list.itemAt(pos)
        asset_is_selected = len(self.asset_list.selectedItems()) > 0
        context_menu = OutlinerContextMenu(self, self.core, use_asset_menu, asset_is_selected)

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

    def ProcessQABDrop(self, path: str):
        """ When the user drops an asset on the Quick Access Buttons, invoke the 'Move' action """
        selection = self.asset_list.selectedItems()[0]  # Multi-select not currently supported
        self.core.MoveAssetUsingQAB(f"{self.core.cur_directory}/{selection.text()}", path)

    def ProcessAssetDoubleClick(self, item: QtWidgets.QListWidgetItem):
        if item.asset_type == FileType.Folder:
            self.MoveToDirectory(f"{self.core.cur_directory}/{item.text()}")
        else:
            self.core.OpenFile(item.text())

    def AddAsset(self, name: str, asset_type: FileType, thumbnail_path: str = ""):
        new_asset = OutlinerAsset(asset_type, name, thumbnail_path)

        self.asset_list.addItem(new_asset)

        # Allow folders to be drop targets so assets can be rearranged in the editor
        if asset_type == FileType.Folder:
            new_asset.setFlags(new_asset.flags() | QtCore.Qt.ItemIsDropEnabled)

    def RemoveAsset(self, name: str):
        asset = self.asset_list.findItems(name, QtCore.Qt.MatchExactly)[0]
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


class AssetList(QtWidgets.QListWidget):
    SIG_DROP = QtCore.pyqtSignal(object, object)

    def __init__(self, parent):
        super().__init__(parent)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setIconSize(QtCore.QSize(
            settings.editor_data["Outliner"]["icon_size"][0],
            settings.editor_data["Outliner"]["icon_size"][1]
        ))
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setWordWrap(True)

        # We need very specific control over the rendering for 'IconMode' in order to improve the 'tile' look. This
        # requires the use of a delegate which lets us override and expand the painting
        delegate = TileDelegate(parent)
        self.setItemDelegate(delegate)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        # Normally we'd need to create a drop object, create its MIME data, etc. However, this setup ensures that we
        # only action on selected items, which is supported out-of-the-box
        drop_source = self.selectedItems()[0]  # Multi-select is not currently supported
        drop_target = self.itemAt(event.pos())
        if drop_source is not None and drop_target is not None and drop_source is not drop_target:
            self.SIG_DROP.emit(drop_source, drop_target)


class OutlinerAsset(QtWidgets.QListWidgetItem):
    def __init__(self, asset_type: FileType, name: str, thumbnail_path: str = ""):
        super().__init__()
        self.setText(name)

        self.asset_type = asset_type
        if thumbnail_path:
            self.setIcon(QtGui.QIcon(QtGui.QPixmap(thumbnail_path)))
        else:
            self.setIcon(QtGui.QIcon(QtGui.QPixmap(FileTypeIcons.icons[asset_type])))

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
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, option.widget)

    def sizeHint(self, option, index):
        if not index.isValid():
            return super(TileDelegate, self).sizeHint(option, index)
        else:
            return QtCore.QSize(64, 80)


class OutlinerContextMenu(QtWidgets.QMenu):
    def __init__(self, parent, core, use_asset_menu: bool = False, active_selection: bool = False):
        super().__init__(parent)
        # Store a ref to the window core so we can access pertinent functions
        self.core = core

        if not use_asset_menu:
            a_import = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(":/Icons/Import.png")), "Import", self)
            a_import.triggered.connect(self.core.ImportAsset)
            self.addAction(a_import)

        if active_selection:
            a_rename = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(":/Icons/Rename.png")), "Rename", self)
            a_rename.triggered.connect(self.core.RenameAsset)
            self.addAction(a_rename)

            a_delete = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(":/Icons/Close.png")), "Delete", self)
            a_delete.triggered.connect(self.core.DeleteAsset)
            self.addAction(a_delete)

            a_duplicate = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(":/Icons/Copy.png")), "Duplicate", self)
            a_duplicate.triggered.connect(self.core.DuplicateAsset)
            self.addAction(a_duplicate)

        if not use_asset_menu:
            a_create_folder = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(":/Icons/Folder.png")), "Create Folder", self)
            a_create_folder.triggered.connect(self.core.CreateFolder)
            self.addAction(a_create_folder)

            a_new_scene = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(":/Icons/AM_Scene.png")), "Create Scene", self)
            a_new_scene.triggered.connect(self.core.CreateScene)
            self.addAction(a_new_scene)

        if active_selection:
            a_details = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(":/Icons/Information.png")), "Details", self)
            self.addAction(a_details)


class QuickAccessButton(QtWidgets.QToolButton):
    SIG_DROP = QtCore.pyqtSignal(str)

    def __init__(self, parent, path: str, process_func: object=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        self.path = path

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        # Accept any and all drops
        event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        self.SIG_DROP.emit(self.path)
        self.setAttribute(QtCore.Qt.WA_UnderMouse, False)  # Fix for hover state freeze due to QDialogs
        event.acceptProposedAction()
