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
from pickle import ADDITEMS

from PyQt6 import QtWidgets, QtGui, QtCore
from HBEditor.Core import settings
from HBEditor.Core.EditorCommon.SceneViewer.scene_viewer import SceneViewer
from HBEditor.Core.EditorCommon.SceneViewer.scene_items import RootItem


class OutlinerItem(QtWidgets.QTreeWidgetItem):
    def __init__(self):
        super().__init__()

        # the view item that this outliner item is associated with
        self.view_item = None


class OutlinerTree(QtWidgets.QTreeWidget):
    """ A custom QTreeWidget with improved drag & drop functionality """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QTableWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.setDropIndicatorShown(False)
        self.setAcceptDrops(True)

        self.setColumnCount(2)
        self.setHeaderLabels(['Name', ''])
        self.setAutoScroll(False)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QTreeView.DragDropMode.InternalMove)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.header().setStretchLastSection(False)  # Disable to allow custom sizing
        self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def startDrag(self, supportedActions: QtCore.Qt.DropAction) -> None:
        if supportedActions.MoveAction:
            new_drag = QtGui.QDrag(self)
            item_data: OutlinerItem = self.itemFromIndex(self.selectedIndexes()[0])
            #entry_widget = self.itemWidget(self.item(self.selectedIndexes()[0].row()))
            #drag_image = QtGui.QPixmap(entry_widget.size())
            #entry_widget.render(drag_image)  # Render the entry widget to a Pixmap
            #new_drag.setPixmap(drag_image)
            new_drag.setMimeData(self.mimeData([item_data.view_item]))
            new_drag.exec(supportedActions)
        else:
            super().startDrag(supportedActions)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        super().dropEvent(event)


class ViewOutliner(QtWidgets.QWidget):
    """ This class functions as a secondary way of visualizing entities within a View / Viewer """
    SIG_USER_UPDATE = QtCore.pyqtSignal()
    SIG_USER_ENTITY_CHANGE = QtCore.pyqtSignal(object, object) # Emits when the user selects a different entry than the active one

    def __init__(self, viewer: SceneViewer):
        super().__init__()

        # The viewer that this outliner is monitoring / reflects
        self.viewer = viewer
        self.viewer.SIG_USER_ADDED_ITEM.connect(self.AddItem)
        self.viewer.SIG_SELECTION_CHANGED.connect(self.OnViewerSelectionChanged)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the toolbar
        self.toolbar = QtWidgets.QToolBar(self)

        # Expand All Button
        self.toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Arrow_Down.png")),
            "Expand All",
            self.ExpandAllItems
        )
        self.toolbar.setObjectName("vertical")

        # Collapse All Button
        self.toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Arrow_Right.png")),
            "Collapse All",
            self.CollapseAllItems
        )
        self.main_layout.addWidget(self.toolbar)

        # Create search filter
        #self.groups_filter = QtWidgets.QLineEdit(self.toolbar)
        #self.groups_filter.setPlaceholderText("filter...")
        #self.toolbar_layout.addWidget(self.groups_filter)

        # Create entry List
        self.outliner_tree = OutlinerTree(self)
        self.outliner_tree.currentItemChanged.connect(self.OnOutlinerSelectionChanged)
        self.main_layout.addWidget(self.outliner_tree)

        # In case the View already has contents, populate immediately to ensure parity
        self.Sync()

    def Sync(self, recurse_target = None):
        """ Clear the tree and sync the latest state of the View """
        self.outliner_tree.clear()
        for item in self.viewer.GetSceneItems():
            self.AddItem(item)

    def AddItem(self, new_view_item: RootItem):
        """ Adds a new item to the view tree """
        new_tree_item = OutlinerItem()
        new_tree_item.view_item = new_view_item
        new_tree_item.setText(0, new_view_item.key)
        new_tree_item.setIcon(1, QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Information.png")))

        #if RootItem.parent():
        #    parent.addChild(new_item)
        #else:
        #    self.outliner_tree.addTopLevelItem(new_item)
        self.outliner_tree.addTopLevelItem(new_tree_item)

    def ExpandAllItems(self):
        """ Reveals all children at all depths  """
        # do thing here
        pass

    def CollapseAllItems(self):
        """ Collapses all items, hiding everything but root items """
        # do thing here
        pass

    # Slot Functions

    def OnOutlinerSelectionChanged(self, new_item: OutlinerItem, old_item):
        self.viewer.scene.clearSelection()
        new_item.view_item.setSelected(True)

    def OnViewerSelectionChanged(self, selected_items: list):
        self.outliner_tree.clearSelection()

        for selected_item in selected_items:
            for outliner_item_index in range(0, self.outliner_tree.topLevelItemCount()):
                top_level_item: OutlinerItem = self.outliner_tree.topLevelItem(outliner_item_index)
                if top_level_item.view_item == selected_item:
                    top_level_item.setSelected(True)
                elif top_level_item.childCount() > 0:
                    matching_item = self.FindMatchingOutlinerItem(selected_item, top_level_item)
                    if matching_item:
                        matching_item.setSelected(True)
                        break

    def FindMatchingOutlinerItem(self, view_item: RootItem, parent_outliner_item: OutlinerItem) -> OutlinerItem:
        for child_index in range(0, parent_outliner_item.childCount()):
            outliner_item: OutlinerItem = parent_outliner_item.child(child_index)
            if outliner_item.view_item == view_item:
                return outliner_item
            elif outliner_item.childCount() > 0:
                matching_item = self.FindMatchingOutlinerItem(view_item, outliner_item)
                if matching_item:
                    return matching_item

        return None
