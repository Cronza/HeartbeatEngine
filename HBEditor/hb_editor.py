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
import sys
import shutil
import re
from pathlib import Path
from PyQt5 import QtWidgets

from HBEditor import hb_editor_ui as hbe
from HBEditor.Content import content
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core import settings
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.play_manager import PlayManager
from HBEditor.Core.Menus.NewSceneMenu.new_scene_menu import NewSceneMenu
from HBEditor.Core.Prompts.file_system_prompt import FileSystemPrompt
from HBEditor.Core.EditorDialogue.editor_dialogue import EditorDialogue
from HBEditor.Core.EditorPointAndClick.editor_pointandclick import EditorPointAndClick
from HBEditor.Core.EditorProjectSettings.editor_project_settings import EditorProjectSettings
from Tools.HBBuilder.hb_builder import HBBuilder
from Tools.HBYaml.hb_yaml import Reader, Writer


class HBEditor:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)

        self.main_window = QtWidgets.QMainWindow()
        self.e_ui = hbe.HBEditorUI(self)
        self.e_ui.setupUi(self.main_window)

        self.outliner = None  # Assignment happens once a project is loaded
        self.active_editor = None

        # Show the interface. This suspends execution until the interface is closed, meaning the proceeding exit command
        # will be ran only then
        self.main_window.show()

        sys.exit(self.app.exec_())

    def NewProject(self):
        """
        Prompts the user for a directory to create a new project, and for a project name. Then creates the
        chosen project
        """
        Logger.getInstance().Log("Requesting directory for the new project...'")
        prompt = FileSystemPrompt(self.main_window)
        new_project_dir = prompt.GetDirectory(
            self.GetLastSearchPath(),
            "Choose a Directory to Create a Project",
            False
        )
        self.UpdateSearchHistory(new_project_dir)

        if not new_project_dir:
            Logger.getInstance().Log("Project directory was not provided - Cancelling 'New Project' action", 3)
        else:
            # [0] = user_input: str, [1] = value_provided: bool
            Logger.getInstance().Log("Requesting a name for the new project...'")
            user_project_name = QtWidgets.QInputDialog.getText(
                self.e_ui.central_widget,
                "New Project",
                "Please Enter a Project Name:"
            )[0]

            if not user_project_name:
                Logger.getInstance().Log("Project name was not provided - Cancelling 'New Project' action", 3)
            else:
                # Check if the project folder exists. If so, inform the user that this is already a project dir
                if os.path.exists(new_project_dir + "/" + user_project_name):
                    Logger.getInstance().Log("Chosen project directory already exists - Cancelling 'New Project' action", 4)
                    QtWidgets.QMessageBox.about(
                        self.e_ui.central_widget,
                        "Project Already Exists!",
                        "The chosen directory already contains a project of the chosen name.\n"
                        "Please either delete this project, or choose another directory"
                    )

                # Everything is good to go. Create a new project!
                else:
                    Logger.getInstance().Log("Valid project destination chosen! Creating project folder structure...")

                    # Create the project directory
                    project_path = new_project_dir + "/" + user_project_name
                    os.mkdir(project_path)

                    # Create the pre-requisite project folders
                    for main_dir in settings.project_folder_structure:
                        main_dir_path = project_path + "/" + main_dir
                        os.mkdir(main_dir_path)

                    # Create the heartbeat file, containing asset registrations for the project
                    heartbeat_file = f"{project_path}/{settings.heartbeat_file}"
                    Writer.WriteFile({"Content": {}}, heartbeat_file, settings.GetMetadataString())

                    # Clone project default files
                    for key, rel_path in settings.project_default_files.items():
                        shutil.copy(
                            settings.engine_root + "/" + rel_path,
                            project_path + "/" + rel_path
                        )

                    Logger.getInstance().Log(f"Project Created at: {project_path}", 2)

                    # Set this as the active project
                    self.SetActiveProject(user_project_name, project_path)

    def OpenProject(self):
        """ Prompts the user for a project directory, then loads that file in the respective editor """
        Logger.getInstance().Log("Requesting path to project root...")
        prompt = FileSystemPrompt(self.main_window)
        existing_project_dir = prompt.GetDirectory(
            self.GetLastSearchPath(),
            "Choose a Project Directory",
            False
         )
        self.UpdateSearchHistory(existing_project_dir)

        if not existing_project_dir:
            Logger.getInstance().Log("Project directory was not provided - Cancelling 'Open Project' action", 3)
        else:
            # Does the directory already have a project in it (Denoted by the heartbeat file's existence)
            if os.path.exists(f"{existing_project_dir}/{settings.heartbeat_file}"):
                Logger.getInstance().Log("Valid project selected - Setting as Active Project...")

                # Since we aren't asking for the project name, let's infer it from the path
                project_name = os.path.basename(existing_project_dir)
                self.SetActiveProject(project_name, existing_project_dir)
            else:
                Logger.getInstance().Log("An invalid Heartbeat project was selected - Cancelling 'Open Project' action", 4)
                QtWidgets.QMessageBox.about(
                    self.e_ui.central_widget,
                    "Not a Valid Project Directory!",
                    "The chosen directory is not a valid Heartbeat project.\n"
                    "Please either choose a different project, or create a new project."
                )

    def NewFolder(self, parent_dir: str) -> str:
        """
        Given a partial path with the content folder as the root, prompt the user to create a new directory in that
        location. If successful, register it and return the folder name. Otherwise, return an empty string
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            folder_name = QtWidgets.QInputDialog.getText(
                self.e_ui.central_widget,
                "New Folder",
                "Please Enter a Folder Name:"
            )[0]

            if folder_name:
                if self.ValidateFileName(folder_name):
                    # Add the folder name to the current working dir to get a full path
                    full_path = f"{settings.user_project_dir}/{parent_dir}/{folder_name}"

                    # Confirm that the folder doesn't already exist. If not, then create it. Otherwise, raise an error
                    if not os.path.exists(full_path):
                        os.mkdir(full_path)
                        Logger.getInstance().Log(f"Folder created - {full_path}", 2)
                        settings.RegisterAssetFolder(f"{parent_dir}/{folder_name}")
                        return folder_name
                    else:
                        self.ShowFileAlreadyExistsPrompt()
                        return ""
                else:
                    self.ShowInvalidFileNamePrompt()

        return ""

    def NewScene(self, parent_dir: str) -> tuple:
        """
        Given a partial path with the content folder as the root, prompt the user to create a new scene in that
        location. If successful, register that file in the asset registry and return the name and type of the file.
        Otherwise, return "", None
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            new_scene_prompt = NewSceneMenu()
            new_scene_prompt.exec()
            selected_name = new_scene_prompt.GetName()
            selected_type = new_scene_prompt.GetSelection()

            if selected_name:
                if self.ValidateFileName(selected_name):
                    file_name = f"{selected_name}.yaml"
                    full_path = f"{settings.user_project_dir}/{parent_dir}/{file_name}"
                    if not os.path.exists(full_path):
                        with open(full_path, 'w'):
                            Logger.getInstance().Log(f"File created - {full_path}", 2)

                        settings.RegisterAsset(parent_dir, file_name, selected_type)

                        # Create the editor, then export to initially populate the new file
                        self.OpenEditor(full_path, selected_type)
                        self.active_editor.Export()
                        return file_name, selected_type
                    else:
                        self.ShowFileAlreadyExistsPrompt()
                else:
                    self.ShowInvalidFileNamePrompt()

        return "", None

    def DeleteFileOrFolder(self, partial_file_path: str, is_folder: True) -> bool:
        """
        Given a partial path with the content folder as the root, prompt the user for confirmation before deleting
        the provided file. If there is an open editor for that file, inform the user of it before forcefully closing it.
        If the path is to a directory, recursively scan the directory tree, and close all open editors. Return whether
        the deletion was successful
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            full_path = f"{settings.user_project_dir}/{partial_file_path}"

            # Check for open editors that might need to be closed prior to performing this action
            open_files = []
            files_open = False
            if is_folder:
                open_files = self.CheckForOpenFiles(full_path)
                files_open = open_files != []
            else:
                files_open = self.CheckIfFileOpen(full_path)

            # Confirm with the user that we're okay to proceed
            result = self.ShowConfirmModificationPrompt(
                files_open,
                "Delete",
                "Deleting",
                partial_file_path
            )
            if result:
                # Close any related editors
                if is_folder:
                    for f in open_files:
                        self.CloseEditor(f)
                else:
                    self.CloseEditor(full_path)

                try:
                    if is_folder:
                        shutil.rmtree(full_path)
                    else:
                        os.remove(full_path)
                except Exception as exc:
                    Logger.getInstance().Log(f"Failed to delete '{full_path}' - Please review the exception to understand more\n{exc}", 4)
                else:
                    settings.DeregisterAsset(partial_file_path, os.path.basename(full_path))
                    Logger.getInstance().Log(f"Successfully deleted '{full_path}'", 2)
                    return True

        return False

    def DuplicateFileOrFolder(self, partial_file_path: str, is_folder: bool = False) -> bool:
        """
        Given a partial path with the content folder as the root, duplicate the file or folder and assign a temp name.
        Return whether the duplication was successful
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            full_path = f"{settings.user_project_dir}/{partial_file_path}"
            orig_parent_dir = os.path.dirname(full_path)
            orig_name = os.path.basename(full_path)

            # Try up to 9999 permutations of a temp name before erroring out
            for name_index in range(0, 9999):
                copy_name = f"Copy{name_index}_{orig_name}"
                copy_full_path = os.path.join(orig_parent_dir, copy_name)
                if not os.path.exists(copy_full_path):
                    try:
                        if is_folder:
                            shutil.copytree(full_path, copy_full_path)
                        else:
                            shutil.copy(full_path, copy_full_path)
                    except Exception as exc:
                        Logger.getInstance().Log(f"Failed to duplicate path '{full_path}' - Please review the exception to understand more\n{exc}",4)
                        return False
                    else:
                        settings.DuplicateAssetRegistration(os.path.dirname(partial_file_path), orig_name, copy_name)
                        Logger.getInstance().Log(f"Successfully duplicated file '{full_path}'", 2)
                        return True

            Logger.getInstance().Log(f"Failed to find an acceptable name for the duplicate file - Please contact the developer as this shouldn't happen!")

        return False

    def RenameFileOrFolder(self, partial_file_path: str, is_folder: bool) -> bool:
        """
        Given a partial path with the content folder as the root, prompt the player for a new name for the file or
        folder. If a name was provided, rename and reregister the file. Return whether the rename was successful
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            full_path = f"{settings.user_project_dir}/{partial_file_path}"

            new_name = QtWidgets.QInputDialog.getText(
                self.e_ui.central_widget,
                "Rename",
                "Please Enter a New Name:"
            )[0]
            if new_name:
                if self.ValidateFileName(new_name):
                    orig_file_ext = os.path.splitext(full_path)[1]
                    new_full_path = f"{os.path.dirname(full_path)}/{new_name}{orig_file_ext}"
                    if not os.path.exists(new_full_path):
                        # Check for open editors that might need to be closed prior to performing this action
                        open_files = []
                        files_open = False
                        if is_folder:
                            open_files = self.CheckForOpenFiles(full_path)
                            files_open = open_files != []
                        else:
                            files_open = self.CheckIfFileOpen(full_path)

                        # Check if the file is open in the editor
                        result = self.ShowConfirmModificationPrompt(
                            files_open,
                            "Rename",
                            "Renaming",
                            partial_file_path
                        )
                        if result:
                            # Close any related editors
                            if is_folder:
                                for f in open_files:
                                    self.CloseEditor(f)
                            else:
                                self.CloseEditor(full_path)
                            try:
                                os.rename(full_path, new_full_path)
                            except Exception as exc:
                                Logger.getInstance().Log(f"Failed to duplicate path '{full_path}' - Please review the exception to understand more\n{exc}", 4)
                            else:
                                settings.RenameAssetRegistration(os.path.dirname(partial_file_path), os.path.basename(full_path), os.path.basename(new_full_path))
                                self.CloseEditor(full_path)
                                Logger.getInstance().Log(f"Successfully renamed '{new_full_path}'", 2)
                                return True
                    else:
                        self.ShowFileAlreadyExistsPrompt()
                else:
                    self.ShowInvalidFileNamePrompt()

            return False

    def MoveFileOrFolder(self, src_partial_path: str, tar_partial_path: str) -> bool:
        """
        Given a source and target partial path with the content folder as the roots, move the source path to the target
        path, deregistering and registering as appropriate. Return whether the move was successful
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            src_full_path = f"{settings.user_project_dir}/{src_partial_path}"
            tar_full_path = f"{settings.user_project_dir}/{tar_partial_path}"
            is_folder = os.path.isdir(src_full_path)
            source_name = os.path.basename(src_full_path)

            if not os.path.exists(f"{tar_full_path}/{source_name}"):
                # Check for open editors that might need to be closed prior to performing this action
                open_files = []
                files_open = False
                if is_folder:
                    open_files = self.CheckForOpenFiles(src_full_path)
                    files_open = open_files != []
                else:
                    files_open = self.CheckIfFileOpen(src_full_path)

                # Confirm with the user that we're okay to proceed
                result = self.ShowConfirmModificationPrompt(
                    files_open,
                    "Move",
                    "Moving",
                    src_partial_path
                )
                if result:
                    # Close any related editors
                    if is_folder:
                        for f in open_files:
                            self.CloseEditor(f)
                    else:
                        self.CloseEditor(src_full_path)
                    try:
                        shutil.move(src_full_path, tar_full_path)
                    except Exception as exc:
                        Logger.getInstance().Log(f"Failed to move path '{src_full_path}' to '{tar_full_path}' - Please review the exception to understand more\n{exc}", 4)
                        return False
                    else:
                        settings.MoveAssetRegistration(src_partial_path, source_name, tar_partial_path)
                        Logger.getInstance().Log(f"Successfully moved '{tar_full_path}'", 2)
                        return True
            else:
                self.ShowFileAlreadyExistsPrompt()

        return False

    def OpenFile(self, partial_file_path: str) -> bool:
        """
        Given a partial path with the content folder as the root, determine the type of file it is before attempting
        to load the appropriate editor for it. Returns whether an editor was successfully opened
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:

            # Validate whether the selected file is capable of being opened
            # Note: This is expected to change in a future release
            if ".yaml" not in partial_file_path:
                Logger.getInstance().Log("File type does not have any interact functionality", 3)
                return False
            else:
                full_path = f"{settings.user_project_dir}/{partial_file_path}"
                # Read the first line to determine the type of file
                with open(full_path) as f:
                    # Check the metadata at the top of the file to see which file type this is
                    line = f.readline()
                    search = re.search("# Type: (.*)", line)

                    # Was the expected metadata found?
                    if search:
                        file_type = FileType[search.group(1)]
                        self.OpenEditor(full_path, file_type, True)
                        return True
                    else:
                        Logger.getInstance().Log("An invalid file was selected - Cancelling 'Open File' action", 4)
                        QtWidgets.QMessageBox.about(
                            self.e_ui.central_widget,
                            "Not a Valid File!",
                            "The chosen file was not created by the HBEditor.\n"
                             "Please either choose a different file, or create a new one.\n\n"
                            "If you authored this file by hand, please add the correct metadata to the top of the file"
                        )
        return False

    def Import(self, partial_dest_path: str) -> bool:
        """
        Given a partial path with the content folder as the root, prompt the user to choose a file to import. Then,
        go through a series of validations before copying the file into the project and registering it. Returns whether
        the import was successful.
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            full_path = f"{settings.user_project_dir}/{partial_dest_path}"
            import_target = QtWidgets.QFileDialog.getOpenFileName(
                self.e_ui.central_widget,
                "Choose a file to Import"
            )[0]

            if import_target:
                if self.ValidateImportTarget(import_target, partial_dest_path):
                    tar_name = os.path.basename(import_target)
                    tar_type = settings.supported_file_types[os.path.splitext(tar_name)[1]]

                    # Perform additional processing to differentiate core .yaml files (Scene, Character, etc) from
                    # generic data files
                    if tar_type is FileType.Asset_Data:
                        tar_type = self.GetYAMLFileType(import_target)
                    try:
                        shutil.copy(import_target, full_path)
                    except Exception as exc:
                        Logger.getInstance().Log(f"Failed to copy '{import_target}' to '{full_path}' - Please review the exception to understand more\n{exc}",4)
                    else:
                        settings.RegisterAsset(partial_dest_path, tar_name, tar_type)
                        Logger.getInstance().Log(f"Successfully imported file '{partial_dest_path}/{tar_name}'", 2)
                        return True

        return False

    def Play(self):
        """ Launches the HBEngine, temporarily suspending the HBEditor """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        elif not settings.user_project_data["Game"]["starting_scene"]:
            self.ShowNoStartingScenePrompt()
        else:
            p_manager = PlayManager()
            p_manager.Play(self.e_ui.central_widget, settings.user_project_dir, settings.root)

    def Build(self):
        """ Launches the HBBuilder in order to generate an executable from the active project """
        # Only allow this is there is an active project
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        elif not settings.user_project_data["Game"]["starting_scene"]:
            self.ShowNoStartingScenePrompt()
        else:
            HBBuilder.Build(
                Logger.getInstance(),
                settings.engine_root,
                settings.user_project_dir,
                settings.user_project_name
            )

    def Clean(self):
        """ Cleans the active project's build folder """
        # Only allow this is there is an active project
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            HBBuilder.Clean(
                Logger.getInstance(),
                settings.user_project_dir
            )

    def Save(self):
        """ Requests the active editor to save its data """
        # Only allow this is there is an active project
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            if self.active_editor:
                self.active_editor.Export()

    def OpenEditor(self, target_file_path, editor_type, import_file=False):
        """ Creates an editor tab based on the provided file information """
        if not settings.editor_data["EditorSettings"]["max_tabs"] <= self.e_ui.main_tab_editor.count():
            editor_classes = {
                FileType.Scene_Dialogue: EditorDialogue,
                FileType.Scene_Point_And_Click: EditorPointAndClick,
                FileType.Project_Settings: EditorProjectSettings
             }

            # Let's check if we already have an editor open for this file
            result = self.CheckIfFileOpen(target_file_path)
            if result:
                Logger.getInstance().Log("An editor for the selected file is already open - Switching to the open editor ", 3)
                self.e_ui.main_tab_editor.setCurrentWidget(result)
            else:
                # Initialize the Editor
                self.active_editor = editor_classes[editor_type](target_file_path)

                # Allow the caller to load the provided file instead of just marking it as the export target
                if import_file:
                    self.active_editor.Import()

                self.e_ui.AddTab(
                    self.active_editor.GetUI(),
                    os.path.basename(target_file_path),
                    self.e_ui.main_tab_editor
                )
        else:
            QtWidgets.QMessageBox.about(
                self.e_ui.central_widget,
                "Tab Limit Reached!",
                "You have reached the maximum number of open tabs. Please close "
                "a tab before attempting to open another"
            )

    def CloseEditor(self, target_file_path: str):
        """
        Closes the editor that is open for the provided file path
        """
        for tab_index in range(0, self.e_ui.main_tab_editor.count()):
            open_editor = self.e_ui.main_tab_editor.widget(tab_index)

            if open_editor.core.file_path == target_file_path:
                self.e_ui.RemoveTab(tab_index)
                break

    def SetActiveProject(self, project_name, project_dir):
        """ Sets the active project, pointing the editor to the new location, and refreshing the interface """
        settings.user_project_name = project_name
        settings.user_project_dir = project_dir.replace("\\", "/")
        settings.LoadProjectSettings()
        settings.LoadHeartbeatFile()

        # If this is the first time a user is loading a project after opening the editor, delete the 'Getting Started'
        # display
        if self.e_ui.getting_started_container:
            target = self.e_ui.main_resize_container.widget(0)
            target.deleteLater()
            self.e_ui.getting_started_container = None

            self.e_ui.CreateMainTabContainer()
            self.e_ui.CreateOutliner()

        # Clear any open editor tabs
        self.e_ui.main_tab_editor.clear()

        # Refresh U.I text using any active translations
        self.e_ui.retranslateUi(self.main_window)

    def OpenProjectSettings(self):
        """ Opens the 'Project Settings' editor """
        # Normally we would have loaded this editor like the others, but since we need to bind loading this to a menu
        # button, we need it in the form of a function
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            self.OpenEditor(
                settings.user_project_dir + "/" + settings.project_default_files['Config'],
                FileType.Project_Settings,
                True
            )

    def CheckForOpenFiles(self, root: str) -> list:
        """
        Walks the given directory tree, and checks if any file is opened in the editor. Returns the list of
        opened files
        """
        open_files = []
        for path, folders, files in os.walk(root):
            for f in files:
                full_file_path = os.path.join(path, f).replace("\\", "/")
                if self.CheckIfFileOpen(full_file_path):
                    open_files.append(full_file_path)

        return open_files

    def CheckIfFileOpen(self, file_path) -> object:
        """
        Checks all open editor tabs for the provided file. Returns the editor if found. Otherwise, returns None
        """
        for tab_index in range(0, self.e_ui.main_tab_editor.count()):
            open_editor = self.e_ui.main_tab_editor.widget(tab_index)
            if open_editor.core.file_path == file_path:
                return open_editor

        return None

    def ValidateFileName(self, name_no_ext: str) -> bool:
        """
        Validates the given file name for any illegal characters (Ex. ?!$*) or reserved words (Ex. HBEngine).
        If none are found, return True
        """
        has_invalid_char = any(not char.isalnum() and char != "_" and char != "-" for char in name_no_ext)
        has_reserved_word = name_no_ext.lower() == "hbengine"

        return has_invalid_char is False and has_reserved_word is False

    def ValidateImportTarget(self, tar_full_path: str, import_dest: str) -> bool:
        """ Given a file path, validate and return a bool for whether it's a valid import target """
        tar_name = os.path.basename(tar_full_path)

        # Check 1: Is this file type supported?
        tar_ext = os.path.splitext(tar_full_path)[1]
        if tar_ext not in settings.supported_file_types:
            self.ShowUnsupportedFileTypePrompt()
            return False

        # Check 2: Does it have an acceptable name? This check will flag extensions as problematic, so strip that
        if not self.ValidateFileName(os.path.splitext(tar_name)[0]):
            self.ShowInvalidFileNamePrompt()
            return False

        # Check 3: Does that item already exist within the project? This checks the asset registry and current
        #          directory (Also known as import_dest). Due to possible import complications with files that reside
        #          within the project, prohibit any import from within the project's content directory
        if tar_name in settings.GetAssetRegistryFolder(import_dest) or \
               os.path.exists(os.path.join(settings.user_project_dir, import_dest, tar_name).replace("\\", "/")):
            self.ShowFileAlreadyExistsPrompt()
            return False
        elif settings.GetProjectContentDirectory() in tar_full_path:
            self.ShowInternalImportErrorPrompt()
            return False

        # If no checks have failed, then validation complete!
        return True

    def UpdateSearchHistory(self, new_search_dir):
        """ Updates the record for the last location searched for in a file browser"""
        if new_search_dir:
            self.WriteToTemp(settings.temp_history_path, {"search_dir": new_search_dir})

    def GetLastSearchPath(self):
        """ Returns the current search path record, or if there is none, return the system home"""
        search_dir = self.ReadFromTemp(settings.temp_history_path, "search_dir")
        if search_dir:
            return search_dir
        else:
            return str(Path.home())

    def GetYAMLFileType(self, file_path: str) -> FileType:
        """
        Given a full path to a file, read it to determine its type. Return its 'FileType' if it has a defined type,
        otherwise return the generic 'Asset_Data' file type
        """
        # Read the first line to determine the type of file
        with open(file_path) as f:
            # Check the metadata at the top of the file to see which file type this is
            line = f.readline()
            search = re.search("# Type: (.*)", line)

            # Was the expected metadata found?
            if search:
                return FileType[search.group(1)]
            else:
                return FileType.Asset_Data

    def WriteToTemp(self, temp_file: str, data: dict) -> bool:
        """ Write to the provided temp file, creating it if it doesn't already exist """
        if not os.path.exists(temp_file):
            try:
                if not os.path.exists(settings.editor_temp_root):
                    os.mkdir(settings.editor_temp_root)
                with open(temp_file, "w"):
                    pass
            except Exception as exc:
                Logger.getInstance().Log(f"Unable to create '{temp_file}'", 4)
                Logger.getInstance().Log(str(exc), 4)
                return False
        temp_data = Reader.ReadAll(temp_file)
        if not temp_data:
            temp_data = {}
        try:
            for key, val in data.items():
                temp_data[key] = val
        except Exception as exc:
            Logger.getInstance().Log(f"Failed to update '{temp_file}'", 4)
            Logger.getInstance().Log(str(exc), 4)
            return False
        Writer.WriteFile(temp_data, temp_file)
        return True

    def ReadFromTemp(self, temp_file: str, key: str) -> str:
        """ Read from the provided temp file using the provided key, returning the results if found """
        if not os.path.exists(temp_file):
            Logger.getInstance().Log(f"The temp file '{temp_file}' was not found")
            return ""
        try:
            req_data = Reader.ReadAll(temp_file)[key]
            return req_data
        except Exception as exc:
            Logger.getInstance().Log(f"Failed to read '{temp_file}'")
            Logger.getInstance().Log(str(exc), 4)
            return ""

    def ShowFileAlreadyExistsPrompt(self):
        Logger.getInstance().Log("A file / folder of that name already exists", 4)
        QtWidgets.QMessageBox.about( # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.central_widget,
            "File / Folder Already Exists",
            "The file / folder already exists."
        )

    def ShowNoActiveProjectPrompt(self):
        QtWidgets.QMessageBox.about( # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.central_widget,
            "No Active Project",
            "There is currently no project open.\n"
            "Please either open an existing project, or create a new one."
        )

    def ShowNoStartingScenePrompt(self):
        QtWidgets.QMessageBox.about( # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.central_widget,
            "No Starting Scene",
            "There is currently no starting scene.\n"
            "Please open the project settings and choose a starting scene."
        )

    def ShowUnsupportedFileTypePrompt(self):
        Logger.getInstance().Log("The chosen file type is unsupported", 4)
        QtWidgets.QMessageBox.about( # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.central_widget,
            "Unsupported File Type",
            "The chosen file type is not supported.\n"
        )

    def ShowInvalidFileNamePrompt(self):
        Logger.getInstance().Log("The chosen file has an invalid name. Please remove special characters such as ?!(+",4)
        QtWidgets.QMessageBox.about(  # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.central_widget,
            "Invalid Name",
            "The chosen file name contains illegal characters, or reserved words. Please remove them before "
            "trying again."
        )

    def ShowInternalImportErrorPrompt(self):
        Logger.getInstance().Log("The chosen file has an invalid name. Please remove special characters such as ?!(+",4)
        QtWidgets.QMessageBox.about(  # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.central_widget,
            "Unable to Import",
            "The import target resides within a project's 'Content' directory, which is prohibited. This is due to"
            " potential problems that may arise from targeting files that are already registered to the project.\n\n"
            "Please move the import target to a location outside of the 'Content' directory before trying again."
        )

    def ShowConfirmModificationPrompt(self, file_open: bool, action: str, participle: str,
                                          partial_file_path: str) -> bool:
        if os.path.isfile(f"{settings.user_project_dir}/{partial_file_path}"):
            return self.ShowConfirmFileModificationPrompt(file_open, action, participle, partial_file_path)
        else:
            return self.ShowConfirmFolderModificationPrompt(file_open, action, participle, partial_file_path)

    def ShowConfirmFileModificationPrompt(self, file_open: bool, action: str, participle: str,
                                          partial_file_path: str) -> bool:
        if file_open:
            message = f"The file is open in the editor. {participle.capitalize()} this file will forcefully close " \
                      "the corresponding editor. Are you sure you want to continue with " \
                      f"{participle.lower()} the following item:\n\n'{partial_file_path}'?"
        else:
            message = f"Are you sure you want to {action.lower()} the following item:\n\n'{partial_file_path}'?"

        result = QtWidgets.QMessageBox.question(
            self.e_ui.central_widget,
            f"Confirm {action.capitalize()}",
            message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        return result == QtWidgets.QMessageBox.Yes

    def ShowConfirmFolderModificationPrompt(self, files_open: bool, action: str, participle: str,
                                            partial_folder_path: str) -> bool:
        if files_open:
            message = f"There are open files in this folder. {participle.capitalize()} it will forcefully close " \
                      "the editor for each open file. Are you sure you want to continue with " \
                      f"{participle.lower()} the following directory:\n\n'{partial_folder_path}'?\n\n" \
                      f"This may recursively impact all files and folders within this directory."
        else:
            message = f"Are you sure you want to {action.lower()} the following directory:\n'" \
                      f"{partial_folder_path}'?\n\nThis may recursively impact all files and folders " \
                      f"within this directory."

        result = QtWidgets.QMessageBox.question(
            self.e_ui.central_widget,
            f"Confirm {action.capitalize()}",
            message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        return result == QtWidgets.QMessageBox.Yes

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


sys.excepthook = except_hook

print(sys.excepthook)
if __name__ == "__main__":
    editor = HBEditor()
