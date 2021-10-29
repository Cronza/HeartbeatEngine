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
"""

This file lists available actions that can be defined in various .yaml files throughout the HBEngine project.
All actions take in two parameters:

    - scene - Simply a reference to the scene object. This is handled by the engine
    - action_data - This is a dictionary that is created by reading in a section of .yaml. A .yaml example looks like:
        - action: "create_sprite"
          key: "Speaker_01"
          sprite: "Content/Sprites/Characters/Mary/Mary_Happy.png"
          position:
            x: 0.2
            y: 1.4

All actions can be designed to accept and use a variety of different parameters. To learn more, review some of the
provided actions
"""
import pygame.mixer
from HBEngine.Core.BaseClasses.renderable_sprite import SpriteRenderable
from HBEngine.Core.BaseClasses.renderable_text import TextRenderable
from HBEngine.Core.BaseClasses.interactable import Interactable
from HBEngine.Core.BaseClasses.button import Button
from HBEngine.Core.BaseClasses.choice import Choice
from HBEngine.Core.BaseClasses.renderable_container import Container
from HBEngine.Core.BaseClasses.action import Action
from HBEngine.Core.BaseClasses.action_sound import SoundAction


# -------------- GRAPHICS ACTIONS --------------

class remove_renderable(Action):
    """
    Based on a given key, remove the associated renderable from the renderable stack
    Possible Parameters:
    - key : str
    - transition : dict
        - type: str
        - speed: int
    """
    def Start(self):
        if "key" in self.action_data:
            renderable = self.scene.active_renderables.renderables[self.action_data['key']]

            # Any transitions are applied to the sprite pre-unload
            if "None" not in self.action_data["transition"]["type"]:
                self.active_transition = self.a_manager.CreateTransition(self.action_data["transition"], renderable)
                self.active_transition.Start()
            else:
                self.scene.active_renderables.Remove(self.action_data["key"])
                self.scene.Draw()
                self.Complete()
        else:
            raise ValueError("'remove_renderable' action Failed - Key not specified")

    def Update(self, events):
        if self.active_transition.complete is True:
            self.scene.active_renderables.Remove(self.action_data["key"])
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()

class remove_container(Action):
    """
        Based on a given key, remove the associated container and all of it's children from the renderable stack
        Possible Parameters:
        - key : str
        - transition : dict
            - type: str
            - speed: int
    """
    def Start(self):
        if "key" in self.action_data:
            container = self.scene.active_renderables.renderables[self.action_data["key"]]

            # Collect a flattened list of all children in this container
            children = container.GetAllChildren()

            if "None" not in self.action_data["transition"]["type"]:
                # In order to apply the transition to each and every child of the container, we merge the surfaces
                # and combine them into the container surface. That way, the rendering only manages a single
                # surface. This causes containers to be non-functional once a transition starts, as the underlying
                # children are destroyed before the transition begins

                # Merge the surfaces, then delete the child (Grim, I know)
                for child in list(children):
                    container.surface.blit(child.GetSurface(), (child.rect.x, child.rect.y))
                    self.scene.active_renderables.Remove(child.key)

                container.visible = True
                self.active_transition = self.a_manager.CreateTransition(self.action_data["transition"], container)
                self.active_transition.Start()
            else:
                # Remove all children first
                for child in children:
                    self.scene.active_renderables.Remove(child.key)
                self.scene.active_renderables.Remove(self.action_data['key'])
                self.scene.Draw()
                self.Complete()
        else:
            raise ValueError("'remove_renderable' action Failed - Key not specified")

    def Update(self, events):
        if self.active_transition.complete is True:
            self.scene.active_renderables.Remove(self.action_data['key'])
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()

class create_dialogue_interface(Action):
    """
    Creates sprite renderables for the dialogue and speaker text, and assigns them to the renderable stack using
    pre-configured settings
    Possible Parameters:
        - sprite: str <GLOBAL_AVAILABLE>
        - position: tuple <GLOBAL_AVAILABLE>
        - z_order: int <GLOBAL_AVAILABLE>
        - center_align: bool <GLOBAL_AVAILABLE>
    """
    def Start(self):
        self.skippable = False

        # Action-specific adjustments
        self.action_data["key"] = "DialogueFrame"

        # PROJECT DEFAULTS OVERRIDE
        if "sprite" not in self.action_data:
            self.action_data['sprite'] = self.scene.settings.project_settings['Dialogue'][
                'dialogue_frame_sprite']

        if "position" not in self.action_data:
            self.action_data['position'] = self.scene.settings.project_settings['Dialogue'][
                'dialogue_frame_position']

        if "z_order" not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.project_settings['Dialogue'][
                'dialogue_frame_z_order']

        if "center_align" not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.project_settings['Dialogue'][
                'dialogue_frame_center_align']

        dialogue_frame = SpriteRenderable(
            self.scene,
            self.action_data
        )

        # Add the dialogue interface to the sprite group so they exist until explicitly unloaded
        self.scene.active_renderables.Add(dialogue_frame)

        self.scene.Draw()
        self.Complete()

