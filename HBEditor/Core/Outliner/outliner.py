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
import pathlib
from PyQt5 import QtWidgets
from PIL import Image, UnidentifiedImageError
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core import settings
from HBEditor.Core.Outliner.outliner_ui import OutlinerUI, OutlinerAsset
from HBEditor.Core.DataTypes.file_types import FileType


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
        cur_dir = settings.GetAssetRegistryFolder(self.cur_directory)
        for asset in cur_dir:
            # File assets are registered with their respective type enum. Folders hold nested dicts
            if isinstance(cur_dir[asset], dict):
                self.ui.AddAsset(asset, FileType.Folder)

            elif FileType[cur_dir[asset]] == FileType.Asset_Image:
                thumbnail_path = self.GetThumbnail(f"{self.cur_directory}/{asset}")
                if not thumbnail_path:
                    thumbnail_path = self.GenerateThumbnail(f"{self.cur_directory}/{asset}")

                self.ui.AddAsset(asset, FileType[cur_dir[asset]], thumbnail_path)

            else:
                self.ui.AddAsset(asset, FileType[cur_dir[asset]])

    def CreateFolder(self):
        asset_name = self.hb_core.NewFolder(self.cur_directory)
        if asset_name:
            self.ui.AddAsset(asset_name, FileType.Folder)

    def CreateScene(self):
        asset_name, asset_type = self.hb_core.NewScene(self.cur_directory)
        if asset_name:
            self.ui.AddAsset(asset_name, asset_type)

    def OpenFile(self, asset_name: str):
        self.hb_core.OpenFile(f"{self.cur_directory}/{asset_name}")

    def DeleteAsset(self):
        selected_items = self.ui.asset_list.selectedItems()  # Multi-select deletions are not supported currently
        if selected_items:
            is_folder = False
            if selected_items[0].GetType() == FileType.Folder:
                is_folder = True

            self.hb_core.DeleteFileOrFolder(f"{self.cur_directory}/{selected_items[0].text()}", is_folder)
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

    def ImportAsset(self):
        self.hb_core.Import(self.cur_directory)
        self.Populate()

    def GenerateThumbnail(self, path: str) -> str:
        """
        Given a relative file path to an image with the Content folder as the root, generate a thumbnail image for it
        and save it to /Thumbnails. Return the path for the thumbnail if successfully created. Otherwise, return an empty
        string
        """
        # Full path to the source image
        full_image_path = f"{settings.user_project_dir}/{path}"

        # Full path to the thumbnail (Remove the root folder for 'path' as we need the thumbnail folder to be the root)
        thumbnail_image_path = f"{settings.user_project_dir}/Thumbnails/{'/'.join(path.split('/')[1:])}"
        pathlib.Path(os.path.dirname(thumbnail_image_path)).mkdir(parents=True, exist_ok=True)

        try:
            # Open the original file, and overwrite it with a generated, smaller copy. Use (64, 64) to match the size
            # of the editor icons
            img = Image.open(full_image_path)
            img.thumbnail((64, 64))
            bg = Image.new('RGB', (64, 64), (0, 0, 0))

            # Paste the image onto the center of the background
            bg.paste(img, (round(bg.width / 2 - img.width / 2), round(bg.height / 2 - img.height / 2)))

            # Write the changes back to the copy on disc
            img = bg
            img.save(thumbnail_image_path)

            return thumbnail_image_path
        except UnidentifiedImageError:
            Logger.getInstance().Log(
                f"Unable to generate thumbnail for '{full_image_path}' as it does not appear to be an image")

        return ""

    def GetThumbnail(self, path: str) -> str:
        """
        Given a relative file path to an image with the Content folder as the root, check if there is a matching
        thumbnail in the thumbnails directory. Returns the thumbnail file path if found. Otherwise, returns an empty string
        """
        # Full path to the thumbnail (Remove the root folder for 'path' as we need the thumbnail folder to be the root)
        thumbnail_image_path = f"{settings.user_project_dir}/Thumbnails/{'/'.join(path.split('/')[1:])}"
        if os.path.exists(thumbnail_image_path):
            return thumbnail_image_path
        else:
            return ""
