from PyQt5 import QtWidgets

class SimpleCheckbox(QtWidgets.QWidget):
    """
    A custom wrapper for the QCheckbox class when provides a textless, centered checkbox
    """
    def __init__(self, click_function):
        super().__init__()
        # For some unholy reason, the QCheckbox widget does not support center alignment natively. To make matters
        # worse, the text is considered in the size when used in layouts regardless if text is actually specified

        # This can be bypassed by surrounding the QCheckbox in spacers that force it to the center of the layout
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.left_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding)
        self.right_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding)

        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setText("")

        self.main_layout.addItem(self.left_spacer)
        self.main_layout.addWidget(self.checkbox)
        self.main_layout.addItem(self.right_spacer)

        if click_function:
            self.checkbox.stateChanged.connect(click_function)

    def Get(self) -> bool:
        """ Returns whether the checkbox is checked """
        return self.checkbox.isChecked()

    def Set(self, value) -> None:
        self.checkbox.setChecked(value)
