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
class Action():
    def __init__(self, scene, action_data, a_manager):
        self.scene = scene
        self.action_data = action_data
        self.a_manager = a_manager
        self.active_transition = None
        self.speed = 5
        self.skippable = True
        self.complete = False
        self.complete_delegate = None  # Called by the action manager before it deletes the action

    def Start(self):
        pass

    def Update(self, events):
        pass

    def Skip(self):
        pass

    def Complete(self):
        self.complete = True

    #@TODO: Create 'ValidateParams' function to handle checking for parameters in action data, and using global default
    #@TODO: if none are provided
    def ValidateParams(self):
        pass