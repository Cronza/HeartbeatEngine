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
from HBEngine.Core.Scenes.scene_pointandclick import PointAndClickScene


class DialogueScene(PointAndClickScene):
    def __init__(self, scene_data_file, window):
        self.dialogue_index = 0
        self.dialogue_data = {}
        self.active_branch = "Main"
        self.character_data = {}

        # Update the generic data using the parent's init
        super().__init__(scene_data_file, window)

    def Update(self, events):
        super().Update(events)

        if not self.paused:
            for event in events:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        # Skip the running action if it's able to be skipped
                        if self.a_manager.active_actions:
                            for action in self.a_manager.active_actions:
                                if action.skippable:
                                    action.Skip()

                        # No actions active. Go to next
                        else:
                            self.LoadAction()

    def LoadAction(self):
        """
        Runs the next action specified in the dialogue file. Will recurse if the action has 'wait_for_input' set
        to False
        """
        if len(self.dialogue_data[self.active_branch]["entries"]) > self.dialogue_index:
            action_data = self.dialogue_data[self.active_branch]["entries"][self.dialogue_index]

            # The action_dict dict has one top level key which is the name of the action. We need to fetch it in order
            # to access the action data stored as the value
            name = next(iter(action_data))
            data = action_data[name]
            if "post_wait" in data:
                if "wait_for_input" in data["post_wait"]:
                    self.a_manager.PerformAction(data, name)
                    self.dialogue_index += 1
                elif "wait_until_complete" in data["post_wait"]:
                    self.a_manager.PerformAction(data, name, self.ActionComplete)
                elif "no_wait" in data["post_wait"]:
                    self.a_manager.PerformAction(data, name)
                    self.dialogue_index += 1
                    self.LoadAction()
            # Default to 'no_wait' when nothing is provided
            else:
                self.a_manager.PerformAction(data, name)
                self.dialogue_index += 1
                self.LoadAction()
        else:
            print('The end of available dialogue actions has been reached')

    def LoadSceneData(self):
        """ Load the full dialogue structure, and load the first action """
        if "dialogue" in self.scene_data:
            self.dialogue_data = self.scene_data['dialogue']

            # Dialogue Scenes can read speaker files in order to prepare a variety of values for the dialogue to reference
            #if 'characters' in self.scene_data:
                #self.LoadCharacters()

            # Load any applicable interfaces
            if self.scene_data["settings"]["interface"] and self.scene_data["settings"]["interface"] != "None":
                self.LoadInterface(self.scene_data["settings"]["interface"])

            self.LoadAction()
        else:
            raise ValueError("'dialogue' missing from the scene file")

    def SwitchDialogueBranch(self, branch):
        """ Given a branch name within the active dialogue file, switch to using it """
        self.active_branch = branch
        self.dialogue_index = 0
        self.LoadAction()

    #@TODO: Investigate how to pre-load character files using the new combined Dialogue / Dialogue Scene file format
    #def LoadCharacters(self):
    #    """ Reads in all character YAML files specified in the dialogue scene file, and stores them in the scene """
    #    #print(self.scene_data['speakers'])
    #    for char, data in self.scene_data['characters'].items():
    #        self.character_data[char] = Reader.ReadAll(data)

    def ActionComplete(self):
        """ Moves the dialogue counter forward one, and loads the next action """
        self.dialogue_index += 1
        self.LoadAction()


