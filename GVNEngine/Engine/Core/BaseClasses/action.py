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

    def Update(self):
        pass

    def Skip(self):
        pass

    def Complete(self):
        self.complete = True

    #@TODO: Create 'ValidateParams' function to handle checking for parameters in action data, and using global default
    #@TODO: if none are provided
    def ValidateParams(self):
        pass