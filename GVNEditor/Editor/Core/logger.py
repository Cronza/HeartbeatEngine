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
from Editor.Interface.logger import LoggerUI
from PyQt5 import QtCore, QtGui, QtWidgets


class Logger:
    def __init__(self, e_ui):

        # Keep track of the main editor U.I in case we need access to shared settings
        self.e_ui = e_ui

        # Build the Logger UI
        self.log_ui = LoggerUI(self)
        self.Log("Initializing Logger...")

    def Log(self, log_text):
        self.log_ui.log_list.addItem(datetime.now().strftime("%H:%M:%S") + ": " + log_text)

    def ClearLog(self):
        self.log_ui.log_list.clear()
