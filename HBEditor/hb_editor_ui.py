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
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from HBEditor.Core import settings
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.Outliner.outliner import Outliner


class HBEditorUI:
    def __init__(self, core):
        super().__init__()

        self.main_window = QtWidgets.QMainWindow()
        self.core = core

        # Initialize the U.I
        self.setupUi(self.main_window)

    def setupUi(self, MainWindow):
        self.LoadFonts(settings.editor_data['EditorSettings']["active_fonts"])
        self.LoadTheme(settings.editor_data['EditorSettings']["active_theme"])

        # Configure the Window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 720)

        MainWindow.setWindowIcon(QtGui.QIcon("EditorContent:Icons/Engine_Logo.png"))

        # Build the core widget / layout
        self.central_widget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)
        self.central_grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        # Build the Menu Bar
        self.menu_bar = MainMenuBar(MainWindow, self.core)
        MainWindow.setMenuBar(self.menu_bar)

        # Build the main resize splitter, allowing the user to resize each row
        self.main_resize_container = QtWidgets.QSplitter(self.central_widget)
        self.main_resize_container.setContentsMargins(0, 0, 0, 0)
        self.main_resize_container.setOrientation(Qt.Orientation.Vertical)
        self.central_grid_layout.addWidget(self.main_resize_container, 0, 0)

        # Build the Getting Started Screen
        self.getting_started_widget = GettingStartedScreen()
        self.main_resize_container.addWidget(self.getting_started_widget)

        # Sub tab widget - Ideal for widgets that should be accessible alongside the core editors
        self.sub_tab_widget = QtWidgets.QTabWidget(self.main_resize_container)
        self.sub_tab_widget.setContentsMargins(0, 0, 0, 0)
        self.AddSubTab(Logger.getInstance().GetUI(), "Logger")
        self.main_resize_container.insertWidget(1, self.sub_tab_widget)

        # Adjust the main editor container, so it takes up as much space as possible. This needs to happen once
        # all other widgets have been added, otherwise it'll break formatting
        self.main_resize_container.setStretchFactor(0, 10)

        # Cleanup
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.retranslateUi(MainWindow)

        Logger.getInstance().Log("Initialized Editor Interface")

    def retranslateUi(self, MainWindow):
        """ Sets the text of all UI components using available translation """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", f"Heartbeat Editor - {settings.user_project_name}"))
        self.menu_bar.retranslateUi(_translate)

    def Show(self):
        """ Show the Main Window, suspending execution until it is closed """
        self.main_window.show()

    def SetActiveProject(self):
        """
        Reload various UI elements for the newly opened project. If this is the first project loaded since
        launching the editor, then delete the 'Getting Started' screen and add additional windows"""
        if self.getting_started_widget:
            # Delete the 'Getting Started' screen
            self.main_resize_container.widget(0).deleteLater()
            self.getting_started_widget = None

            # Add the new elements
            self.main_tab_widget_container = QtWidgets.QWidget()
            self.main_tab_widget_layout = QtWidgets.QVBoxLayout(self.main_tab_widget_container)
            self.main_tab_widget_layout.setContentsMargins(0, 0, 0, 0)
            self.main_tab_widget_layout.setSpacing(0)
            self.main_tab_widget = MainTabWidget()
            self.main_tab_widget.SIG_TAB_CLOSE.connect(self.RemoveTab)
            self.main_tab_widget.SIG_TAB_CHANGE.connect(self.ChangeTab)
            self.main_tab_widget_layout.addWidget(self.main_tab_widget)
            self.main_resize_container.insertWidget(0, self.main_tab_widget_container)
            self.main_resize_container.setStretchFactor(0, 1)  # Enforce greedy scaling to consume available space

            self.outliner = Outliner(self.core)
            self.AddSubTab(self.outliner.GetUI(), "Outliner")

        # Clear old data
        self.main_tab_widget.clear()
        self.outliner.GetUI().ClearAssets()
        Logger.getInstance().ClearLog()

        # Reload the Outliner
        self.outliner.Populate()

        # Refresh U.I text using any active translations
        self.retranslateUi(self.main_window)

    def AddMainTab(self, widget: QtWidgets.QWidget, tab_name: str, enable_connections: bool = True):
        """
        Create a new tab to the 'main_tab_widget' and add the provided widget to it.

        If 'enable_connections' is True, then attempt to connect the widget to the 'Mark Dirty' and 'Mark Clean'
        functions of the tab. This requires that the provided widget has implemented both the 'SIG_USER_UPDATE' and
        'SIG_USER_SAVE' signals
        """

        self.main_tab_widget.setCurrentIndex(self.main_tab_widget.addTab(widget, tab_name))

        if enable_connections:
            self.main_tab_widget.currentWidget().SIG_USER_UPDATE.connect(self.main_tab_widget.MarkDirty)
            self.main_tab_widget.currentWidget().SIG_USER_SAVE.connect(self.main_tab_widget.MarkClean)

    def AddSubTab(self, widget: QtWidgets.QWidget, tab_name: str):
        """ Create a new tab to the 'sub_tab_widget' and add the provided widget to it """
        self.sub_tab_widget.addTab(widget, tab_name)
        self.sub_tab_widget.setCurrentIndex(self.sub_tab_widget.count() - 1)

    def ChangeTab(self, index):
        """ Updates the active editor when the tab selection changes """
        if index != -1:
            self.core.active_editor = self.main_tab_widget.widget(index).core
            if not self.main_tab_widget.isVisible():
                self.main_tab_widget.setVisible(True)
        else:
            self.core.active_editor = None
            self.main_tab_widget.setVisible(False)

    def RemoveTab(self, index):
        """ Remove the tab for the given index """
        #@TODO: Review if a memory leak is created here due to not going down the editor reference tree and deleting things
        Logger.getInstance().Log("Closing editor...")
        self.main_tab_widget.removeTab(index)
        if self.main_tab_widget.count() == 0:
            self.core.active_editor = None
        Logger.getInstance().Log("Editor closed")

    def LoadTheme(self, theme_path: str) -> None:
        """ Given the 'EditorContent' path to a theme .css file, load it and apply it to the editor application """
        theme_file = QtCore.QFile(theme_path)
        if theme_file.open(QtCore.QIODevice.OpenModeFlag.ReadOnly):
            self.core.app.setStyleSheet(QtCore.QTextStream(theme_file).readAll())
        else:
            Logger.getInstance().Log(f"Failed to initialize editor theme '{theme_path}'\n{theme_file.errorString()}", 4)

    def LoadFonts(self, font_paths: list):
        """ Given a list of 'EditorContent' font paths, load them so that they're available throughout the editor """
        for path in font_paths:
            if QtGui.QFontDatabase.addApplicationFont(QtCore.QDir(path).path()) < 0:
                Logger.getInstance().Log(f"Failed to load font '{path}'", 4)

    def GetWindow(self) -> QtWidgets.QMainWindow:
        return self.main_window


class MainMenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent: QtWidgets.QWidget, engine_core):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(0, 0, 1024, 21))

        # File Menu
        self.file_menu = QtWidgets.QMenu(self)
        self.file_menu.setWindowFlags(self.file_menu.windowFlags() | QtCore.Qt.WindowType.NoDropShadowWindowHint)
        self.a_save_file = QtGui.QAction(parent)
        self.a_save_file.triggered.connect(engine_core.Save)
        self.a_new_project = QtGui.QAction(parent)
        self.a_new_project.triggered.connect(engine_core.NewProject)
        self.a_open_project = QtGui.QAction(parent)
        self.a_open_project.triggered.connect(engine_core.OpenProject)
        self.file_menu.addAction(self.a_save_file)
        # self.file_menu.addAction(self.a_save_file_as)
        self.file_menu.addAction(self.a_new_project)
        self.file_menu.addAction(self.a_open_project)

        # Edit Menu
        self.edit_menu = QtWidgets.QMenu(self)
        self.edit_menu.setWindowFlags(self.edit_menu.windowFlags() | QtCore.Qt.WindowType.NoDropShadowWindowHint)
        self.a_open_project_settings = QtGui.QAction(parent)
        self.a_open_project_settings.triggered.connect(engine_core.OpenProjectSettings)
        self.a_open_values = QtGui.QAction(parent)
        self.a_open_values.triggered.connect(engine_core.OpenValues)
        self.edit_menu.addAction(self.a_open_project_settings)
        self.edit_menu.addAction(self.a_open_values)

        # Play Menu
        self.play_menu = QtWidgets.QMenu(self)
        self.play_menu.setWindowFlags(self.play_menu.windowFlags() | QtCore.Qt.WindowType.NoDropShadowWindowHint)
        self.a_play_game = QtGui.QAction(parent)
        self.a_play_game.triggered.connect(engine_core.Play)
        self.play_menu.addAction(self.a_play_game)

        # Build Menu
        self.build_menu = QtWidgets.QMenu(self)
        self.build_menu.setWindowFlags(self.build_menu.windowFlags() | QtCore.Qt.WindowType.NoDropShadowWindowHint)
        self.a_build = QtGui.QAction(parent)
        self.a_build.triggered.connect(engine_core.Build)
        self.a_build_clean = QtGui.QAction(parent)
        self.a_build_clean.triggered.connect(engine_core.Clean)
        self.build_menu.addAction(self.a_build)
        self.build_menu.addAction(self.a_build_clean)

        # Add each menu to the menu bar
        self.addAction(self.file_menu.menuAction())
        self.addAction(self.edit_menu.menuAction())
        self.addAction(self.play_menu.menuAction())
        self.addAction(self.build_menu.menuAction())

    def retranslateUi(self, _translate):
        # 'File Menu' Actions
        self.file_menu.setTitle(_translate("MainWindow", "File"))
        self.a_save_file.setText(_translate("MainWindow", "Save"))
        self.a_save_file.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.a_new_project.setText(_translate("MainWindow", "New Project"))
        self.a_new_project.setShortcut(_translate("MainWindow", "Ctrl+Alt+Shift+N"))
        self.a_open_project.setText(_translate("MainWindow", "Open Project"))
        self.a_open_project.setShortcut(_translate("MainWindow", "Ctrl+Alt+Shift+O"))

        # 'Play Menu' Actions
        self.play_menu.setTitle(_translate("MainWindow", "Play"))
        self.a_play_game.setText(_translate("MainWindow", "Play"))
        self.a_play_game.setShortcut(_translate("MainWindow", "Ctrl+Alt+P"))

        # 'Build Menu' Actions
        self.build_menu.setTitle(_translate("MainWindow", "Build"))
        self.a_build.setText(_translate("MainWindow", "Build"))
        self.a_build.setShortcut(_translate("MainWindow", "Ctrl+Alt+B"))
        self.a_build_clean.setText(_translate("MainWindow", "Clean"))

        # 'Edit Menu' Actions
        self.edit_menu.setTitle(_translate("MainWindow", "Edit"))
        self.a_open_project_settings.setText(_translate("MainWindow", "Project Settings"))
        self.a_open_project_settings.setShortcut(_translate("MainWindow", "Ctrl+Shift+P"))
        self.a_open_values.setText(_translate("MainWindow", "Values"))
        self.a_open_values.setShortcut(_translate("MainWindow", "Ctrl+Shift+V"))


