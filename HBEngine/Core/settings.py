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
from Tools.HBYaml.hb_yaml import Reader, Writer


def SetProjectRoot(new_root):
    global root_dir
    global project_root

    # If a project was not provided, use the engine root (Necessary for builds where project
    # and engine are conjoined)
    if new_root:
        project_root = new_root
    else:
        project_root = root_dir


def LoadProjectSettings(partial_file_path: str = "Config/Game.yaml"):
    """ Reads in the provided project settings file path. Defaults to 'Config/Game.yaml' if no path is provided """
    global project_settings
    global resolution
    global resolution_options
    global active_resolution
    global project_setting_listeners

    file_path = ConvertPartialToAbsolutePath(partial_file_path)
    project_settings = Reader.ReadAll(file_path)

    # Initialize the listener dict with keys for each available settings
    for cat, settings in project_settings.items():
        project_setting_listeners[cat] = {}
        for name, val in settings.items():
            project_setting_listeners[cat][name] = {}

    # Apply the effects of various project settings
    resolution = project_settings['Window']['resolution']
    resolution_options = project_settings['Window']['resolution_options']
    active_resolution = tuple(resolution_options[resolution])


def SaveProjectSettings(file_path: str = "Config/Game.yaml"):
    """ Saves the project settings to the provided file path. Defaults to 'Config/Game.yaml' if no path is provided """
    global project_settings

    file_path = ConvertPartialToAbsolutePath(file_path)
    Writer.WriteFile(project_settings, file_path)


def SetProjectSetting(category: str, setting: str, value: any):
    global project_settings
    global project_setting_listeners

    # Sets the target project setting, apply the relevant functional change (IE. Editing 'mute' will mute all audio)
    if category == "Audio":
        if setting == "mute":
            if isinstance(value, bool):
                project_settings[category][setting] = value

    # Inform any applicable listeners
    for listener_name, connect_func in project_setting_listeners[category][setting].items():
        connect_func(value)

    # Save changes to ensure persistence for all changes
    SaveProjectSettings()


def GetProjectSetting(category, key):
    """ Returns the value from the global setting defined in 'Game.yaml' that matches the provided category and key """
    global project_settings
    return project_settings[category][key]


def ConvertPartialToAbsolutePath(partial_path):
    """
    Given a partial path, return an absolute path

    If the provided path has 'HBEngine' at the beginning, then the returned path will be relative
    to the engine, not the project. This is to allow references to engine default files that are not
    a part of Heartbeat projects
    """
    global root_dir
    global project_root
    #@TODO: Figure out how to solve this path reference with packaged builds
    # Context: If using the "main" script to launch the engine from the editor, then the root
    # will be "<root>/HBEngine", which means to access engine files, you'll need to append another
    # "HBEngine". This doesn't quite make sense, as this directory struture would likely change for builds
    # where we won't need the editor, so "main" would be non-existent. At that point, we'd likely start
    # in the deeper "HBEngine", which doesn't require that additional concatenation

    # Idea 1: We still use main, but we don't package the editor, and in main, we have a flag to skip
    # the editor (Likely ill-advised)
    #print(os.getcwd())

    # Idea 2: We modify this code for the build
    if partial_path.startswith("HBEngine"):
        return partial_path.replace("HBEngine", f"{root_dir}/HBEngine")
    else:
        return project_root + "/" + partial_path


def LoadCharacter(partial_file_path: str):
    """
    Given a file path to a character file within the project, load its data and store it within 'loaded_characters'.
    If the character has already been loaded, then skip loading. Return the loaded data, or the already loaded data
    """
    global loaded_characters

    if partial_file_path not in loaded_characters:
        file_path = ConvertPartialToAbsolutePath(partial_file_path)
        character_data = Reader.ReadAll(file_path)
        loaded_characters[partial_file_path] = character_data
        return character_data
    else:
        return loaded_characters[partial_file_path]


root_dir = os.getcwd().replace("\\", "/")
project_root = ""
project_settings = None

active_scene = None  # Managed by 'hb_engine.py'
loaded_characters = {}  # Cache loaded characters so we don't need to reload them multiple times

# When objects need to be aware of changes to settings (IE. "mute" checkbox renderable needs
# to change based on the mute setting), we need a way of tracking who needs to be informed. This dict
# represents that tracking, by using a structure like the following:
#
# {"<Category>": {"<setting>": {"<object_ref>": "<func>"}}}
#
# "Func" in this case is the function to invoke when the connected setting is changed
project_setting_listeners = {}

# Window
resolution = None
resolution_options = None
resolution_multiplier = 1
active_resolution = None
