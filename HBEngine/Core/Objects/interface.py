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
import pygame
from HBEngine.Core import settings
from HBEngine.Core.Objects.renderable import Renderable
from Tools.HBYaml.hb_yaml import Reader


class Interface(Renderable):
    def __init__(self, scene, interface_data: dict, parent: Renderable = None):
        self.visible = False
        if "key" not in interface_data: interface_data["key"] = id(self)
        if "z_order" not in interface_data: interface_data["z_order"] = 10000
        super().__init__(scene, interface_data, parent)

        if "renderables" in interface_data:
            for item in interface_data["renderables"]:
                self.children.append(
                    self.scene.a_manager.PerformAction(action_data=item, action_name=item['action'], no_draw=True)
                )
        else:
            raise ValueError("'renderables' missing from the interface file - No items to display!")