class create_background(Action):
    """
    Creates a pre-configured 'SpriteRenderable' suitable as a background image. Returns a
    'SpriteRenderable'

    Possible Parameters:
    - sprite : str
    - flip : bool
    - z_order : int <GLOBAL_AVAILABLE>
    """
    def Start(self):
        self.skippable = False

        # Background-specific adjustments
        self.action_data["position"] = (0,0)
        self.action_data["key"] = "Background"
        self.action_data["center_align"] = False

        # PROJECT DEFAULTS OVERRIDE
        if "z_order" not in self.action_data:
            self.action_data["z_order"] = self.scene.settings.project_settings["Sprite"]["background_z_order"]

        new_sprite = SpriteRenderable(
            self.scene,
            self.action_data,
        )

        self.scene.active_renderables.Add(new_sprite)

        self.scene.Draw()
        self.Complete()

        return new_sprite

class create_sprite(Action):
    """
    Create a sprite renderable using passed in settings. Returns a 'SpriteRenderable'

    Possible Parameters:
    - key : str
    - sprite : str
    - position : tuple
    - center_align : bool <GLOBAL_AVAILABLE>
    - flip : bool
    - z_order : int <GLOBAL_AVAILABLE>
    - transition : dict
        - type: str
        - speed: int
    """
    def Start(self):

        # OVERRIDES WITH NO PROJECT DEFAULTS
        if "position" not in self.action_data:
            self.action_data["position"] = (0, 0)

        # PROJECT DEFAULTS OVERRIDE
        if "z_order" not in self.action_data:
            self.action_data["z_order"] = self.scene.settings.project_settings["Sprite"][
                "z_order"]

        if "center_align" not in self.action_data:
            self.action_data["center_align"] = self.scene.settings.project_settings["Sprite"][
                "center_align"]

        new_sprite = SpriteRenderable(
            self.scene,
            self.action_data
        )

        # If the user requested a flip action, do so
        if "flip" in self.action_data:
            if self.action_data["flip"]:
                new_sprite.Flip()

        self.scene.active_renderables.Add(new_sprite)

        # Any transitions are applied to the sprite post-load
        if "None" not in self.action_data["transition"]["type"]:
            self.active_transition = self.a_manager.CreateTransition(self.action_data["transition"], new_sprite)
            self.active_transition.Start()
        else:
            self.scene.Draw()
            self.Complete()

        return new_sprite

    def Update(self, events):
        if self.active_transition.complete:
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()

class create_interactable(Action):  # AWAITING EDITOR IMPLEMENTATION - WILL BE UPDATED
    """ Creates an interactable renderable, and adds it to the renderable stack. Returns an 'Interactable'"""
    def Start(self):
        self.skippable = False

        # OVERRIDES WITH NO PROJECT DEFAULTS
        if 'position' not in self.action_data:
            self.action_data['position'] = (0, 0)

        # PROJECT DEFAULTS OVERRIDE
        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.project_settings['Interactable'][
                'z_order']

        if 'center_align' not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.project_settings['Interactable'][
                'center_align']

        new_renderable = Interactable(
            self.scene,
            self.action_data,
        )

        # If the user requested a flip action, do so
        if 'flip' in self.action_data:
            if self.action_data['flip']:
                new_renderable.Flip()

        self.scene.active_renderables.Add(new_renderable)

        self.scene.Draw()
        self.Complete()

        return new_renderable

