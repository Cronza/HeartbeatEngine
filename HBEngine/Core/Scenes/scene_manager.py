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
from HBEngine.Core import settings
from HBEngine.Core.Scenes.scene_pointandclick import PointAndClickScene
from HBEngine.Core.Scenes.scene_dialogue import DialogueScene
from HBEngine.Core.DataTypes.file_types import FileType


class SceneManager:
    def __init__(self, window):

        # Objects
        self.window = window
        self.active_scene = None

        # Cached Values (Scene agnostic)
        self.resolution_multiplier = None  # Null by default to allow the starting scene to generate a starting value
        self.pause_menu_data = None  # Menu data is stored in the manager, but the menu is owned by a scene

        self.scene_types = {
            FileType.Scene_Dialogue: DialogueScene,
            FileType.Scene_Point_And_Click: PointAndClickScene
        }

        # Load the starting scene defined in the project settings
        print(settings.project_settings)
        if not settings.project_settings["Game"]["starting_scene"]:
            raise ValueError("No starting scene was provided in the project settings")
        self.LoadScene(settings.project_settings["Game"]["starting_scene"])

        # Read in the yaml data for the pause menu
        #@TODO: Re-enable after review
        #self.pause_menu_data = Reader.ReadAll(self.settings.project_root + "/" + self.settings.project_settings['Pause Menu']['data_file'])
        #self.pause_menu_data['action'] = "create_container"

    def LoadScene(self, scene_file):
        """ Given a path to a scene file, check it's type, and load the corresponding scene object """
        # We need to read the file to find it's type. This is denoted by the 'type' value somewhere near the top of the
        # file. We can't guarentee it's position since the metadata may grow one day, and the line number would shift.
        scene_type = None
        with open(settings.ConvertPartialToAbsolutePath(scene_file), "r") as f:
            for line in f:
                if line.startswith("type:"):
                    scene_type = FileType[line.replace("type: ", "").strip()]

        if scene_type is not None:
            if scene_type in self.scene_types:
                del self.active_scene
                self.active_scene = self.scene_types[scene_type](
                    scene_file,
                    self.window,
                    self
                )
            else:
                raise ValueError(f"Failed to Load Scene - Specified scene type does not exist: {scene_type}")
        else:
            raise ValueError(f"No scene type specified in file '{scene_file}'")

    def ResizeScene(self):
        """ Inform the scene object o resize to support a resolution change """
        self.active_scene.Resize()

    def ShowPauseMenu(self):
        pass
