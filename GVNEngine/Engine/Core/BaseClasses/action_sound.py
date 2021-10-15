from Engine.Core.BaseClasses.action import Action

class SoundAction(Action):
    # @TODO: Add Pause function
    def __init__(self, scene, action_data, a_manager):
        super().__init__(scene, action_data, a_manager)
        self.assigned_channel = None
