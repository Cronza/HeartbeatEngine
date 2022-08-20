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
from Tools.HBYaml.hb_yaml import Reader

root_dir = os.getcwd().replace("\\", "/")

project_root = ""
project_settings = None

# Some params need to be accessed more immediately than through the settings dict. Declare them here
resolution = None
resolution_options = None
active_resolution = None


def SetProjectRoot(new_root):
    global root_dir
    global project_root

    # If a project was not provided, use the engine root (Necessary for builds where project
    # and engine are conjoined)
    if new_root:
        project_root = new_root
    else:
        project_root = root_dir


def Evaluate(data_path):
    """ Reads in the provided project settings file path """
    global project_settings
    global resolution
    global resolution_options
    global active_resolution

    project_settings = Reader.ReadAll(data_path)

    resolution = project_settings['Window']['resolution']
    resolution_options = project_settings['Window']['resolution_options']
    active_resolution = tuple(resolution_options[resolution])


def ConvertPartialToAbsolutePath(partial_path):
    """
    Given a partial path, return a absolute path

    If the provided path has 'ENGINE_FILES' at the beginning, then the returned path will be relative
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


def GetProjectGlobal(category, key):
    """ Returns the value from the global setting defined in 'Game.yaml' that matches the provided category and key """
    global project_settings
    return project_settings[category][key]
