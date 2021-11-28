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
from HBEditor.Core.settings import Settings


class DialogueEntry(QtWidgets.QWidget):
    def __init__(self, action_data, select_func, size_refresh_func):
        super().__init__()

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store a func object that is used when the row containing this object should be resized based on the
        # subtext data in this object
        self.size_refresh_func = size_refresh_func

        # Store this entries action data
        self.action_data = action_data

        # ****** DISPLAY WIDGETS ******
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Name
        self.name_widget = QtWidgets.QLabel()
        self.name_widget.setFont(Settings.getInstance().header_2_font)
        self.name_widget.setStyleSheet(Settings.getInstance().header_2_color)
        self.name_widget.setText(self.action_data["display_name"])

        # Details
        self.subtext_widget = QtWidgets.QLabel()
        self.subtext_widget.setFont(Settings.getInstance().subtext_font)
        self.subtext_widget.setStyleSheet(Settings.getInstance().subtext_color)

        # Refresh the subtext
        self.UpdateSubtext()

        # Add everything to the layout
        self.main_layout.addWidget(self.name_widget)
        self.main_layout.addWidget(self.subtext_widget)

    def Get(self) -> dict:
        """ Returns the action data stored in this object """
        return self.action_data

    def UpdateSubtext(self):
        """ Updates the subtext displaying entry parameters """
        if "requirements" in self.action_data:
            self.subtext_widget.setText(self.CompileSubtextString(self.action_data["requirements"]))

    def CompileSubtextString(self, data):
        """ Given a list of requirements from the ActionsDatabase file, compile them into a user-friendly string """
        #@TODO: Resolve issue for actions that don't have any requirements (IE. Stop Music)
        cur_string = ""
        for param in data:
            if param["preview"]:

                param_name = param["name"]
                param_data = None

                if param["type"] == "container":
                    # Recurse, searching the children as well
                    cur_string += f"{param_name}: ["
                    cur_string += self.CompileSubtextString(param['children'])
                    cur_string += "], "

                else:
                    param_data = param["value"]
                    cur_string += f"{param_name}: {param_data}, "

        # Due to how the comma formatting is, strip it from the end of the string
        return cur_string.strip(', ')

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """

        self.UpdateSubtext()
        self.size_refresh_func()

