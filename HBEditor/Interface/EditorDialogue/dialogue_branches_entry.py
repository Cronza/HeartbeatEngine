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
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


class BranchesEntry(QtWidgets.QWidget):
    def __init__(self, settings, select_func):
        super().__init__()
        self.settings = settings

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store all dialogue entries associated with this branch
        self.branch_data = []

        # ****** DISPLAY WIDGETS ******
        # Due to some size shenanigans with the widgets when they have a certain amount of text, force them to use
        # the minimum where possible
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        #@TODO: Investigate why QLabel size hint includes newlines needed for wordwrap
        # Name
        self.name_widget = QtWidgets.QLabel()
        self.name_widget.setFont(settings.header_2_font)
        self.name_widget.setStyleSheet(settings.header_2_color)
        self.name_widget.setWordWrap(True)
        self.name_widget.setText("Test Name")
        self.name_widget.setSizePolicy(size_policy)
        self.name_widget.heightForWidth(0)

        # Details
        self.subtext_widget = QtWidgets.QLabel()
        self.subtext_widget.setFont(settings.subtext_font)
        self.subtext_widget.setStyleSheet(settings.subtext_color)
        self.subtext_widget.setText('Test Description')
        self.subtext_widget.setAlignment(Qt.AlignTop)
        self.subtext_widget.setSizePolicy(size_policy)

        # Add everything to the layout
        self.main_layout.addWidget(self.name_widget)
        self.main_layout.addWidget(self.subtext_widget)

    def Get(self):
        """ Returns a tuple of 'branch name', 'branch description' """
        return self.name_widget.text(), self.subtext_widget.text()

    def Set(self, data):
        """ Given a tuple of 'branch name' and 'branch description', update the relevant widgets """
        self.name_widget.setText(data[0])
        self.subtext_widget.setText(data[1])

    def GetData(self) -> list:
        """ Returns a list of dialogue entry data stored in this branch entry """
        return self.branch_data

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """

        pass