class create_text(Action):
    """
    Create a TextRenderable at the target location, with the given settings. Returns a 'TextRenderable'

    Possible Parameters:
    - key : str
    - position : tuple
    - center_align : bool <GLOBAL_AVAILABLE>
    - text : str
    - text_size : str <GLOBAL_AVAILABLE>
    - text_color : str <GLOBAL_AVAILABLE>
    - font : str <GLOBAL_AVAILABLE>
    - z_order : int <GLOBAL_AVAILABLE>
    - transition : dict
        - type: str
        - speed: int
    """

    def Start(self):

        # OVERRIDES WITH NO PROJECT DEFAULTS
        if "position" not in self.action_data:
            self.action_data["position"] = (0,0)

        # PROJECT DEFAULTS OVERRIDE
        if "z_order" not in self.action_data:
            self.action_data["z_order"] = self.scene.settings.project_settings["Text"]['z_order']

        if "center_align" not in self.action_data:
            self.action_data["center_align"] = self.scene.settings.project_settings["Text"]["center_align"]

        if "font" not in self.action_data:
            self.action_data["font"] = self.scene.settings.project_settings["Text"]["font"]

        if "text_size" not in self.action_data:
            self.action_data["text_size"] = self.scene.settings.project_settings["Text"]["size"]

        if "text_color" not in self.action_data:
            self.action_data["text_color"] = self.scene.settings.project_settings["Text"]["color"]

        new_text_renderable = TextRenderable(
            self.scene,
            self.action_data
        )

        # Add the text to the renderables list instead of the sprite group as text is a temporary element that is
        # not meant to be kept around long-term
        self.scene.active_renderables.Add(new_text_renderable)

        if "None" not in self.action_data["transition"]["type"]:
            self.active_transition = self.a_manager.CreateTransition(self.action_data["transition"], new_text_renderable)
            self.active_transition.Start()
        else:
            self.scene.Draw()
            self.Complete()

        return new_text_renderable

    def Update(self, events):
        if self.active_transition.complete is True:
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()

class create_button(Action):  # AWAITING EDITOR IMPLEMENTATION - WILL BE UPDATED
    """ Creates a button interactable, and adds it to the renderable stack. Returns a 'Button' """
    def Start(self):
        self.skippable = False

        # OVERRIDES WITH NO PROJECT DEFAULTS
        if 'position' not in self.action_data:
            self.action_data['position'] = (0, 0)

        if 'text_position' not in self.action_data:
            self.action_data['text_position'] = self.action_data['position']

        # PROJECT DEFAULTS OVERRIDE
        if 'sprite' not in self.action_data:
            self.action_data['sprite'] = self.scene.settings.project_settings['Button']['sprite']

        if 'sprite_hover' not in self.action_data:
            self.action_data['sprite_hover'] = self.scene.settings.project_settings['Button']['sprite_hover']

        if 'sprite_clicked' not in self.action_data:
            self.action_data['sprite_clicked'] = self.scene.settings.project_settings['Button']['sprite_clicked']

        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.project_settings['Button']['button_z_order']

        if 'center_align' not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.project_settings['Button']['button_center_align']

        if 'text_z_order' not in self.action_data:
            self.action_data['text_z_order'] = self.scene.settings.project_settings['Button']['text_z_order']

        if 'text_center_align' not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.project_settings['Button']['text_center_align']

        if 'font' not in self.action_data:
            self.action_data['font'] = self.scene.settings.project_settings['Button']['font']

        if 'text_size' not in self.action_data:
            self.action_data['text_size'] = self.scene.settings.project_settings['Button']['text_size']

        if 'text_color' not in self.action_data:
            self.action_data['text_color'] = self.scene.settings.project_settings['Button']['text_color']

        new_renderable = Button(
            self.scene,
            self.action_data
        )

        # If the user requested a flip action, do so
        if 'flip' in self.action_data:
            if self.action_data['flip']:
                new_renderable.Flip()

        self.scene.active_renderables.Add(new_renderable)

        self.scene.Draw()
        self.Complete()

        return new_renderable

class create_container(Action): # AWAITING EDITOR IMPLEMENTATION - WILL BE UPDATED
    """ Creates a simple container renderable with the provided action data. Returns a 'Container' """

    # @TODO: Update to new workflow
    def Start(self):
        self.skippable = False

        # Container-specific adjustments
        self.action_data['position'] = (0, 0)
        self.action_data['z_order'] = 0
        self.action_data['center_align'] = False

        # Containers aren't rendered, so use defaults
        new_renderable = Container(
            self.scene,
            self.action_data,
        )

        self.scene.active_renderables.Add(new_renderable)

        self.scene.Draw()
        self.Complete()

        return new_renderable

# -------------- DIALOGUE ACTIONS --------------

