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
from datetime import datetime
from HBEditor.Core.settings import Settings
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QColor, QFont
from HBEditor.Core.Logger.logger_ui import LoggerUI
from HBEditor.Core.DataTypes.log_types import LogType


class Logger:
    __instance = None

    @staticmethod
    def getInstance():
        """
        Static access method - Used to acquire the singleton instance, or instantiate it if it doesn't already exist
        """
        if Logger.__instance is None:
            Logger()
        return Logger.__instance

    def __init__(self):
        # Enforce the use of the singleton instance
        if Logger.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Logger.__instance = self

        # Build the Logger UI
        self.log_ui = LoggerUI(self)

        # Load styling
        self.log_font = QFont(
            Settings.getInstance().style_data['EditorTextSettings']['log_font'],
            Settings.getInstance().style_data['EditorTextSettings']['log_text_size']
        )
        self.log_colors = {
            LogType.Normal: Settings.getInstance().style_data['EditorTextSettings']['log_normal_color'],
            LogType.Success: Settings.getInstance().style_data['EditorTextSettings']['log_success_color'],
            LogType.Warning: Settings.getInstance().style_data['EditorTextSettings']['log_warning_color'],
            LogType.Error: Settings.getInstance().style_data['EditorTextSettings']['log_error_color']
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
        except Exception as exc:
            print(f"Failed to determine log color type - Resorting to normal colors: {exc}")
            color = self.log_colors[LogType.Normal]
            prefix = self.log_colors[LogType.Normal]

        # Convert the string list structure we use to a int list using some sketchy conversions
        color = list(map(int, color.split(", ")))

        new_entry = QListWidgetItem(datetime.now().strftime("%H:%M:%S") + ": " + prefix + log_text)
        new_entry.setForeground(QColor(color[0], color[1], color[2]))
        new_entry.setFont(self.log_font)
        self.log_ui.log_list.addItem(new_entry)

        # Since Qt only refreshes widgets when it regains control of the main thread, force the update here
        # as long updates are high priority in terms of visibility
        self.log_ui.log_list.repaint()
        self.log_ui.repaint()

    def ClearLog(self):
        """ Deletes all log entries """
        self.log_ui.log_list.clear()

    def GetUI(self):
        """ Returns a reference to the logger U.I """
        return self.log_ui
