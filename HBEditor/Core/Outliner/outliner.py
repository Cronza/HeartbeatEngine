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
import os
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core import settings
from HBEditor.Core.Outliner.outliner_ui import OutlinerUI, OutlinerAsset
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.EditorUtilities import image


class Outliner:
    def __init__(self, hb_core):

        self.cur_directory = "Content"

        self.hb_core = hb_core  # We need an explicit reference to the Heartbeat core in order to access file commands
        self.ui = OutlinerUI(self)  # Build the Logger UI
        self.Populate()  # Populate the view with assets from the registry

    def GetUI(self):
        return self.ui

    def Populate(self):
        """ Create an asset widget for each registered asset in the current directory """
        self.ui.ClearAssets()
        self.ui.ClearQAB()
        self.ui.CreateQuickAccessButtons()

        cur_dir = settings.GetAssetRegistryFolder(self.cur_directory)
        for asset in cur_dir:
            # File assets are registered with their respective type enum. Folders hold nested dicts
            if isinstance(cur_dir[asset], dict):
                self.ui.AddAsset(asset, FileType.Folder)

            elif FileType[cur_dir[asset]] == FileType.Asset_Image:
                thumbnail_path = image.GetThumbnail(f"{self.cur_directory}/{asset}")
                if not thumbnail_path:
                    thumbnail_path = image.GenerateThumbnail(f"{self.cur_directory}/{asset}")

                self.ui.AddAsset(asset, FileType[cur_dir[asset]], thumbnail_path)

            else:
                self.ui.AddAsset(asset, FileType[cur_dir[asset]])

    def CreateFolder(self):
        asset_name = self.hb_core.NewFolder(self.cur_directory)
        if asset_name:
            self.Populate()

    def CreateScene(self):
        asset_name = self.hb_core.NewFile(self.cur_directory, FileType.Scene)
        if asset_name:
            self.Populate()


    def CreateDialogue(self):
        asset_name = self.hb_core.NewFile(self.cur_directory, FileType.Dialogue)
        if asset_name:
            self.Populate()

    def CreateInterface(self):
        asset_name = self.hb_core.NewInterface(self.cur_directory)
        if asset_name:
            self.Populate()

    def OpenFile(self, asset_name: str):
        self.hb_core.OpenFile(f"{self.cur_directory}/{asset_name}")

    def DeleteAsset(self):
        selected_items = self.ui.asset_list.selectedItems()  # Multi-select deletions are not supported currently
        if selected_items:
            self.hb_core.DeleteFileOrFolder(
                f"{self.cur_directory}/{selected_items[0].text()}",
                selected_items[0].GetType() == FileType.Folder
            )
            self.Populate()

    def DuplicateAsset(self):
        selected_items = self.ui.asset_list.selectedItems()  # Multi-select deletions are not supported currently
        if selected_items:
            is_folder = False
            if selected_items[0].GetType() == FileType.Folder:
                is_folder = True

            self.hb_core.DuplicateFileOrFolder(f"{self.cur_directory}/{selected_items[0].text()}", is_folder)
            self.Populate()

    def RenameAsset(self):
        selected_items = self.ui.asset_list.selectedItems()  # Multi-select deletions are not supported currently
        if selected_items:
            is_folder = False
            if selected_items[0].GetType() == FileType.Folder:
                is_folder = True

            self.hb_core.RenameFileOrFolder(f"{self.cur_directory}/{selected_items[0].text()}", is_folder)
            self.Populate()

    def MoveAsset(self, source: OutlinerAsset, target: OutlinerAsset):
        """ Moves the 'source' asset to the 'target' asset directory """
        source_path = f"{self.cur_directory}/{source.text()}"
        target_path = f"{self.cur_directory}/{target.text()}"

        if target.asset_type == FileType.Folder:
            if self.hb_core.MoveFileOrFolder(source_path, target_path):
                self.ui.RemoveAsset(source.text())

        self.Populate()

    def MoveAssetUsingQAB(self, source: str, target: str):
        """
        Moves an asset to the corresponding directory based on the Quick Access Button that was used. Both paths must
        be full paths with the content directory as their roots
        """

        if self.hb_core.MoveFileOrFolder(source, target):
            self.ui.RemoveAsset(os.path.basename(source))

        self.Populate()

    def ImportAsset(self, import_targets: list = None):
        if not import_targets:
            # No specified target, use full import process
            self.hb_core.Import(self.cur_directory)

        elif len(import_targets) == 1 and not os.path.isdir(import_targets[0]):
            # Singular target, use partial import process (Warning and error prompts, but no file dialog)
            self.hb_core.Import(self.cur_directory, import_targets[0])

        else:
            # N targets, use batch import process (No prompts except for a collective results window)
            self.hb_core.BatchImport(self.cur_directory, import_targets)

        self.Populate()
