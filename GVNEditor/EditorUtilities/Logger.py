"""
    This file is part of GVNEditor.

    GVNEditor is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GVNEditor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GVNEditor.  If not, see <https://www.gnu.org/licenses/>.
"""

from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets

class Logger(QtWidgets.QListWidget):
    def __init__(self, logWidget):
        self.logWidget = logWidget
        self.Log("Initializing Logger...")

    def Log(self, logText):
        self.logWidget.addItem(datetime.now().strftime("%H:%M:%S") + ": " + logText)
