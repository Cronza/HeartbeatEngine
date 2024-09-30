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
from HBEngine.Core import settings, action_manager
from Tools.HBYaml.hb_yaml import Reader
from HBEngine.Core.Modules.base import BaseModule
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.interface import Interface


class Dialogue(BaseModule):
    MODULE_NAME = "Dialogue"
    RESERVE_THREAD = True  # Disable updates for everything but this module (IE. Scene, other modules)
    CLOSE_ON_SCENE_CHANGE = True  # Prevent this module from persisting between scenes

    def __init__(self, file_path: str):
        super().__init__(file_path)

        self.dialogue_index = 0
        self.dialogue_data = {}
        self.active_branch = "Main"

        # Keep track of all spawned renderables by adding them as children to a root object. When removing this module,
        # instead of tracking each instance down, we can just delete the root and all children will go with it
        self.root_renderable = Renderable({'key': '!&MODULE_DIALOGUE_ROOT&!', 'z_order': 99999})
        self.root_renderable.visible = False
        settings.scene.active_renderables.Add(self.root_renderable)

        # Read in the dialogue file data
        self.dialogue_data = Reader.ReadAll(settings.ConvertPartialToAbsolutePath(file_path))

    def Start(self):
        if self.dialogue_data['settings']['interface']:
            self.LoadInterface(self.dialogue_data['settings']['interface'])
        self.LoadAction()

    def Update(self, events):
        for event in events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    # Skip the running action if it's able to be skipped
                    if action_manager.active_actions:
                        for action in action_manager.active_actions:
                            if action.skippable:
                                action.Skip()

                    # No actions active. Go to next
                    else:
                        self.LoadAction()

        super().Update(events)

    def LoadAction(self):
        """
        Runs the next action specified in the dialogue file. Will recurse if the action has 'wait_for_input' set
        to False
        """
        if len(self.dialogue_data['dialogue'][self.active_branch]["entries"]) > self.dialogue_index:
            action_data = self.dialogue_data['dialogue'][self.active_branch]["entries"][self.dialogue_index]

            # The action_dict dict has one top level key which is the name of the action. We need to fetch it in order
            # to access the action data stored as the value
            name = next(iter(action_data))
            data = action_data[name]
            if "post_wait" in data:
                if "wait_for_input" in data["post_wait"]:
                    action_manager.PerformAction(action_data=data, action_name=name, parent=self.root_renderable)
                    self.dialogue_index += 1
                elif "wait_until_complete" in data["post_wait"]:
                    action_manager.PerformAction(action_data=data, action_name=name, parent=self.root_renderable, completion_callback=self.ActionComplete)
                elif "no_wait" in data["post_wait"]:
                    action_manager.PerformAction(action_data=data, action_name=name, parent=self.root_renderable)
                    self.dialogue_index += 1
                    self.LoadAction()
            # Default to 'no_wait' when nothing is provided
            else:
                action_manager.PerformAction(action_data=data, action_name=name, parent=self.root_renderable)
                self.dialogue_index += 1
                self.LoadAction()
        else:
            #print("End of Dialogue Sequence - The game will not proceed past this point.")
            from HBEngine import hb_engine
            hb_engine.UnloadModule(self.MODULE_NAME)

    def SwitchDialogueBranch(self, branch):
        """ Given a branch name within the active dialogue file, switch to using it """
        self.active_branch = branch
        self.dialogue_index = 0
        self.LoadAction()

    def ActionComplete(self):
        """ Moves the dialogue counter forward one, and loads the next action """
        self.dialogue_index += 1
        self.LoadAction()