class dialogue(Action):
    """
    Create dialogue and speaker text renderables, and add them to the renderable stack using pre-configured settings.
    If the user specifies a 'character' block, create a speaker text using the character details instead
    Returns None

    Possible Parameters:
    - position : tuple
    - center_align : bool
    - text : str
    - text_size : str
    - text_color : str
    - font : str
    - z_order : int
    - transition : dict
        - type: str
        - speed: int
    """

    def Start(self):
        # If the user has specified a 'speaker' block, build the speaker renderable details using any provided
        # information, and / or any global settings
        if "speaker" in self.action_data:
            # Dialogue-specific adjustments
            self.action_data["speaker"]['key'] = "SpeakerText"

            # PROJECT DEFAULTS OVERRIDE
            if "position" not in self.action_data["speaker"]:
                self.action_data["speaker"]["position"] = self.scene.settings.project_settings["Dialogue"][
                    "speaker_text_position"]

            if "center_align" not in self.action_data["speaker"]:
                self.action_data["speaker"]["center_align"] = self.scene.settings.project_settings["Dialogue"][
                    "speaker_center_align"]

            if "text_size" not in self.action_data["speaker"]:
                self.action_data["speaker"]["text_size"] = self.scene.settings.project_settings["Dialogue"][
                    "speaker_text_size"]

            if "text_color" not in self.action_data["speaker"]:
                self.action_data["speaker"]["text_color"] = self.scene.settings.project_settings["Dialogue"][
                    "speaker_text_color"]

            if "font" not in self.action_data["speaker"]:
                self.action_data["speaker"]["font"] = self.scene.settings.project_settings["Dialogue"][
                    "speaker_font"]

            if "z_order" not in self.action_data["speaker"]:
                self.action_data["speaker"]["z_order"] = self.scene.settings.project_settings["Dialogue"][
                    "speaker_z_order"]

            new_speaker_text = TextRenderable(
                self.scene,
                self.action_data["speaker"]
            )
            # Speaker text does not support transitions currently
            self.scene.active_renderables.Add(new_speaker_text)

        # If the user has specified a 'dialogue' block, build the speaker renderable
        if "dialogue" in self.action_data:
            # Dialogue-specific adjustments
            self.action_data["dialogue"]["key"] = "DialogueText"

            # PROJECT DEFAULTS OVERRIDE
            if "position" not in self.action_data["dialogue"]:
                self.action_data["dialogue"]["position"] = self.scene.settings.project_settings["Dialogue"][
                    "dialogue_text_position"]

            if "center_align" not in self.action_data["dialogue"]:
                self.action_data["dialogue"]["center_align"] = self.scene.settings.project_settings["Dialogue"][
                    "dialogue_center_align"]

            if "text_size" not in self.action_data["dialogue"]:
                self.action_data["dialogue"]["text_size"] = self.scene.settings.project_settings["Dialogue"][
                    "dialogue_text_size"]

            if "text_color" not in self.action_data["dialogue"]:
                self.action_data["dialogue"]["text_color"] = self.scene.settings.project_settings["Dialogue"][
                    "dialogue_text_color"]

            if "font" not in self.action_data["dialogue"]:
                self.action_data["dialogue"]["font"] = self.scene.settings.project_settings["Dialogue"][
                    "dialogue_font"]

            if "z_order" not in self.action_data["dialogue"]:
                self.action_data["dialogue"]["z_order"] = self.scene.settings.project_settings["Dialogue"][
                    "dialogue_z_order"]

            new_dialogue_text = TextRenderable(
                self.scene,
                self.action_data["dialogue"]
            )

            self.scene.active_renderables.Add(new_dialogue_text)

            # By default, dialogue text fades in. However, allow the user to override this behaviour
            if "None" not in self.action_data["dialogue"]["transition"]["type"]:
                self.active_transition = self.a_manager.CreateTransition(self.action_data["dialogue"]["transition"],
                                                                         new_dialogue_text)
                self.active_transition.Start()
            else:
                self.action_data["dialogue"]["transition"] = {
                    "type": "fade_in",
                    "speed": 1000
                }
                self.active_transition = self.a_manager.CreateTransition(self.action_data["dialogue"]["transition"],
                                                                         new_dialogue_text)
                self.active_transition.Start()

        return None

    def Update(self, events):
        if self.active_transition.complete is True:
            print("Transition Complete")
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()

