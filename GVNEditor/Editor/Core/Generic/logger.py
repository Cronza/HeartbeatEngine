"""
    This file is part of GVNEditor.

    GVNEditor is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GVNEditor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GVNEditor.  If not, see <https://www.gnu.org/licenses/>.
"""

from datetime import datetime
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QColor, QFont
from Editor.Interface.Generic.logger import LoggerUI
from Editor.Utilities.DataTypes.log_types import LogType


class Logger:
    def __init__(self, e_ui, settings):

        self.settings = settings

        # Build the Logger UI
        self.log_ui = LoggerUI(self)

        # Load styling
        self.log_font = QFont(self.settings.settings['EditorTextSettings']['log_font'], self.settings.settings['EditorTextSettings']['log_text_size'])
        self.log_colors = {
            LogType.Normal: self.settings.settings['EditorTextSettings']['log_normal_color'],
            LogType.Success: self.settings.settings['EditorTextSettings']['log_success_color'],
            LogType.Warning: self.settings.settings['EditorTextSettings']['log_warning_color'],
            LogType.Error: self.settings.settings['EditorTextSettings']['log_error_color']
        }
        self.log_prefixes = {
            LogType.Normal: "",
            LogType.Success: "Success: ",
            LogType.Warning: "Warning: ",
            LogType.Error: "Error: "
        }

        self.Log("Initializing Logger...")

    def Log(self, log_text, log_type=LogType.Normal):
        prefix = ""

        # Since the expectation is that the user provides ints that are converted to the respective log type, this
        # can lead to an invalid log type. If this ever happens, just default to the normal style
        try:
            converted_type = LogType(log_type)
            color = self.log_colors[converted_type]
            prefix = self.log_prefixes[converted_type]
        except:
            color = self.log_colors[LogType.Normal]
            prefix = self.log_colors[LogType.Normal]

        # Convert the string list structure we use to a int list using some sketchy conversions
        color = list(map(int, color.split(", ")))

        new_entry = QListWidgetItem(datetime.now().strftime("%H:%M:%S") + ": " + prefix + log_text)
        new_entry.setForeground(QColor(color[0], color[1], color[2]))
        self.log_ui.log_list.addItem(new_entry)

    def ClearLog(self):
        self.log_ui.log_list.clear()
