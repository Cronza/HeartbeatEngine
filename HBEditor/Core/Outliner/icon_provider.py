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
from PyQt5 import QtWidgets, QtGui
from HBEditor.Core import settings

# Useful Thread: https://stackoverflow.com/questions/50068802/pyqt-qfileiconprovider-class-custom-icons


class FileSystemIconProvider(QtWidgets.QFileIconProvider):
    def __init__(self):
        super().__init__()

        self.recognized_image_extensions = ["png", "jpg", "jpeg", "targa"]

    def icon(self, fileInfo):
        # Override the icon function which returns the icon to use for each item in a QTree
        if fileInfo.isDir():
            return QtGui.QIcon(":/Icons/Folder.png")
        elif fileInfo.suffix() in self.recognized_image_extensions:
            return QtGui.QIcon(":/Icons/File_Image.png")
        return QtGui.QIcon(":/Icons/File.png")
