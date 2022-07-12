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
from HBEngine.Core.Rendering.renderable_group import RenderableGroup


class Renderer:
    """
    The HBRenderer acts as a utility wrapper for the pygame renderer, utilizing Heartbeat's
    'Renderable' classes and custom z_ordering
    """
    def __init__(self, window):
        self.window = window
        self.active_renderables = RenderableGroup()

    def Draw(self):
        # Sort the renderable elements by their z-order (Lowest to Highest)
        renderables = sorted(self.active_renderables.renderables.values(),
                             key=lambda renderable: renderable.z_order)

        # Draw any renderables using the screen space multiplier to fit the new resolution
        for renderable in renderables:
            if renderable.visible:
                self.window.blit(renderable.GetSurface(), (renderable.rect.x, renderable.rect.y))

            # Draw any child renderables after drawing the parent
            #if renderable.children:
            #    for child in renderable.children:
            #        if child.visible:
            #            self.window.blit(child.GetSurface(), (child.rect.x, child.rect.y))