class MainTabWidget(QtWidgets.QTabWidget):
    """ The main tab widget which contains tabs for opened files, editors and other key widgets """
    SIG_TAB_CLOSE = QtCore.pyqtSignal(int)
    SIG_TAB_CHANGE = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setVisible(False)
        self.setElideMode(QtCore.Qt.TextElideMode.ElideLeft)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.OnTabClose)
        self.currentChanged.connect(self.SIG_TAB_CHANGE.emit)

    def MarkDirty(self):
        """ Marks the active tab as dirty, showing an icon representing the tab has changes made to it's widget """
        self.setTabIcon(self.currentIndex(), QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/ChangesPending.png")))
        self.currentWidget().pending_changes = True

    def MarkClean(self):
        """ Marks the active tab as clean, removing any present icons """
        self.setTabIcon(self.currentIndex(), QtGui.QIcon())
        self.currentWidget().pending_changes = False

    def OnTabClose(self, tab_index: int):
        """ Close the tab. If the tab widget has pending changes, prompt for confirmation before closing"""
        tab_widget = self.currentWidget()
        if tab_widget.pending_changes:
            # Unfortunately there is no mechanical way of stopping the cancellation once it has started, so we can't
            # add a 'Cancel' option
            result = QtWidgets.QMessageBox.question(
                self,
                f"You have Pending Changes",
                "There are pending changes in this tab. Would you like to Save before closing?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )

            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                tab_widget.core.Export()

        self.SIG_TAB_CLOSE.emit(tab_index)


class GettingStartedScreen(QtWidgets.QWidget):
    """ An introductory screen meant for display when the editor is booted, prior to creating or loading a project """
    def __init__(self):
        super().__init__()

        self.getting_started_layout = QtWidgets.QVBoxLayout(self)

        getting_started_title = QtWidgets.QLabel("Getting Started")
        getting_started_title.setObjectName("text-soft-h1")

        getting_started_message = QtWidgets.QLabel()
        getting_started_message.setObjectName("text-soft")
        getting_started_message.setText(
            "To access editor features, please open a Heartbeat project: \n\n"
            "1) Go to 'File' -> 'New Project' to Create a new Heartbeat project\n"
            "2) Go to 'File' -> 'Open Project' to Open an existing Heartbeat project"
        )

        self.getting_started_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.getting_started_layout.addWidget(getting_started_title)
        self.getting_started_layout.addWidget(getting_started_message)