class character_dialogue(Action):
    """
    A specialized variant of the 'dialogue' class that uses values from a character file instead of manual inputs
    Returns None
    """

    def Start(self):

        # Dialogue-specific adjustments
        assert type(self.scene) == Core.BaseClasses.scene_dialogue.DialogueScene, print(
            "The active scene is not of the 'DialogueScene' type. This action can not be performed"
        )

        #@TODO: Can we consolidate to avoid duplicated if checks for global settings?
        # If the user provides a 'character' block, use details from the relevant character data file if it exists, as
        # well as any applicable global settings
        if 'character' in self.action_data:
            character_data = self.scene.character_data[self.action_data['character']]

            # Dialogue-specific adjustments
            character_data['key'] = 'SpeakerText'

            # OVERRIDES WITH NO PROJECT DEFAULTS
            assert 'name' in character_data, print(
                f"Character file '{self.action_data['character']}' does not have a 'name' param")
            character_data['text'] = character_data['name']

            assert 'color' in character_data, print(
                f"Character file '{self.action_data['character']}' does not have a 'color' param")
            character_data['text_color'] = character_data['color']

            # PROJECT DEFAULTS
            character_data['position'] = self.scene.settings.project_settings['Dialogue'][
                'speaker_text_position']

            character_data['z_order'] = self.scene.settings.project_settings['Dialogue'][
                'speaker_z_order']

            character_data['center_align'] = self.scene.settings.project_settings['Dialogue'][
                'speaker_center_align']

            character_data['font'] = self.scene.settings.project_settings['Dialogue'][
                'speaker_font']

            character_data['text_size'] = self.scene.settings.project_settings['Dialogue'][
                'speaker_text_size']

            new_character_text = TextRenderable(
                self.scene,
                character_data
            )
            # Speaker text does not support transitions currently
            self.scene.active_renderables.Add(new_character_text)

        # If the user has specified a 'speaker' block, build the speaker renderable details using any provided
        # information, and / or any global settings
        elif 'speaker' in self.action_data:
            # Dialogue-specific adjustments
            self.action_data['speaker']['key'] = 'SpeakerText'

            # PROJECT DEFAULTS OVERRIDE
            if 'position' not in self.action_data['speaker']:
                self.action_data['speaker']['position'] = self.scene.settings.project_settings['Dialogue'][
                    'speaker_text_position']

            if 'z_order' not in self.action_data['speaker']:
                self.action_data['speaker']['z_order'] = self.scene.settings.project_settings['Dialogue'][
                    'speaker_z_order']

            if 'center_align' not in self.action_data['speaker']:
                self.action_data['speaker']['center_align'] = self.scene.settings.project_settings['Dialogue'][
                    'speaker_center_align']

            if 'font' not in self.action_data['speaker']:
                self.action_data['speaker']['font'] = self.scene.settings.project_settings['Dialogue'][
                    'speaker_font']

            if 'text_size' not in self.action_data['speaker']:
                self.action_data['speaker']['text_size'] = self.scene.settings.project_settings['Dialogue'][
                    'speaker_text_size']

            if 'text_color' not in self.action_data['speaker']:
                self.action_data['speaker']['text_color'] = self.scene.settings.project_settings['Dialogue'][
                    'speaker_text_color']

            new_speaker_text = TextRenderable(
                self.scene,
                self.action_data['speaker']
            )
            # Speaker text does not support transitions currently
            self.scene.active_renderables.Add(new_speaker_text)

        # If the user has specified a 'dialogue' block, build the speaker renderable
        if 'dialogue' in self.action_data:
            # Dialogue-specific adjustments
            self.action_data['dialogue']['key'] = 'DialogueText'

            # PROJECT DEFAULTS OVERRIDE
            if 'position' not in self.action_data['dialogue']:
                self.action_data['dialogue']['position'] = self.scene.settings.project_settings['Dialogue'][
                    'dialogue_text_position']

            if 'z_order' not in self.action_data['dialogue']:
                self.action_data['dialogue']['z_order'] = self.scene.settings.project_settings['Dialogue'][
                    'dialogue_z_order']

            if 'center_align' not in self.action_data['dialogue']:
                self.action_data['dialogue']['center_align'] = self.scene.settings.project_settings['Dialogue'][
                    'dialogue_center_align']

            if 'font' not in self.action_data['dialogue']:
                self.action_data['dialogue']['font'] = self.scene.settings.project_settings['Dialogue'][
                    'dialogue_font']

            if 'text_size' not in self.action_data['dialogue']:
                self.action_data['dialogue']['text_size'] = self.scene.settings.project_settings['Dialogue'][
                    'dialogue_text_size']

            if 'text_color' not in self.action_data['dialogue']:
                self.action_data['dialogue']['text_color'] = self.scene.settings.project_settings['Dialogue'][
                    'dialogue_text_color']

            new_dialogue_text = TextRenderable(
                self.scene,
                self.action_data['dialogue']
            )

            self.scene.active_renderables.Add(new_dialogue_text)

            # By default, dialogue text fades in. However, allow the user to override this behaviour
            if 'transition' in self.action_data['dialogue']:
                self.active_transition = self.a_manager.CreateTransition(self.action_data['dialogue']['transition'],
                                                                         new_dialogue_text)
                self.active_transition.Start()
            else:
                self.action_data['dialogue']['transition'] = {
                    'type': 'fade_in',
                    'speed': 1000
                }
                self.active_transition = self.a_manager.CreateTransition(self.action_data['dialogue']['transition'],
                                                                         new_dialogue_text)
                self.active_transition.Start()

        return None

    def Update(self, events):
        if self.active_transition.complete is True:
            print("Transition Complete")
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()

