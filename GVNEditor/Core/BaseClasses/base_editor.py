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
import os


class EditorBase:
    def __init__(self, settings, logger, file_path):
        self.settings = settings
        self.logger = logger
        self.file_path = file_path
        self.file_type = None
        self.editor_ui = None

        self.logger.Log("Initializing Editor...")

    def GetFileName(self):
        """ Returns the name of the file that is being targeted by this editor """
        return os.path.basename(self.file_path)

    def GetFilePath(self):
        """ Returns the path of the file that is being targeted by this editor """
        return self.file_path

    def GetUI(self):
        """ Returns the UI object for this editor """
        return self.editor_ui

    def Save(self):
        """ Write the data held in the editor to the file it points to """
        pass

    def Export(self):
        """
        Writes the data held in the editor to a variant of the file it points to in the structure usable by the
        engine
        """
        pass

    def Import(self):
        """ Reads in and loads file this editor points to """

