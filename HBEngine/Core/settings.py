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
import os, pathlib
from Tools.HBYaml.hb_yaml import Reader, Writer
from Tools.HBYaml.CustomTags.connection import Connection


def SetProjectRoot(new_root: str):
    global root_dir
    global saves_dir
    global project_root

    if new_root:
        project_root = new_root
    else:
        packaged_root = os.path.join(root_dir, "_internal")
        if os.path.exists(packaged_root):
            print(f"Packaged path found - Setting root to '{packaged_root}'")
            project_root = packaged_root
            saves_dir = os.path.join(project_root, "saves")
        else:
            raise ValueError("No project root provided, and this does not seem to be a packaged build")


def LoadProjectSettings(partial_file_path: str = "Config/Game.yaml"):
    """ Reads in the provided project settings file path. Defaults to 'Config/Game.yaml' if no path is provided """
    global project_settings
    global resolution
    global resolution_options
    global connection_listeners

    # Load project settings
    file_path = ConvertPartialToAbsolutePath(partial_file_path)
    project_settings = Reader.ReadAll(file_path)

    # Initialize the 'Setting' side of the listener dict with keys for each available settings
    for cat, settings in project_settings.items():
        connection_listeners["Settings"][cat] = {}
        for name, val in settings.items():
            connection_listeners["Settings"][cat][name] = {}

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
    global connection_listeners

    project_settings[category][setting]['value'] = value

    # Inform any applicable listeners
    for listener, notify_func in connection_listeners["Settings"][category][setting].items():
        notify_func(value)

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
    global connection_listeners

    # Load user variables
    file_path = ConvertPartialToAbsolutePath(partial_file_path)
    variables = Reader.ReadAll(file_path)

    # Initialize the 'Variable' side of the listener dict with keys for each available variables
    for cat, variable in variables.items():
        connection_listeners["Variables"][cat] = {}
        for name, val in variable.items():
            connection_listeners["Variables"][cat][name] = {}


def SaveVariables(file_path: str = "Config/Variables.yaml"):
    """ Saves the project variables to the provided file path. Defaults to 'Config/Variables.yaml' if no path is provided """
    global variables

    file_path = ConvertPartialToAbsolutePath(file_path)
    Writer.WriteFile(variables, file_path)


def SetVariable(category: str, variable: str, value: str):
    """
    Set the corresponding project variable

    Note: This change will not persist between runs of the game unless the user saves the game
    """
    global variables
    global connection_listeners

    variables[category][variable]['value'] = value

    # Inform any applicable listeners
    for listener, notify_func in connection_listeners["Variables"][category][variable].items():
        notify_func(value)


def GetVariable(category_name: str, variable_name: str) -> any:
    """ Returns the project variable that matches the provided name """
    global variables

    try:
        return variables[category_name][variable_name]['value']
    except KeyError:
        raise ValueError(f"Project Variable Not Found: '{category_name}' | '{variable_name}'")


def ConvertPartialToAbsolutePath(partial_path):
    """
    Given a partial path, return an absolute path

    The returned path is within the project root if this is ran through the editor, or packaged build if this is ran
    from a compiled .exe.

    If the provided path has 'HBEngine' at the beginning, then the returned path will be relative
    to the engine, not the project.
    """
    global root_dir
    global project_root
    if partial_path.startswith("HBEngine"):
        return partial_path.replace("HBEngine", f"{root_dir}/HBEngine")
    else:
        return project_root + "/" + partial_path


def GetConnectionData(connection_obj: Connection) -> any:
    """ Returns the value from the target of the given connection object """
    if connection_obj.source == "Variables":
        return GetVariable(connection_obj.category, connection_obj.variable)
    else:
        return GetProjectSetting(connection_obj.category, connection_obj.variable)


def RegisterConnectionListener(connection_obj: Connection, registeree: object, notify_func: callable) -> bool:
    """
    Registers a connection listener for the given connection data. When the target var or setting is changed,
    invoke "notify_func". Registree is used to identify 'who' the connection is for.

    Returns whether the registration was successfully made
    """
    global connection_listeners

    if connection_obj.category == "" or connection_obj.variable == "" or connection_obj.source == "":
        print(f"Unable to Register Connection for '{registeree}'. Please review the connection settings")
        return False

    # Add the object as a listener (This stomps any previous connection)
    connection_listeners[connection_obj.category][connection_obj.variable][registeree] = notify_func


def DeregisterConnectionListener(connection_obj: Connection, registeree: object):
    """ Removes a registered connection listener based on the given connection data """
    global connection_listeners

    # Remove the registration if it exists
    if registeree in connection_listeners[connection_obj.category][connection_obj.variable]:
        del connection_listeners[connection_obj.category][connection_obj.variable][registeree]


# --- Core engine references managed by 'hb_engine.py' ---
modules = {}
clock = None
window = None
scene = None
thread_reservations = []  # Descending list of objects that are reserving control of the main thread
paused = False

root_dir = os.getcwd().replace("\\", "/")  # Either the engine root, or the packaged root
project_root = ""
project_settings = {}
variables = {}
saves_dir = ""  # Set by 'SetProjectRoot'

# Graphics
resolution = (1280, 720)
resolution_options = None
resolution_multiplier = 1

# When objects need to be aware of changes to variables or settings (IE. "mute" checkbox renderable needs
# to change based on the mute setting), we need a way of tracking who needs to be informed. Any class may add
# themselves as listeners
#
# Structure of dict: {"<category>": {"<var_or_setting_name>": {}}}}
# Expected way of adding new entries: connection_listeners['registree_object'] = 'notify_func'
connection_listeners = {
    "Variables" : {},
    "Settings" : {}
}



