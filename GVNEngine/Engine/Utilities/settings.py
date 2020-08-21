import configparser

class Settings:
    def __init__(self, yaml_parser):
        # Define defaults for Game settings
        self.title = "No Name"
        self.resolution = 0
        self.resolution_options = [(1280, 720)]
        self.main_resolution = (1280, 720)
        self.starting_scene = 'Test_Dialogue_Scene_01.yaml'

        self.dialogue_frame_sprite = ""
        self.dialogue_speaker_frame_sprite = ""
        self.text_speed = 5

    def EvaluateGameINI(self, ini_path):
        parser = configparser.ConfigParser()
        parser.read(ini_path)
        self.title = parser['Game']['Title']
        self.starting_scene = parser['Game']['starting_scene']

        # Index value for a given resolution
        self.resolution = int(parser['Window.Settings']['resolution'])

        # All supported resolutions
        resolutions = parser['Window.Settings']['resolution_options'].split(",")
        if resolutions:  # If any resolutions were provided, use them. Otherwise, use the default
            self.resolution_options.clear()
            for res in resolutions:
                self.resolution_options.append(tuple(map(int, res.split("x"))))

        # The main resolution to base scene positions
        self.main_resolution = self.resolution_options[
            int(parser['Window.Settings']['main_resolution'])
        ]

        # Load all settings related to the dialogue system
        self.dialogue_frame_sprite = parser['Dialogue.Settings']['dialogue_frame_sprite']
        self.dialogue_speaker_frame_sprite = parser['Dialogue.Settings']['dialogue_speaker_frame_sprite']
        self.text_speed = parser['Dialogue.Settings']['text_speed']