class create_character(Action):
    """
    Creates a specialized 'SpriteRenderable' based on character data settings, allowing the developer to move
    references to specific sprites to a character yaml file, leaving the dialogue sequence agnostic.
    Returns a 'SpriteRenderable'.
    This action is only available in DialogueScenes, and requires a 'character' block be provided
    """
    def Start(self):

        # Character-specific adjustments
        assert type(self.scene) == Core.BaseClasses.scene_dialogue.DialogueScene, print(
            "The active scene is not of the 'DialogueScene' type. This action can not be performed")
        assert 'character' in self.action_data, print(
            f"No 'character' block assigned to {self}. This makes for an impossible action!")
        assert 'name' in self.action_data['character'], print(
            f"No 'name' value assigned to {self} character block. This makes for an impossible action!")
        assert 'mood' in self.action_data['character'], print(
            f"No 'mood' value assigned to {self} character block. This makes for an impossible action!")

        # Get the character data from the scene
        character_data = self.scene.character_data[self.action_data['character']['name']]

        assert 'moods' in character_data, print(
            f"Character file '{self.action_data['character']['name']}' does not have a 'moods' block")
        self.action_data['sprite'] = character_data['moods'][self.action_data['character']['mood']]

        # OVERRIDES WITH NO PROJECT DEFAULTS
        if 'position' not in self.action_data:
            self.action_data['position'] = (0, 0)

        # PROJECT DEFAULTS OVERRIDE
        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.project_settings['Sprite'][
                'z_order']

        if 'center_align' not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.project_settings['Sprite'][
                'center_align']

        new_sprite = SpriteRenderable(
            self.scene,
            self.action_data
        )

        # If the user requested a flip action, do so
        if 'flip' in self.action_data:
            if self.action_data['flip']:
                new_sprite.Flip()

        self.scene.active_renderables.Add(new_sprite)

        # Any transitions are applied to the sprite post-load
        if 'transition' in self.action_data:
            self.active_transition = self.a_manager.CreateTransition(self.action_data['transition'], new_sprite)
            self.active_transition.Start()
        else:
            self.scene.Draw()
            self.Complete()

        return new_sprite

    def Update(self, events):
        if self.active_transition.complete:
            print("Transition Complete")
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()

