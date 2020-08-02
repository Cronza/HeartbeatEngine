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
                    self.LoadAction()

    def LoadAction(self):
        """
        Runs the next action specified in the dialogue file. Will recurse if the action has 'wait_for_input' set
        to False
        """
        if len(self.dialogue_data['dialogue']) > self.dialogue_index:
            recurse = False

            action_data = self.dialogue_data['dialogue'][self.dialogue_index]

            if 'wait_for_input' in action_data:
                if action_data['wait_for_input'] is False:
                    # Don't wait for input on this action. Run it, and move to the next
                    recurse = True

            self.a_manager.PerformAction(action_data)
            self.dialogue_index += 1

            if recurse:
                self.LoadAction()
            else:
                # If we're changing the scene, forgo the draw update as data will no longer be available
                if action_data['action'] != "load_scene":
                    self.Draw(
                        self.settings.main_resolution,
                        self.settings.resolution_options[self.settings.resolution]
                    )

        else:
            print('The end of available dialogue actions has been reached')

    def LoadSceneData(self):
        super().LoadSceneData()
        self.dialogue_data = Reader.ReadAll(self.scene_data['dialogue'])
        self.LoadAction()


