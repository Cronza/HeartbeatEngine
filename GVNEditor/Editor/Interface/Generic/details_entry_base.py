from PyQt5 import QtWidgets


class DetailsEntryBase(QtWidgets.QWidget):
    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)

    def Get(self):
        pass

    def Set(self, data) -> None:
        pass

    def MakeUneditable(self):
        pass


