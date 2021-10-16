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
import shutil
from GVNEditor.Interface.Outliner.outliner import OutlinerUI
from GVNEditor.Utilities.DataTypes.file_types import FileType
from GVNEditor.Utilities.yaml_manager import Writer

class Outliner:
    def __init__(self, settings, gvn_core):

        self.settings = settings

        # We need an explicit reference to the GVN core in order to access file commands
        self.gvn_core = gvn_core

        # Build the Logger UI
        self.ui = OutlinerUI(self, settings)

    def UpdateRoot(self, new_root):
        """ Requests that the FileSystemTree refresh it's tree using a new root """
        self.ui.fs_tree.UpdateRoot(new_root)

    def GetUI(self):
        """ Returns a reference to the outliner U.I """
        return self.ui

    def CreateFile(self, path: str, file_type) -> str:
        """
        Create a file of the given file type, initially assigning it a temp name. Returns whether the action was
        successful
        """
        file_name_exists = True

        # Keep trying to create the file using a simple iterator. At some point, don't allow creating if the user has
        # somehow created enough files to max this...I really hope they don't
        for num in range(0, 100):
            full_file_path = path + f"/New_{file_type}_{num}.yaml"
            if not os.path.exists(full_file_path):

                # Doesn't exist. Create it!
                Writer.WriteFile(
                    "",
                    full_file_path,
                    self.settings.GetMetadataString(FileType[file_type])
                )
                return full_file_path

        # Somehow the user has all versions of the default name covered...Inform the user
        self.gvn_core.logger.Log("Unable to create file as all default name iterations are taken", 4)
        return None

    def CreateFolder(self, path: str) -> bool:
        """ Create a directory, initially assigning it a temp name. Returns whether the action was successful """
        folder_name_exists = True

        # Keep trying to create the folder using a simple iterator. At some point, don't allow creating if the user has
        # somehow created enough folders to max this...I really hope they don't
        for num in range(0, 100):
            full_folder_path = path + f"/New_Folder_{num}"
            if not os.path.exists(full_folder_path):
                # Doesn't exist. Create it!
                os.mkdir(full_folder_path)
                return full_folder_path

        # Somehow the user has all versions of the default name covered...Inform the user
        self.gvn_core.logger.Log("Unable to create folder as all default name iterations are taken", 4)
        return None

    def DeleteFile(self, path):
        """ Delete the provided file. Editor will remain open if the user wishes to resave """
        try:
            os.remove(path)
            self.gvn_core.logger.Log(f"Successfully deleted file '{path}'", 2)
        except Exception as exc:
            self.gvn_core.logger.Log(f"Failed to delete file '{path}' - Please review the exception to understand more", 4)

    def DeleteFolder(self, path):
        """ Delete the provided folder recursively. Editors will remain open if the user wishes to resave """
        print("Deleting folder")
        try:
            print(path)
            shutil.rmtree(path)
            self.gvn_core.logger.Log(f"Successfully deleted folder '{path}' and all of it's contents", 2)
        except Exception as exc:
            self.gvn_core.logger.Log(f"Failed to delete folder '{path}' - Please review the exception to understand more", 4)
            print(exc)