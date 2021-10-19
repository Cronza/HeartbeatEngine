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
class Transition:
    def __init__(self, scene, a_manager, renderable, speed=5):
        self.scene = scene
        self.a_manager = a_manager
        self.renderable = renderable
        self.speed = speed

        self.complete = False

    def Start(self):
        pass

    def Update(self):
        pass

    def Skip(self):
        pass