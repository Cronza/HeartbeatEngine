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
    def __init__(self, scene, renderable_data: dict, parent: Renderable = None):
        # Page renderables are independent of the persistent renderables, and can be created and removed at runtime. In
        # order to faciliate quick removal, keep a list of keys for page renderables as they're created
        self.page_renderables = []

        self.visible = False
        if "key" not in renderable_data: renderable_data["key"] = id(self)
        if "z_order" not in renderable_data: renderable_data["z_order"] = 10000
        super().__init__(scene, renderable_data, parent)

        if "Persistent" in renderable_data["pages"]:
            for item in renderable_data["pages"]["Persistent"]["items"]:
                self.children.append(
                    self.scene.a_manager.PerformAction(action_data=item, action_name=item['action'], no_draw=True)
                )
        else:
            raise ValueError("'Persistent' missing from the interface file - No items to display!")

    def LoadPage(self, page_name: str) -> bool:
        """
        Unload the prior page if applicable, and load the provided page. Only one page is supported at a time.
        Returns whether the load succeeded
        """
        if "pages" in self.renderable_data:
            if page_name in self.renderable_data["pages"]:
                if self.page_renderables:
                    self.RemovePage()

                # Create and record new page renderables
                for page_action in self.renderable_data["pages"][page_name]["items"]:
                    renderable = self.scene.a_manager.PerformAction(page_action, page_action["action"], no_draw=True)
                    self.children.append(renderable)
                    self.page_renderables.append(renderable)
                return True

        return False

    def RemovePage(self):
        """ Removes all active page renderables """
        # Wipe existing page renderables if there are any
        for renderable in self.page_renderables:
            self.children.remove(renderable)
        self.page_renderables.clear()

