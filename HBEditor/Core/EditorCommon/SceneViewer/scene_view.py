from PyQt5 import QtWidgets, QtCore, QtGui


class SceneView(QtWidgets.QGraphicsView):
    """ A custom subclass of QGraphicsView with extended features """
    SIG_USER_MOVED_ITEMS = QtCore.pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)

        self.setObjectName("scene-viewer")

        self.zoom_min = 0.4  # Zoom Out
        self.zoom_max = 4  # Zoom In
        self.zoom = 1  # Tracks the amount we've zoomed in
        self.zoom_speed = 0.1

        self.setDragMode(self.RubberBandDrag)
        self.setRubberBandSelectionMode(QtCore.Qt.ContainsItemShape)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.fitInView(parent.sceneRect(), QtCore.Qt.KeepAspectRatio)

        # Track the mouse position on LMB press to know whether selected items have been moved
        self.mouse_pos_on_press = None

    def wheelEvent(self, event):
        """ Override the wheel event so we can add zoom functionality """
        if event.angleDelta().y() > 0:  # User scrolled in
            modifier = 1
        else:  # User scrolled out
            modifier = -1

        factor = 1 + self.zoom_speed * modifier
        new_zoom = self.zoom * factor

        # If we've exceeded the zoom bounds, scale directly to the limit
        if new_zoom < self.zoom_min:
            factor = self.zoom_min / self.zoom
        elif new_zoom > self.zoom_max:
            factor = self.zoom_max / self.zoom

        self.scale(factor, factor)
        self.zoom *= factor

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        # Enable viewport panning while spacebar is down
        if event.key() == QtCore.Qt.Key_Space and not event.isAutoRepeat():
            self.setDragMode(self.ScrollHandDrag)
            self.setInteractive(False)

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        # Disable viewport panning once the spacebar is released
        if event.key() == QtCore.Qt.Key_Space and not event.isAutoRepeat():
            self.setDragMode(self.RubberBandDrag)
            self.setInteractive(True)

        super().keyReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        pass

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.mouse_pos_on_press = event.pos()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        selected_items = self.scene().selectedItems()
        if selected_items:
            # Only consider a move having happened if the cursor pos moved from when the mouse was first pressed
            if self.mouse_pos_on_press != event.pos():
                for item in selected_items:
                    for child in item.childItems():
                        # Always store a normalized position value between 0-1
                        #
                        # Normally we'd use 'scenePos' to skip all these conversions, but that seems to return a value that
                        # is altered by any translation applied to the item (Needs additional review to confirm). This
                        # breaks features such as 'center_align'
                        parent_pos = child.pos()
                        item_pos = child.mapFromParent(parent_pos)
                        scene_pos = child.mapToScene(item_pos)
                        norm_range = [
                            scene_pos.x() / self.scene().width(),
                            scene_pos.y() / self.scene().height()
                        ]
                        child.action_data["position"]["value"] = norm_range

                self.SIG_USER_MOVED_ITEMS.emit(selected_items)


class Scene(QtWidgets.QGraphicsScene):
    """ A custom subclass of QGraphicsScene with extended features """
    def __init__(self, rect):
        super().__init__(rect)

        self.scene_size = rect  # type: QtCore.QRectF
        self.AddDefaultBackground()

    def AddDefaultBackground(self):
        """ Create a default background (since the scene is, by default, transparent) """
        self.setBackgroundBrush(QtCore.Qt.darkGray)
        background = self.addRect(
            QtCore.QRectF(0, 0, self.scene_size.width(), self.scene_size.height()),
            QtGui.QPen(),
            QtGui.QBrush(QtCore.Qt.black)
        )
        background.setZValue(-9999999999)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        pass
