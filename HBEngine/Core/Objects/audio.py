import pygame.mixer
from HBEngine.Core import settings


class Sound(pygame.mixer.Sound):
    """ A subclass for the pygame Sound object with extra functionality for muting and identification """
    def __init__(self, sound_data: dict):
        super().__init__(settings.ConvertPartialToAbsolutePath(sound_data["sound"]))

        self.sound_data = sound_data
        self.key = ""
        self.channel = None
        self.paused = False
        self.loop_count = 0
        if "loop" in self.sound_data:
            if self.sound_data["loop"]:
                self.loop_count = -1

        # For indentification in the audio stack, all sounds require a unique identifier
        if 'key' not in self.sound_data:
            raise ValueError(f"No key assigned to {self}. The 'key' property is mandatory for all renderables")
        else:
            self.key = self.sound_data["key"]

        # Preset the volume (Use the base implementation to avoid the mute lock in 'SetVolume')
        super().set_volume(self.sound_data["volume"])

        # Prepare muted state
        self.pre_mute_volume = 0
        if settings.GetProjectSetting("Audio", "mute"):
            self.Mute()

    def Mute(self):
        self.pre_mute_volume = self.get_volume()
        super().set_volume(0)  # (Use the base implementation to avoid the mute lock)

    def Unmute(self):
        super().set_volume(self.pre_mute_volume)
        self.pre_mute_volume = 0   # (Use the base implementation to avoid the mute lock)

    def Pause(self):
        self.channel.pause()
        self.paused = True

    def Unpause(self):
        self.channel.unpause()
        self.paused = False

    def GetBusy(self) -> bool:
        # We need to ensure that a paused sound is considered still busy in order to avoid it being discarded during
        # any cleanup checks
        if self.paused:
            return True

        try:
            return self.channel.get_busy()
        except AttributeError:  # Channel likely isn't set yet, and thus this sound hasn't started playing
            return False

    def set_volume(self, value: float) -> None:
        """
        Set the volume for this object. If the 'mute' project setting is True, the volume will remain muted but will
        set properly
        """
        # Always modify relative SFX volume by the global SFX volume
        value = value * settings.GetProjectSetting("Audio", "volume_sfx")
        if settings.GetProjectSetting("Audio", "mute"):
            self.pre_mute_volume = value
        else:
            super().set_volume(value)

    def Play(self):
        """ Play the loaded SFX file associated with this object, looping according to the loop policy """
        self.channel = self.play(self.loop_count)

    def Stop(self):
        """ Stop SFX playback and clear the assigned channel """
        self.paused = False
        self.channel = None
        self.stop()


class Music:
    """
    A wrapper for the pygame Music Mixer with extra functionality for muting

    Unlike SFX, pygame does not use an object for music, instead opting for streaming a single musical track using the
    pygame.mixer. Since this prevents subclassing, we need an entirely custom object that has hooks into the mixer
    """
    def __init__(self, sound_data: dict):
        self.sound_data = sound_data
        self.paused = False
        if "loop" in self.sound_data:
            if self.sound_data["loop"]:
                self.loop_count = -1

        # Preset the volume (Use the base implementation to avoid the mute lock in 'SetVolume')
        pygame.mixer.music.set_volume(self.sound_data["volume"])

        # Prepare muted state
        self.pre_mute_volume = 0
        if settings.GetProjectSetting("Audio", "mute"):
            self.Mute()

        # Load the track
        self.Load()

    def Mute(self):
        self.pre_mute_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(0)

    def Unmute(self):
        pygame.mixer.music.set_volume(self.pre_mute_volume)
        self.pre_mute_volume = 0

    def SetVolume(self, value: float) -> None:
        """
        Set the volume for this object. If the 'mute' project setting is True, the volume will remain muted but will
        set properly
        """
        # Always modify music volume by the global music volume
        value = value * settings.GetProjectSetting("Audio", "volume_music")
        if settings.GetProjectSetting("Audio", "mute"):
            self.pre_mute_volume = value
        else:
            pygame.mixer.music.set_volume(value)

    def Pause(self):
        pygame.mixer.music.pause()
        self.paused = True

    def Unpause(self):
        pygame.mixer.music.unpause()
        self.paused = False

    def GetBusy(self) -> bool:
        # We need to ensure that a paused track is considered still busy in order to avoid it being discarded during
        # any cleanup checks
        if self.paused:
            return True

        return pygame.mixer.music.get_busy()

    def Load(self):
        """ Load the music file associated with this object into the mixer """
        pygame.mixer.music.load(settings.ConvertPartialToAbsolutePath(self.sound_data["music"]))

    def Play(self):
        """ Play the loaded music file associated with this object, looping according to the loop policy """
        pygame.mixer.music.play(self.loop_count)

    def Stop(self):
        pygame.mixer.music.stop()

    def set_endevent(self):
        pass

    def get_endevent(self):
        pass
