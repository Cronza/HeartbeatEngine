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
    global project_setting_listeners

    file_path = ConvertPartialToAbsolutePath(partial_file_path)
    project_settings = Reader.ReadAll(file_path)

    # Initialize the listener dict with keys for each available settings
    for cat, settings in project_settings.items():
        project_setting_listeners[cat] = {}
        for name, val in settings.items():
            project_setting_listeners[cat][name] = {}

    # Apply the effects of various project settings
    resolution = tuple(map(int, project_settings['Graphics']['resolution']['value'].split('x')))
    resolution_options = project_settings['Graphics']['resolution']['options']

def SaveProjectSettings(file_path: str = "Config/Game.yaml"):
    """ Saves the project settings to the provided file path. Defaults to 'Config/Game.yaml' if no path is provided """
    global project_settings

    file_path = ConvertPartialToAbsolutePath(file_path)
    Writer.WriteFile(project_settings, file_path)


def SetProjectSetting(category: str, setting: str, value: any):
    """ Sets the corresponding project settings, then save it to disk"""
    global project_settings
    global project_setting_listeners

    project_settings[category][setting]['value'] = value

    # Inform any applicable listeners
    for listener_name, connect_func in project_setting_listeners[category][setting].items():
        connect_func(value)

    # Save changes to ensure persistence for all changes
    SaveProjectSettings()


def GetProjectSetting(category: str, key: str):
    """ Returns the project setting value that matches the provided category and key """
    global project_settings

    try:
        return project_settings[category][key]['value']
    except KeyError:
        raise ValueError(f"Project Setting Not Found: '{category}', '{key}'")


def LoadVariables(partial_file_path: str = "Config/Variables.yaml"):
    """ Reads in the project values file path. Defaults to 'Config/Variables.yaml' if no path is provided """
    global variables

    file_path = ConvertPartialToAbsolutePath(partial_file_path)
    variables = Reader.ReadAll(file_path)


def SaveVariables(file_path: str = "Config/Variables.yaml"):
    """ Saves the project variables to the provided file path. Defaults to 'Config/Variables.yaml' if no path is provided """
    global project_settings

    file_path = ConvertPartialToAbsolutePath(file_path)
    Writer.WriteFile(project_settings, file_path)


def SetValue(value_name: str, value_data: str):
    """
    Set the corresponding project value

    Note: This change will not persist between runs of the game unless the user saves the game
    """
    global values
    global value_listeners

    values[value_name] = value_data

    # Inform any applicable listeners
    for listener_name, connect_func in value_listeners[value_name].items():
        connect_func(value_name)


def GetValue(value_name: str) -> str:
    """ Returns the user value that matches the provided name """
    global values

    try:
        return str(values[value_name])
    except KeyError:
        raise ValueError(f"Project Value Not Found: '{value_name}'")


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


# --- Core engine references managed by 'hb_engine.py' ---
modules = {}
clock = None
window = None
scene = None
input_owner = None
paused = False

root_dir = os.getcwd().replace("\\", "/")
project_root = ""
project_settings = {}
variables = {}

# Graphics
resolution = (1280, 720)
resolution_options = None
resolution_multiplier = 1

# When objects need to be aware of changes to settings (IE. "mute" checkbox renderable needs
# to change based on the mute setting), we need a way of tracking who needs to be informed. These dicts
# represents that tracking
project_setting_listeners = {}  # Structure: {"<category>": {"<setting>": {"<object_ref>": "<connect_func>"}}}
variable_listeners = {}  # Structure: {"<var_name">: {"<object_ref>": "<connect_func>"}}


