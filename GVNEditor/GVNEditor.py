# Any behaviour here that interfaces with QTUI/GVNEditor.py will be deprecated in favor of
# moving that code in here before a release

import sys, os
from EditorUtilities import Logger
from QTUI import GVNEditor as gvne
from PyQt5 import QtCore, QtGui, QtWidgets

class GVNEditor:
    def __init__(self):

        # DEPRECATE ON RELEASE BUILDS
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.editor = gvne.Ui_MainWindow()
        self.editor.setupUi(self.MainWindow)

        #Initialize the logger
        self.logWidget = self.editor.logList
        self.logger = Logger.Logger(self.logWidget)

        #@print(self.editor.DataManagerContainer.widget(0).children())
        #self.editor.Move

        #Connect some buttons
        self.MainWindow.show()

        sys.exit(self.app.exec_())

if __name__ == "__main__":
    editor = GVNEditor()

