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
from HBEngine.Core.BaseClasses.renderable_container import Container


class Choice(Container):
    def __init__(self, scene, renderable_data):
        super().__init__(scene, renderable_data)
        self.visible = False

        # Pass in a button list, and generate buttons
        assert 'choices' in self.renderable_data, print(
            f"No 'choices' block assigned to {self}. This makes for an impossible action!")
