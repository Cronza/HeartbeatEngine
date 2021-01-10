from Engine.BaseClasses.scene_pointandclick import PointAndClickScene
from Engine.Utilities.yaml_reader import Reader

class DialogueScene(PointAndClickScene):
    def __init__(self, scene_data_file, window, pygame_lib, settings, scene_manager):
        self.dialogue_index = 0
        self.dialogue_data = ""
        self.waiting_for_action = False

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
        #print(self.dialogue_index)
        if len(self.dialogue_data['dialogue']) > self.dialogue_index:
            action_data = self.dialogue_data['dialogue'][self.dialogue_index]
            #if 'wait_for_input' in action_data and 'wait' in action_data:
            #    print("Please only specify one wait value per yaml block (IE. 'wait' or 'wait_for_input')")

            if 'wait' in action_data:
                if action_data['wait'] is True:
                    self.waiting_for_action = True
                    self.a_manager.PerformAction(action_data, self.ActionComplete)
            elif 'wait_for_input' in action_data:
                if action_data['wait_for_input'] is False:
                    # Don't wait for input on this action. Run it, and move to the next
                    self.a_manager.PerformAction(action_data)
                    self.dialogue_index += 1
                    self.LoadAction()
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
        self.dialogue_index += 1
        self.LoadAction()


