from Engine.Core.BaseClasses.scene_pointandclick import PointAndClickScene


class DialogueScene(PointAndClickScene):
    def __init__(self, scene_data_file, window, pygame_lib, settings, scene_manager):
        self.dialogue_index = 0
        self.dialogue_data = ""
        self.active_branch = "Main"
        self.character_data = {}

        # Update the generic data using the parent's init
        super().__init__(scene_data_file, window, pygame_lib, settings, scene_manager)

    def Update(self, input_events):
        super().Update(input_events)

        for event in input_events:
            if event.type == self.pygame_lib.KEYUP:
                if event.key == self.pygame_lib.K_SPACE:
                    # Skip the running action if its able to be skipped
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
        if len(self.dialogue_data[self.active_branch]) > self.dialogue_index:
            action_data = self.dialogue_data[self.active_branch][self.dialogue_index]
            if "post_wait" in action_data:
                if "wait_for_input" in action_data["post_wait"]:
                    self.a_manager.PerformAction(action_data, action_data["action"])
                    self.dialogue_index += 1
                elif "wait_until_complete" in action_data["post_wait"]:
                    self.a_manager.PerformAction(action_data, action_data["action"], self.ActionComplete)
                elif "no_wait" in action_data["post_wait"]:
                    self.a_manager.PerformAction(action_data, action_data["action"])
                    self.dialogue_index += 1
                    self.LoadAction()
            # Default to 'no_wait' when nothing is provided
            else:
                self.a_manager.PerformAction(action_data, action_data["action"])
                self.dialogue_index += 1
                self.LoadAction()
        else:
            print('The end of available dialogue actions has been reached')

    def LoadSceneData(self):
        """ Load the full dialogue structure, and load the first action """
        super().LoadSceneData()
        self.dialogue_data = self.scene_data['dialogue']

        # Dialogue Scenes can read speaker files in order to prepare a variety of values for the dialogue to reference
        #if 'characters' in self.scene_data:
            #self.LoadCharacters()

        self.LoadAction()

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
        """ When an action specifies 'wait', use this function as the completion delegate """
        self.dialogue_index += 1
        self.LoadAction()


