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
from Editor.Interface.outliner import OutlinerUI


class Outliner:
    def __init__(self, settings, gvn_core):

        self.settings = settings

        # We need an explicit reference to the GVN core in order to access file commands
        self.gvn_core = gvn_core

        # Build the Logger UI
        self.ui = OutlinerUI(self)

    def UpdateRoot(self, new_root):
        """ Updates the root of the dir tree, refreshing the file list """

        self.ui.UpdateRoot(new_root)

    def GetUI(self):
        """ Returns a reference to the outliner U.I """

        return self.ui

    def OpenFile(self, file_path):
        """ Send a request to the GVN editor core to open the provided file path """
        self.gvn_core.OpenFile(file_path)

    def DeleteFile(self, file_path):
        """ Send a request to the GVN editor core to delete the provided file path """
        self.gvn_core.DeleteFile(file_path)
