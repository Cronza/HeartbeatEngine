import re
from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.DetailsPanel.details_entry_base import DetailsEntryBase


class DetailsEntryColor(DetailsEntryBase):
    def __init__(self, settings, refresh_func=None, global_toggle_func=None):
        super().__init__(settings, refresh_func, global_toggle_func)
        # NOTE FOR THE LOGIC IN THIS FILE
        # So for some unholy reason, Qt doesn't really have a great way of changing widget colors. While stylesheets
        # are nice, retrieving data from a stylesheet is a lesson in pain (You get ALL of the data, not just a part
        # you actually want

        # Additionally, to my knowledge, changing stylesheets don't cause a signal change unless you hook onto the
        # underlying events. I try to avoid this complexity, so the way this file handles detecting changes is different
        # than other detail types

        self.input_widget = QtWidgets.QFrame()
        self.input_widget.setFrameStyle(QtWidgets.QFrame.Panel)
        self.input_widget.setStyleSheet("border: 1px solid rgb(122,122,122);background-color: rgb(255,255,255)")

        # @TODO: Replace style sheet assignment with a QPalette to retain button state styles
        # Create the color selector button, and style it accordingly
        self.color_select_button = QtWidgets.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Color_Wheel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.color_select_button.setIcon(icon)
        self.color_select_button.clicked.connect(self.OpenColorPrompt)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.color_select_button)

    def Get(self):
        raw_style_sheet = self.input_widget.styleSheet()
        pattern = "background-color: rgb\((.*)\)"

        color = re.search(pattern, raw_style_sheet).group(1)
        return color.split(",")

    def Set(self, data) -> None:
        # Change the data without causing any signal calls
        self.input_widget.setStyleSheet(f"border: 1px solid rgb(122,122,122); background-color: rgb({','.join(map(str, data))})")

    def MakeUneditable(self):
        pass

    def OpenColorPrompt(self):
        color_choice = QtWidgets.QColorDialog.getColor()

        # 'rgb()' or 'getRgb()' return a QColor with alpha. We only want the RGB values (This feels wrong and I hate it)
        rgb = color_choice.red(), color_choice.green(), color_choice.blue()

        if color_choice.isValid():
            self.input_widget.setStyleSheet(f"background-color: rgb({', '.join(map(str, rgb))})")

            # Manually call the input change func since we know for a fact the input widget has changed
            self.InputValueUpdated()
