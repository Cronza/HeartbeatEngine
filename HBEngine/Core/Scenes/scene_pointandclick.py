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
from HBEngine.Core.Scenes.scene import Scene


class PointAndClickScene(Scene):
    def __init__(self, scene_data_file, window, scene_manager):
        super().__init__(scene_data_file, window, scene_manager)

    def LoadSceneData(self):
        if "scene_items" in self.scene_data:
            for item in self.scene_data["scene_items"]:
                self.a_manager.PerformAction(item, item['action'])
        else:
            raise ValueError("'scene_items' missing from the scene file")
