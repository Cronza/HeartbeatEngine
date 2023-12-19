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
import os, errno
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
from HBEditor.Core.engine_launcher import EngineLauncher
from HBEditor.Core.EditorInterface.dialog_new_interface import DialogNewInterface
from HBEditor.Core.Dialogs.dialog_file_system import DialogFileSystem
from HBEditor.Core.Dialogs.dialog_list import DialogList
from HBEditor.Core.EditorDialogue.editor_dialogue import EditorDialogue
from HBEditor.Core.EditorScene.editor_scene import EditorScene
from HBEditor.Core.EditorInterface.editor_interface import EditorInterface
from HBEditor.Core.EditorProjectSettings.editor_project_settings import EditorProjectSettings
from HBEditor.Core.EditorValues.editor_values import EditorValues
from HBEditor.Core.EditorUtilities import path
from Tools.HBBuilder.hb_builder import HBBuilder
from Tools.HBYaml.hb_yaml import Reader, Writer


class HBEditor:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)

        self.e_ui = hbe.HBEditorUI(self)

        # Track which editor is currently active
        self.active_editor = None

        # Show the interface. This suspends execution until the interface is closed, meaning the proceeding exit command
        # will be ran only then
        self.e_ui.Show()
        sys.exit(self.app.exec_())

    def NewProject(self):
        """
        Prompts the user for a directory to create a new project, and for a project name. Then creates the
        chosen project
        """
        Logger.getInstance().Log("Requesting directory for the new project...'")
        prompt = DialogFileSystem(self.e_ui.GetWindow())
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
                self.e_ui.GetWindow(),
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
                        self.e_ui.GetWindow(),
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
                    for key, rel_path in settings.project_default_files:
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
        prompt = DialogFileSystem(self.e_ui.GetWindow())
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
                    self.e_ui.GetWindow(),
                    "Not a Valid Project Directory!",
                    "The chosen directory is not a valid Heartbeat project.\n"
                    "Please either choose a different project, or create a new project."
                )

    def NewFolder(self, parent_dir: str, folder_name: str = "", batch_mode: bool = False) -> str:
        """
        Given a partial path with the content folder as the root, prompt the user to create a new directory in that
        location. If 'folder_name' is provided, skip prompting the user, and instead attempt to create a directory using
        that name. If 'batch_mode' is True, disable prompts. If successful, register it and return the
        folder name. Otherwise, return an empty string
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            if not folder_name:
                folder_name = QtWidgets.QInputDialog.getText(
                    self.e_ui.GetWindow(),
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
                        self.ShowFileAlreadyExistsPrompt(batch_mode)
                        return ""
                else:
                    self.ShowInvalidFileNamePrompt(batch_mode)

        return ""

    def NewFile(self, parent_dir: str, file_type: FileType) -> str:
        """
        Given a partial path with the content folder as the root, prompt the user to create a new file in that
        location. If successful, register that file in the asset registry and return the name. Otherwise, return ""
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            selected_name = QtWidgets.QInputDialog.getText(
                self.e_ui.GetWindow(),
                f"New {file_type.name}",
                "Please Enter a File Name:"
            )[0]
            if not selected_name:
                Logger.getInstance().Log("File name was not provided - Cancelling 'New File' action", 3)
            else:
                if self.ValidateFileName(selected_name):
                    file_name = f"{selected_name}.{file_type.name.lower()}"
                    full_path = f"{settings.user_project_dir}/{parent_dir}/{file_name}"
                    if not os.path.exists(full_path):
                        with open(full_path, 'w'):
                            Logger.getInstance().Log(f"File created - {full_path}", 2)

                        settings.RegisterAsset(parent_dir, file_name, file_type)

                        # Create the editor, then export to initially populate the new file
                        self.OpenEditor(full_path, file_type)
                        self.active_editor.Export()
                        return file_name
                    else:
                        self.ShowFileAlreadyExistsPrompt()
                else:
                    self.ShowInvalidFileNamePrompt()

        return ""

    def NewInterface(self, parent_dir: str) -> str:
        """
        Given a partial path with the content folder as the root, prompt the user to create a new interface in that
        location. If successful, register that file in the asset registry and return the name of the file.
        Otherwise, return ""
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            new_interface_prompt = DialogNewInterface()
            exit_code = new_interface_prompt.exec()
            if exit_code:
                selected_name = new_interface_prompt.GetName()
                selected_template_path = new_interface_prompt.GetSelection()
                if self.ValidateFileName(selected_name):
                    file_name = f"{selected_name}.interface"
                    full_path = f"{settings.user_project_dir}/{parent_dir}/{file_name}"

                    if not os.path.exists(full_path):
                        # Create the interface file. If the user chose to create using a template, we need to clone
                        # that file into the project instead
                        if selected_template_path:
                            shutil.copy(path.ResolveFilePath(selected_template_path), full_path)
                        else:
                            with open(full_path, 'w'):
                                Logger.getInstance().Log(f"File created - {full_path}", 2)

                        settings.RegisterAsset(parent_dir, file_name, FileType.Interface)

                        # Create the editor, then export to initially populate the new file. If the user chose to create
                        # using a template, import it instead and skip the initial export
                        if selected_template_path:
                            self.OpenEditor(full_path, FileType.Interface, True)
                        else:
                            self.OpenEditor(full_path, FileType.Interface)
                            self.active_editor.Export()

                        return file_name
                    else:
                        self.ShowFileAlreadyExistsPrompt()
                else:
                    self.ShowInvalidFileNamePrompt()

        return ""

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

                # Delete the file or folder
                try:
                    if is_folder:
                        shutil.rmtree(full_path)
                    else:
                        try:
                            os.remove(full_path)
                        except OSError as exc:
                            if exc.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                                raise exc

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
                        settings.DuplicateAssetRegistration(partial_file_path, orig_name, copy_name)
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
                self.e_ui.GetWindow(),
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
                                settings.RenameAssetRegistration(partial_file_path, os.path.basename(full_path), os.path.basename(new_full_path))
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
        path, deregistering and registering as appropriate. If the target is a file, then the move automatically fails.
        Return whether the move was successful
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            src_full_path = f"{settings.user_project_dir}/{src_partial_path}"
            tar_full_path = f"{settings.user_project_dir}/{tar_partial_path}"

            # Only directories are valid targets. Fail silently if the user targeted a file
            if os.path.isfile(tar_full_path):
                Logger.getInstance().Log(f"Failed to move path '{src_full_path}' to '{tar_full_path}' - Invalid destination", 3)
                return False

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
            return False
        else:
            full_path = f"{settings.user_project_dir}/{partial_file_path}"

            # Validate whether the selected file is capable of being opened
            # Note: This is expected to change in a future release
            file_type = None
            if ".interface" in partial_file_path: file_type = FileType.Interface
            elif ".scene" in partial_file_path: file_type = FileType.Scene
            elif ".dialogue" in partial_file_path: file_type = FileType.Dialogue
            else:
                Logger.getInstance().Log("File type does not have any interact functionality", 3)
                return False

            self.OpenEditor(full_path, file_type, True)
            return True


    def Import(self, partial_dest_path: str, import_target: str = "", batch_mode: bool = False) -> bool:
        """
        Given a partial path with the content folder as the root, prompt the user to choose a file to import. Then,
        go through a series of validations before copying the file into the project and registering it. If
        'import_target' is provided (as an absolute path), skip prompting the user for a path, and instead attempt to
        import it instead. If 'batch_mode' is True, disable prompts. Returns whether the import was successful.
        """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            full_path = f"{settings.user_project_dir}/{partial_dest_path}"

            # If no import target is provided, then prompt the user to pick one
            if not import_target:
                import_target = QtWidgets.QFileDialog.getOpenFileName(
                    self.e_ui.GetWindow(),
                    "Choose a file to Import"
                )[0]

            if import_target:
                if self.ValidateImportTarget(import_target, partial_dest_path, batch_mode):
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

    def BatchImport(self, partial_dest_path: str, paths_to_import: list, initial_iter: bool = True):
        """
        Given a partial path with the content folder as the root and a list of absolute file paths, import each file. If
        any are folders, recursively import all child items and folders.This runs in 'batch_mode', which disables error
        and warning prompts during importing
        """
        problematic_files = []
        for target_index in range(0, len(paths_to_import)):
            import_target = paths_to_import[target_index]
            if os.path.isdir(import_target):
                # Create the folder (even if all children fail to import)
                self.NewFolder(partial_dest_path, os.path.basename(import_target), True)

                # Collect a list of the child paths (reconstructing them to be absolute paths)
                contents = os.listdir(import_target)
                for i in range(0, len(contents)):
                    contents[i] = os.path.join(import_target, contents[i]).replace("\\", "/")

                # Recursively batch import child items
                problematic_files.extend(self.BatchImport(f"{partial_dest_path}/{os.path.basename(import_target)}", contents, False))
            else:
                if not self.Import(partial_dest_path, import_target, True):
                    problematic_files.append(import_target)

        if initial_iter:
            if problematic_files:
                DialogList("Failed to Import", "The following files failed to import", problematic_files).exec()

        return problematic_files


    def Play(self):
        """ Launches the HBEngine, temporarily suspending the HBEditor """
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        elif not settings.user_project_data["Game"]["starting_scene"]:
            self.ShowNoStartingScenePrompt()
        else:
            p_manager = EngineLauncher()
            p_manager.Play(self.e_ui.GetWindow(), settings.user_project_dir, settings.root)

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

    def OpenEditor(self, target_file_path: str, editor_type: FileType, import_file: bool = False):
        """ Creates an editor tab based on the provided file information """
        editor_classes = {
            FileType.Scene: EditorScene,
            FileType.Dialogue: EditorDialogue,
            FileType.Interface: EditorInterface,
            FileType.Project_Settings: EditorProjectSettings,
            FileType.Values: EditorValues
         }

        # Let's check if we already have an editor open for this file
        result = self.CheckIfFileOpen(target_file_path)
        if result:
            Logger.getInstance().Log("An editor for the selected file is already open - Switching to the open editor ", 3)
            self.e_ui.main_tab_widget.setCurrentWidget(result.editor_ui)
            self.active_editor = result
        else:
            # Initialize the Editor
            self.active_editor = editor_classes[editor_type](target_file_path)
            if import_file:
                self.active_editor.Import()

            # Create a tab to house the editor UI
            self.e_ui.AddMainTab(self.active_editor.GetUI(), os.path.basename(target_file_path), True)

    def CloseEditor(self, target_file_path: str):
        """
        Closes the editor that is open for the provided file path
        """
        for tab_index in range(0, self.e_ui.main_tab_widget.count()):
            open_editor = self.e_ui.main_tab_widget.widget(tab_index)

            if open_editor.core.file_path == target_file_path:
                self.e_ui.RemoveTab(tab_index)
                break

    def SetActiveProject(self, project_name, project_dir):
        """ Sets the active project, pointing the editor to the new location, and refreshing the interface """
        settings.user_project_name = project_name
        settings.user_project_dir = project_dir.replace("\\", "/")
        settings.LoadProjectSettings()
        settings.LoadHeartbeatFile()

        # Inform the U.I so it cleans up and prepares the U.I
        self.e_ui.SetActiveProject()

    def OpenProjectSettings(self):
        """ Opens the 'Project Settings' editor """
        # Normally we would have loaded this editor like the others, but since we need to bind loading this to a menu
        # button, we need it in the form of a function
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            self.OpenEditor(settings.GetProjectSettingsPath(), FileType.Project_Settings, True)

    def OpenValues(self):
        """ Opens the 'Values' editor """
        # Normally we would have loaded this editor like the others, but since we need to bind loading this to a menu
        # button, we need it in the form of a function
        if not settings.user_project_name:
            self.ShowNoActiveProjectPrompt()
        else:
            self.OpenEditor(settings.GetValuesPath(), FileType.Values, True)

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
        for tab_index in range(0, self.e_ui.main_tab_widget.count()):
            open_editor = self.e_ui.main_tab_widget.widget(tab_index)
            if open_editor.core.file_path == file_path:
                return open_editor.core

        return None

    def ValidateFileName(self, name_no_ext: str) -> bool:
        """
        Validates the given file name for any illegal characters (Ex. ?!$*) or reserved words (Ex. HBEngine).
        If none are found, return True
        """
        has_invalid_char = any(not char.isalnum() and char != "_" and char != "-" for char in name_no_ext)
        has_reserved_word = name_no_ext.lower() == "hbengine"

        return has_invalid_char is False and has_reserved_word is False

    def ValidateImportTarget(self, tar_full_path: str, import_dest: str, batch_mode: bool = False) -> bool:
        """ Given a file path, validate and return a bool for whether it's a valid import target. If 'batch_mode' is
        True, disable prompts """
        tar_name = os.path.basename(tar_full_path)

        # Check 1: Is this file type supported?
        tar_ext = os.path.splitext(tar_full_path)[1]
        if tar_ext not in settings.supported_file_types:
            self.ShowUnsupportedFileTypePrompt(batch_mode)
            return False

        # Check 2: Does it have an acceptable name? This check will flag extensions as problematic, so strip that
        if not self.ValidateFileName(os.path.splitext(tar_name)[0]):
            self.ShowInvalidFileNamePrompt(batch_mode)
            return False

        # Check 3: Does that item already exist within the project? This checks the asset registry and current
        #          directory (Also known as import_dest). Due to possible import complications with files that reside
        #          within the project, prohibit any import from within the project's content directory
        if tar_name in settings.GetAssetRegistryFolder(import_dest) or \
               os.path.exists(os.path.join(settings.user_project_dir, import_dest, tar_name).replace("\\", "/")):
            self.ShowFileAlreadyExistsPrompt(batch_mode)
            return False
        elif settings.GetProjectContentDirectory() in tar_full_path:
            self.ShowInternalImportErrorPrompt(batch_mode)
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

    def ShowNoActiveProjectPrompt(self):
        Logger.getInstance().Log("There is no active project", 4)
        QtWidgets.QMessageBox.about( # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.GetWindow(),
            "No Active Project",
            "There is currently no project open.\n"
            "Please either open an existing project, or create a new one."
        )

    def ShowFileAlreadyExistsPrompt(self, batch_mode: bool = False):
        Logger.getInstance().Log("A file / folder of that name already exists", 4)
        if not batch_mode: QtWidgets.QMessageBox.about( # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.GetWindow(),
            "File / Folder Already Exists",
            "The file / folder already exists."
        )

    def ShowNoStartingScenePrompt(self, batch_mode: bool = False):
        Logger.getInstance().Log("There is no starting scene set", 4)
        if not batch_mode: QtWidgets.QMessageBox.about( # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.GetWindow(),
            "No Starting Scene",
            "There is currently no starting scene.\n"
            "Please open the project settings and choose a starting scene."
        )

    def ShowUnsupportedFileTypePrompt(self, batch_mode: bool = False):
        Logger.getInstance().Log("The chosen file type is unsupported", 4)
        if not batch_mode: QtWidgets.QMessageBox.about( # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.GetWindow(),
            "Unsupported File Type",
            "The chosen file type is not supported.\n"
        )

    def ShowInvalidFileNamePrompt(self, batch_mode: bool = False):
        Logger.getInstance().Log("The chosen file has an invalid name. Please remove special characters such as ?!(+",4)
        if not batch_mode: QtWidgets.QMessageBox.about(  # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.GetWindow(),
            "Invalid Name",
            "The chosen file name contains illegal characters, or reserved words. Please remove them before "
            "trying again."
        )

    def ShowInternalImportErrorPrompt(self, batch_mode: bool = False):
        Logger.getInstance().Log("The chosen file has an invalid name. Please remove special characters such as ?!(+",4)
        if not batch_mode: QtWidgets.QMessageBox.about(  # @TODO: Replace with a custom wrapper that removes the large icon
            self.e_ui.GetWindow(),
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
            self.e_ui.GetWindow(),
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
            self.e_ui.GetWindow(),
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
