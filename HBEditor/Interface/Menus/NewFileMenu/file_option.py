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
from PyQt5.QtWidgets import QListWidgetItem


class FileOption(QListWidgetItem):
    def __init__(self, icon, file_type, display_text, description_text, parent):
        super().__init__(icon, display_text, parent)

        self.setFont(Settings.getInstance().paragraph_font)

        self.file_type = file_type
        self.description_text = description_text

    def GetDescription(self):
        """ Returns the description text for this entry """
        return self.description_text

    def GetFileType(self):
        """ Returns the file type stored in this class """
        return self.file_type
