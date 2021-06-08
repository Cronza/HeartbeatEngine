from PyQt5 import QtWidgets, QtGui


class BasePopupMenu(QtWidgets.QDialog):
    def __init__(self, settings, logger, window_icon_path, window_name):
        super().__init__()

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(window_icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle(window_name)
        self.settings = settings
        self.logger = logger
