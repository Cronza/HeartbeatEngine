import copy, os
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core import settings
from HBEditor.Core.EditorUtilities import image_handler as ih


class AssetBrowser(QtWidgets.QDialog):
    def __init__(self, type_filter: set):
        super().__init__()

        # A list of 'FileType' that controls the available files in this browser
        self.type_filter = type_filter

        # Hide the OS header to lock its position
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.resize(640, 480)
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Options - Search and Active Content Directory
        self.options_layout = QtWidgets.QHBoxLayout(self)
        self.search_input = QtWidgets.QLineEdit(self)
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textEdited.connect(self.GetSearchedAssets)  # Re-search on every char input
        self.options_layout.addWidget(self.search_input, 2)
        self.content_dirs = QtWidgets.QComboBox(self)
        self.content_dirs.addItems(["Project", "Engine"])
        self.content_dirs.currentIndexChanged.connect(self.SwitchContentDirectories)
        self.options_layout.addWidget(self.content_dirs, 1)
        self.main_layout.addLayout(self.options_layout)

        # Asset List
        self.asset_list = QtWidgets.QTableWidget(self)
        self.asset_list.verticalHeader().setObjectName("vertical")
        self.asset_list.setColumnCount(4)
        self.asset_list.setShowGrid(False)
        self.asset_list.setTextElideMode(QtCore.Qt.ElideRight)
        self.asset_list.setWordWrap(False)
        self.asset_list.horizontalHeader().hide()
        self.asset_list.verticalHeader().hide()
        self.asset_list.hideColumn(0)  # Hide the thumbnail column by default
        self.asset_list.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.asset_list.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.asset_list.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.asset_list.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.asset_list.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)

        self.asset_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Disable editing
        self.asset_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # Disable multi-selection
        self.asset_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Disables cell selection
        self.asset_list.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.asset_list.setIconSize(QtCore.QSize(
            settings.editor_data["Outliner"]["icon_size"][0],
            settings.editor_data["Outliner"]["icon_size"][1]
        ))

        # 'outline: none;' doesn't work for table widgets seemingly, so I can't use CSS to disable the
        # focus border. Thus, we do it the slightly more tragic way
        self.asset_list.setFocusPolicy(QtCore.Qt.NoFocus)
        self.main_layout.addWidget(self.asset_list)

        # Confirmation Buttons
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

        # Fetch a list of assets that match the file types provided to this browser, then populate the asset list
        self.SwitchContentDirectories()

    def GetAsset(self) -> str:
        """
        Activate the dialog, and return the full path of the selected asset. If none were chosen, return an
        empty string
        """
        if self.exec():
            selection = self.asset_list.selectedItems()
            if selection:
                if self.asset_list.isColumnHidden(0):
                    asset_name = selection[0].text()
                    asset_path = selection[1].text()
                else:
                    asset_name = selection[1].text()
                    asset_path = selection[2].text()

                if self.GetUsingEngineContent():
                    return f"HBEngine/{asset_path}/{asset_name}"
                else:
                    return f"{asset_path}/{asset_name}"

        return ""

    def GetFilteredAssets(self, cur_depth: dict, cur_path: list = None) -> list:
        """
        Scan the asset registry and return a list of all assets that match this class's 'type_filter'. Return a
        tri-component tuple: <name, type, path>
        """
        assets = []
        if cur_path is None:
            cur_path = []
        for asset, data in cur_depth.items():
            # Is this asset a folder?
            if isinstance(data, dict):
                cur_path.append(asset)  # Prepare the depth for the next recurse
                assets.extend(self.GetFilteredAssets(cur_depth[asset], cur_path))
                cur_path.pop()  # Remove the extra depth as we're no longer there
            else:
                if FileType[data] in self.type_filter:
                    assets.append((asset, data, "/".join(copy.deepcopy(cur_path))))

        return assets

    def GetSearchedAssets(self):
        """ Use the search_input text to hide all assets that don't have it as a substring. Reveal those that do """
        self.asset_list.clearSelection()
        search_criteria = self.search_input.text().lower()
        for row in range(0, self.asset_list.rowCount()):
            asset_name = self.asset_list.item(row, 0).text().lower()
            if search_criteria not in asset_name:
                self.asset_list.hideRow(row)
            else:
                self.asset_list.showRow(row)

    def GenerateAssetEntries(self):
        """ Create an entry for each asset in 'valid_assets', then add them to 'asset_list' """
        for asset_name, asset_type, asset_path in self.valid_assets:
            self.asset_list.insertRow(self.asset_list.rowCount())

            # Thumbnail (Only applicable if a thumbnail is available, otherwise the column is hidden)
            thumbnail = ih.GetThumbnail(f"{asset_path}/{asset_name}")
            if thumbnail:
                if self.asset_list.isColumnHidden(0):
                    self.asset_list.showColumn(0)

                thumbnail_item = QtGui.QIcon(QtGui.QPixmap(thumbnail))
                self.asset_list.setItem(self.asset_list.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(thumbnail_item, ""))

            # Name
            self.asset_list.setItem(self.asset_list.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(asset_name))

            # Path
            path_item = QtWidgets.QTableWidgetItem(asset_path)
            path_item.setToolTip(asset_path)
            self.asset_list.setItem(self.asset_list.rowCount() - 1, 2, path_item)

            # Type
            type_item = QtWidgets.QTableWidgetItem(asset_type)
            self.asset_list.setItem(self.asset_list.rowCount() - 1, 3, type_item)

        # If thumbnails are displayed, resize each row to fit them
        if not self.asset_list.isColumnHidden(0):
            self.asset_list.resizeRowsToContents()

    def SwitchContentDirectories(self):
        """
        Reloads the entry list and valid_assets list based on whether 'content_dirs' is set to the
        project or engine
        """
        self.asset_list.hideColumn(0)  # Rehide the thumbnail column in case it was previously displayed
        self.asset_list.setRowCount(0)
        if self.GetUsingEngineContent():
            self.valid_assets = self.GetFilteredAssets(settings.engine_asset_registry)
            self.GenerateAssetEntries()
        else:
            self.valid_assets = self.GetFilteredAssets(settings.asset_registry)
            self.GenerateAssetEntries()

    def GetUsingEngineContent(self) -> bool:
        return self.content_dirs.currentText() == "Engine"
