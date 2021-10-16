from PyQt5 import QtWidgets, QtGui

# Useful Thread: https://stackoverflow.com/questions/50068802/pyqt-qfileiconprovider-class-custom-icons

class FileSystemIconProvider(QtWidgets.QFileIconProvider):
    def __init__(self, settings):
        super().__init__()

        self.settings = settings
        self.recognized_image_extensions = ["png", "jpg", "jpeg", "targa"]

    def icon(self, fileInfo):
        # Override the icon function which returns the icon to use for each item in a QTree
        if fileInfo.isDir():
            return QtGui.QIcon(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Folder.png"))
        elif fileInfo.suffix() in self.recognized_image_extensions:
            return QtGui.QIcon(self.settings.ConvertPartialToAbsolutePath("Content/Icons/File_Image.png"))
        return QtGui.QIcon(self.settings.ConvertPartialToAbsolutePath("Content/Icons/File.png"))