#@TODO: Organize dialogue actions into their own sections (dialogue, choice, choose_branch)
class choice(Action):
    def Start(self):
        self.skippable = False

        # Choice-specific adjustments
        self.action_data["position"] = (0, 0)
        self.action_data["z_order"] = 0
        self.action_data["center_align"] = False
        self.action_data["key"] = "Choice"

        # All choice options use the same underlying 'create_button' action. Specify and enforce that here
        # Additionally, apply all settings determined here to each choice button
        for choice in self.action_data["choices"]:
            # Build the child dict that gets sent to the interact action
            choice["action"] = {
                "action": "choose_branch",
                "branch": choice["branch"],
                "key": choice["key"]
            }

            # CHOICE BUTTONS - OVERRIDES WITH NO PROJECT DEFAULTS
            if "text_position" not in choice:
                choice["text_position"] = self.action_data["position"]

            # CHOICE BUTTONS - PROJECT DEFAULTS OVERRIDE
            if "sprite" not in choice:
                choice["sprite"] = self.scene.settings.project_settings["Choice"][
                    "button_sprite"]

            if 'sprite_hover' not in choice:
                choice["sprite_hover"] = self.scene.settings.project_settings["Choice"][
                    "button_sprite_hover"]

            if "sprite_clicked" not in choice:
                choice["sprite_clicked"] = self.scene.settings.project_settings["Choice"][
                    "button_sprite_clicked"]

            if "z_order" not in choice:
                choice["z_order"] = self.scene.settings.project_settings["Choice"][
                    "button_z_order"]

            if "center_align" not in choice:
                choice["center_align"] = self.scene.settings.project_settings["Choice"][
                    "button_center_align"]

            if "text_z_order" not in choice:
                choice["text_z_order"] = self.scene.settings.project_settings["Choice"][
                    "button_text_z_order"]

            if "text_center_align" not in choice:
                choice["center_align"] = self.scene.settings.project_settings["Choice"][
                    "button_text_center_align"]

            if "font" not in choice:
                choice["font"] = self.scene.settings.project_settings["Choice"][
                    "button_font"]

            if "text_size" not in choice:
                choice["text_size"] = self.scene.settings.project_settings["Choice"][
                    "button_text_size"]

            if "text_color" not in choice:
                choice["text_color"] = self.scene.settings.project_settings["Choice"][
                    "button_text_color"]

        # Choices provide blocks of options. Each one needs to be built
        new_renderable = Choice(
            self.scene,
            self.action_data
        )

        # Generate and add each choice button to the choice container
        for choice_data in self.action_data["choices"]:
            new_renderable.children.append(self.a_manager.PerformAction(choice_data, "create_choice_button"))

        self.scene.active_renderables.Add(new_renderable)

        self.scene.Draw()
        self.Complete()

        return new_renderable

class create_choice_button(Action):
    """ Creates a simplified button renderable used by the choice system. Returns a 'ButtonRenderable' """
    def Start(self):
        self.skippable = False

        # In order to avoid redundant setting scans and global setting validation, no default settings
        # are applied for this action, as its expected that the choice system will provide those details

        new_renderable = Button(
            self.scene,
            self.action_data
        )

        # If the user requested a flip action, do so
        if 'flip' in self.action_data:
            if self.action_data['flip']:
                new_renderable.Flip()

        self.scene.active_renderables.Add(new_renderable)

        self.scene.Draw()
        self.Complete()

        return new_renderable

class choose_branch(Action):
    def Start(self):
        # If a choice button lead to this, delete that whole choice container, otherwise it would persist
        # into the new branch
        if self.scene.active_renderables.Exists("Choice"):
            self.a_manager.PerformAction(
                {"key": "Choice", "transition": {"type": "None"}},
                "remove_container"
            )

        self.scene.SwitchDialogueBranch(self.action_data['branch'])

        self.scene.Draw()
        self.Complete()

# -------------- SOUND ACTIONS --------------

class play_sfx(SoundAction):
    """
    Possible Parameters:
    - key: str
    - sound: str
    - volume : float
    """

    def Start(self):
        new_sound = pygame.mixer.Sound(self.scene.settings.ConvertPartialToAbsolutePath(self.action_data["sound"]))
        new_sound.set_volume(self.action_data["volume"])

        # Sound objects don't have a way of checking their progress, so let's keep track and monitor
        # the channel it was assigned to. Once it's empty, it's a good assumption that it's successfully completed
        self.assigned_channel = new_sound.play(0)
        self.scene.active_sounds[self.action_data["key"]] = new_sound

        return self.assigned_channel

    def Update(self, events):
        if not self.assigned_channel.get_busy():
            self.scene.active_sounds.pop(self.action_data["key"])
            self.Complete()

    def Skip(self):
        self.scene.active_sounds.pop(self.action_data["key"])
        self.Complete()

class stop_sfx(Action):
    """
    Based on a given key, stop and remove the associated sfx from the sound stack
    Possible Parameters:
    - key : str
    """
    def Start(self):
        self.skippable = False

        if "key" in self.action_data:
            self.scene.active_sounds[self.action_data["key"]].stop()  # Stop the sound
            del self.scene.active_sounds[self.action_data["key"]]  # Delete the sound
            self.scene.active_sounds.pop(self.action_data["key"])  # Remove key

            self.Complete()
        else:
            raise ValueError("'stop_sfx' action Failed - Key not specified")

