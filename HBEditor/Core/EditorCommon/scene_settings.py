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
from HBEditor.Core.Primitives.input_entries import *
from HBEditor.Core.EditorUtilities import action_data as ad
from HBEditor.Core.Primitives import input_entry_handler as ieh


class SceneSettings(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.settings_tree = QtWidgets.QTreeWidget(self)
        self.settings_tree.setObjectName("no-top")
        self.settings_tree.setColumnCount(2)
        self.settings_tree.setHeaderLabels(['Name', 'Input'])
        self.settings_tree.setAutoScroll(False)
        self.settings_tree.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.settings_tree.header().setStretchLastSection(False)  # Disable to allow custom sizing
        self.settings_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        self.settings_tree.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.settings_tree.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.settings_tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.main_layout.addWidget(self.settings_tree)

    def Populate(self, data: dict = None):
        """ Generate and add a pre-defined list of scene settings to view. If 'data' in provided, then populate using
         those values. Expected format: {entry_name>: entry_data}"""
        self.settings_tree.clear()

        entries = {
            "interface": {
                "type": "Asset_Interface",
                "default": "",
                "value": "",
                "flags": ["editable"]
            },
            "description": {
                "type": "Paragraph",
                "default": "",
                "value": "",
                "flags": ["editable"]
            },
            "allow_pausing": {
                "type": "Bool",
                "default": "True",
                "value": "True",
                "flags": ["editable"]
            }
        }

        if data:
            if "interface" in data:
                entries["interface"]["value"] = data["interface"]
            if "description" in data:
                entries["description"]["value"] = data["description"]
            if "allow_pausing" in data:
                entries["allow_pausing"]["value"] = data["allow_pausing"]

        for name, data in entries.items():
            ieh.Add(
                owner=self,
                view=self.settings_tree,
                name=name,
                data=data,
                parent=None
            )

    def GetData(self):
        """
        Return a dict of all items displayed within the scene_settings window. Format: {<entry_name>: <entry_value}
        """
        data_to_return = {}
        parent = self.settings_tree.invisibleRootItem()
        for entry_index in range(0, parent.childCount()):
            entry = parent.child(entry_index)
            entry_name = self.settings_tree.itemWidget(entry, 0).text()
            entry_data = self.settings_tree.itemWidget(entry, 1).Get()
            data_to_return[entry_name] = entry_data

        return data_to_return
