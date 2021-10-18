from PyQt5 import QtWidgets
from HBEditor.Interface.Primitives.simple_checkbox import SimpleCheckbox


class InputEntryBase(QtWidgets.QTreeWidgetItem):
    def __init__(self, settings, refresh_func=None):
        super().__init__()

        self.settings = settings

        # When the input widget is updated, in case another U.I element needs to refresh, allow us to execute an
        # ambiguous function
        self.refresh_func = refresh_func

        # Details entries have three main widgets: 'name_widget', 'input_widget' and 'global_toggle'.
        # - 'name_widget': A standalone text widget representing the name of the detail
        # - 'input_widget': Kept inside 'input_container' as to allow any number of input_widgets for child classes
        # - 'global_toggle': A checkbox representing whether to use a global value or the value in the 'input_widget'

        # 'name_widget' and 'input_widget' are declared, but not initialized as it is up to the subclass to
        # do that
        self.name_widget = QtWidgets.QLabel()
        self.name_widget.setFont(self.settings.paragraph_font)
        self.name_widget.setStyleSheet(settings.paragraph_color)

        self.input_widget = None
        self.input_container = QtWidgets.QWidget()

        # 'global_toggle' is not supposed to be shown for all entries. It's only used for entries that need it
        self.show_global_toggle = False
        self.global_toggle = SimpleCheckbox(self.GlobalToggle)
        self.global_toggle.setToolTip("Whether to use the global value specified in the project file for this entry")

        self.main_layout = QtWidgets.QHBoxLayout(self.input_container)
        self.main_layout.setContentsMargins(0,0,0,0)

    def Get(self):
        pass

    def Set(self, data) -> None:
        pass

    def GetGlobal(self) -> bool:
        """ Returns the current value of the global checkbox """
        return self.global_toggle.Get()

    def MakeUneditable(self):
        """ Makes any relevant input widgets unable to be used """
        pass

    def MakeEditable(self):
        """ Makes any relevant input widgets able to be used """
        pass

    def InputValueUpdated(self):
        """ When the input value for this entry is changed, call the refresh function provided to this class """
        # Any change to detail entries while the global toggle is enabled will toggle it off
        if self.global_toggle.Get():
            self.global_toggle.Set(False)

        if self.refresh_func:
            self.refresh_func(self)

    def GlobalToggle(self):
        """
        When the global checkbox is toggled on, call a provided function, passing a reference to this class
        This function is not meant to be overridden
        """
        if self.global_toggle.Get():
            self.MakeUneditable()
        else:
            self.MakeEditable()

