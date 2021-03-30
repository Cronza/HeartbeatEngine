from PyQt5 import QtWidgets


class DetailsEntryBase(QtWidgets.QTreeWidgetItem):
    def __init__(self, settings, refresh_func=None):
        super().__init__()

        self.settings = settings

        # When the input widget is updated, in case another U.I element needs to refresh, allow us to execute an
        # ambiguous function
        self.refresh_func = refresh_func

        # Details entries have two main widgets: 'name_widget' and 'input_widget'. The former
        # is standalone, while the latter is kept inside 'input_container' as to allow multiple
        # elements to be present

        # Neither are populated here, as it's up to the subclasses to define
        self.name_widget = QtWidgets.QLabel()

        self.input_widget = None
        self.input_container = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QHBoxLayout(self.input_container)
        self.main_layout.setContentsMargins(0,0,0,0)

    def Get(self):
        pass

    def Set(self, data) -> None:
        pass

    def MakeUneditable(self):
        pass


