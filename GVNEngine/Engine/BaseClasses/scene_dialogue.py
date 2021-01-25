from Engine.BaseClasses.scene_pointandclick import PointAndClickScene
from Engine.Utilities.yaml_reader import Reader

class DialogueScene(PointAndClickScene):
    def __init__(self, scene_data_file, window, pygame_lib, settings, scene_manager):
        self.dialogue_index = 0
        self.dialogue_data = ""

        #Update the generic data using the parent's init
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
        if len(self.dialogue_data['dialogue']) > self.dialogue_index:
            action_data = self.dialogue_data['dialogue'][self.dialogue_index]

            #@TODO: Review how the wait mechanism works, and how its communicate to the user

            # Should we automatically load the next action, or wait until the next input?
            if 'wait_for_input' in action_data:
                if action_data['wait_for_input'] is True:
                    self.a_manager.PerformAction(action_data)
                    self.dialogue_index += 1
                else:
                    # Don't wait for input on this action. Run it, and move to the next
                    self.a_manager.PerformAction(action_data)
                    self.dialogue_index += 1
                    self.LoadAction()
            # Should we let the action load the next action when it's complete?
            elif 'wait_until_complete' in action_data:
                if action_data['wait_until_complete'] is True:
                    self.a_manager.PerformAction(action_data, self.ActionComplete)
                else:
                    self.a_manager.PerformAction(action_data)
                    self.dialogue_index += 1
            else:
                self.a_manager.PerformAction(action_data)
                self.dialogue_index += 1
        else:
            print('The end of available dialogue actions has been reached')

    def LoadSceneData(self):
        """ Load the full dialogue structure, and load the first action """
        super().LoadSceneData()
        self.dialogue_data = Reader.ReadAll(self.scene_data['dialogue'])
        self.LoadAction()


    def ActionComplete(self):
        """ When an action specifies 'wait', use this function as the completion delegate """
        #self.Draw()
        self.dialogue_index += 1
        self.LoadAction()


