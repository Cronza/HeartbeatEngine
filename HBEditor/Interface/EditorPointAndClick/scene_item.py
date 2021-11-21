from PyQt5 import QtWidgets


class SceneItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, pixmap, action_data):
        super().__init__(pixmap)

        self.action_data = action_data

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """

        pass