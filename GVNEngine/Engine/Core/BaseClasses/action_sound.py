from Engine.Core.BaseClasses.action import Action

class SoundAction(Action):
    def __init__(self, scene, action_data, a_manager):
        super().__init__(scene, action_data, a_manager)
        self.assigned_channel = None