class play_music(SoundAction):
    #@TODO: Implement end-event so this action completes when the song reaches last frame
    """
    Possible Parameters:
    - music: str
    - volume : float
    - loop : bool
    """

    def Start(self):
        self.skippable = False

        # If the user hasn't removed the previous music, forcefully remove it here without any transition
        if self.scene.active_music:
            pygame.mixer.music.stop()  # This will invoke the end-event on the existing music action

        # The pygame music system doesn't use objects, but instead uses a stream. Any changes made against music
        # are made to the stream itself
        pygame.mixer.music.load(self.scene.settings.ConvertPartialToAbsolutePath(self.action_data["music"]))
        pygame.mixer.music.set_volume(self.action_data["volume"])

        loop_count = 0
        if self.action_data["loop"]:
            loop_count = -1

        # Since there can only be one music item active, there is no need to use a key identifier
        pygame.mixer.music.play(loop_count)
        self.scene.active_music = self

        return None

    def Update(self, events):
        if not pygame.mixer.music.get_busy():
            print("SFX completed")
            self.Complete()

class stop_music(Action):
    """
    Stops the currently active music
    Possible Parameters:
    - key : str
    """
    def Start(self):
        self.skippable = False

        pygame.mixer.music.stop()  # This will invoke the end-event on the existing music action
        self.scene.active_music.complete = True
        self.scene.active_music = None  # DEBUG: Remove once the end-event is implemented
        self.Complete()

# -------------- UTILITY ACTIONS --------------

class load_scene(Action):
    """
    Switches scenes to the one specified in the action data. Requires an applicable scene type be provided. Returns
    nothing
    Possible Parameters:
    - scene_file : str
    """
    def Start(self):
        self.skippable = False

        if "scene_file" in self.action_data:
            self.scene.SwitchScene(self.action_data["scene_file"])
        else:
            raise ValueError("Load Scene Failed - No scene file provided, or a scene type was not provided")

        self.Complete()

class wait(Action):
    """
    Waits for a set amount of time before completing
    """
    def Start(self):
        self.counter = 0
        self.target = self.action_data["seconds"]

        return None

    def Update(self, events):
        self.counter += 1 * self.scene.delta_time
        print(self.counter)

        if self.counter >= self.target:
            print("Times up!")
            self.Complete()

    def Skip(self):
        self.Complete()

class quit_game(Action):
    """
    Immediately closes the game
    This is not meant to be called during scenes, but is available as an action for inputs, buttons, etc
    """
    def Start(self):
        self.skippable = False
        self.scene.pygame_lib.quit()
        exit()

# -------------- TRANSITION ACTIONS --------------
""" 
These actions function as transitions in their own right, but are not modifiers on existing actions like
those listed in the 'transitions' file
"""

class fade_scene_from_black(Action):
    """
    Creates a black texture covering the entire screen, then slowly fades it out. Returns 'SpriteRenderable'
    Possible Parameters:
    - z_order : int <GLOBAL_AVAILABLE>
    - speed: int <GLOBAL_AVAILABLE>
    """
    def Start(self):

        # Action-specific adjustments
        self.action_data['position'] = (0, 0)
        self.action_data['key'] = 'Transition'
        self.action_data['center_align'] = False
        self.action_data['sprite'] = "ENGINE_FILES/Content/Sprites/TransitionEffects/transition_fade_black.png"

        # PROJECT DEFAULTS OVERRIDE
        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.project_settings['Scene Transitions']['z_order']

        if 'speed' not in self.action_data:
            self.speed = self.scene.settings.project_settings['Scene Transitions']['speed']
        else:
            self.speed = self.action_data['speed']

        new_sprite = SpriteRenderable(
            self.scene,
            self.action_data
        )

        self.scene.active_renderables.Add(new_sprite)
        self.scene.Draw()

        self.renderable = new_sprite
        self.progress = self.renderable.GetSurface().get_alpha()
        self.goal = 0

        return new_sprite

    def Update(self, events):
        self.progress -= (self.speed * self.scene.delta_time)
        self.renderable.GetSurface().set_alpha(self.progress)

        self.scene.Draw()

        if self.progress <= self.goal:
            print("Transition Complete")
            self.Complete()

    def Skip(self):
        self.renderable.GetSurface().set_alpha(self.goal)
        self.scene.Draw()
        self.Complete()
