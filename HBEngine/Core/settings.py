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
from HBEngine.Utilities.yaml_reader import Reader


class Settings:
    def __init__(self, project_dir):
        self.root_dir = os.getcwd().replace("\\", "/")

        # If a project was not provided, use the engine root (Necessary for builds where project
        # and engine are conjoined)
        if project_dir:
            self.project_dir = project_dir
        else:
            self.project_dir = self.root_dir

        self.project_settings = None

        # Some params need to be accessed more immediately than through the settings dict. Declare them here
        self.resolution = None
        self.resolution_options = None
        self.active_resolution = None

    def Evaluate(self, data_path):
        """ Reads in the provided project settings file path """
        self.project_settings = Reader.ReadAll(data_path)

        self.resolution = self.project_settings['Window']['resolution']
        self.resolution_options = self.project_settings['Window']['resolution_options']
        self.active_resolution = tuple(self.resolution_options[self.resolution])

    def ConvertPartialToAbsolutePath(self, partial_path):
        """
        Given a partial path, return a absolute path

        If the provided path has 'ENGINE_FILES' at the beginning, then the returned path will be relative
        to the engine, not the project. This is to allow references to engine default files that are not
        a part of Heartbeat projects
        """
        #@TODO: Figure out how to solve this path reference with packaged builds
        # Context: If using the "main" script to launch the engine from the editor, then the root
        # will be "<root>/HBEngine", which means to access engine files, you'll need to append another
        # "HBEngine". This doesn't quite make sense, as this directory struture would likely change for builds
        # where we won't need the editor, so "main" would be non-existent. At that point, we'd likely start
        # in the deeper "HBEngine", which doesn't require that additional concatenation

        # Idea 1: We still use main, but we don't package the editor, and in main, we have a flag to skip
        # the editor (Likely ill-advised)
        print(os.getcwd())
        # Idea 2: We modify this code for the build
        if partial_path.startswith("HBEngine"):
            return partial_path.replace("HBEngine", f"{self.root_dir}/HBEngine")
        else:
            return self.project_dir + "/" + partial_path

