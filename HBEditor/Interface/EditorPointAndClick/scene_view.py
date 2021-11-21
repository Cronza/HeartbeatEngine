from PyQt5 import QtWidgets, QtCore


class SceneView(QtWidgets.QGraphicsView):
    """ A custom subclass of QGraphicsView with extended features """
    def __init__(self, parent):
        super().__init__(parent)

        self.zoom_min = 0.4  # Zoom Out
        self.zoom_max = 4  # Zoom In
        self.zoom = 1  # Tracks the amount we've zoomed in
        self.zoom_speed = 0.1

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.fitInView(parent.sceneRect(), QtCore.Qt.KeepAspectRatio)

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
