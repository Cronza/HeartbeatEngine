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
import pygame.mixer
import copy
from HBEngine.Core import settings
from HBEngine.Core.Objects.renderable_sprite import SpriteRenderable
from HBEngine.Core.Objects.renderable_text import TextRenderable
from HBEngine.Core.Objects.interactable import Interactable
from HBEngine.Core.Objects.button import Button
from HBEngine.Core.Objects.choice import Choice
from HBEngine.Core.Objects.renderable_container import Container
from Tools.HBYaml.hb_yaml import Reader


# Load the metadata that contains the data definitions for what each
# action accepts for 'action_data', and what globals are in use by any
# action
actions_metadata = Reader.ReadAll(settings.ConvertPartialToAbsolutePath("HBEngine/Core/Actions/actions_metadata.yaml"))


# -------------- BASE ACTIONS --------------


class Action:
    def __init__(self, scene, action_data: dict, a_manager, no_draw: bool = False):
        self.scene = scene
        self.action_data = action_data
        self.a_manager = a_manager
        self.active_transition = None
        self.speed = 500
        self.skippable = True
        self.complete = False
        self.completion_callback = None  # Called by the action manager before it deletes the action
        self.metadata = {}  # Loaded via function

        self.no_draw = no_draw  # Whether to skip adding any resulting renderables to the draw stack

    def Start(self):
        pass

    def Update(self, events):
        pass

    def Skip(self):
        pass

    def Complete(self):
        self.complete = True

    def LoadMetadata(self, action_name: str, recurse: bool = False):
        """
        Given an action name, set the 'metadata' variable using the corresponding data found in the
        actions_metadata.yaml file
        """
        # We have to take a parameter for the action name here because '__class__.__name__' returns the base class name
        # when running under code defined in the base class
        self.metadata = copy.deepcopy(actions_metadata[action_name])

        # Compare the action_data against the metadata. If any items found within the metadata are missing in the
        # action_data, we can assume it was not edited or modified by the user, and that we can defer to either the
        # global value or the default
        self.UpdateFromMetadata(self.metadata, self.action_data)

    def UpdateFromMetadata(self, metadata: dict, action_data: dict, search_term: str = "requirements"):
        """
        Recursively compares the provided action_data against the provided metadata, updating the former when
        it is missing data found in the latter
        """
        for md_req_name, md_req_data in metadata[search_term].items():
            if "children" in md_req_data:
                if md_req_name not in action_data:
                    action_data[md_req_name] = {}

                self.UpdateFromMetadata(md_req_data, action_data[md_req_name], "children")

            elif "template" in md_req_data:
                # Requirements that use templates have a fundamentally unique metadata in that each child is generated
                # from the template instead of being instrinctically a part of the metadata to begin with. Due to this,
                # we must compare the action_data against the metadata template specifically
                #
                # The template data structure is usually a few layers deep. Example:
                #    choices: (Array)
                #        choice: (ArrayElement)
                #            ...

                # Because the top level key names for ArrayElements are generated, we can't do a typical key name
                # search (IE. 'choice_01' instead of 'choice' which matches the metadata). Instead, we're accessing the
                # value dict directly
                template_data = list(md_req_data["template"].values())[0]

                # Update each ArrayElement
                for element_name, element_data in action_data[md_req_name].items():
                    # Skip a level as this is the "ArrayElement" container
                    self.UpdateFromMetadata(template_data, element_data, "children")

            elif md_req_name not in action_data:
                # The item is missing. Update it
                if "global" in md_req_data:
                    action_data[md_req_name] = settings.GetProjectGlobal(md_req_data["global"][0], md_req_data["global"][1])
                else:
                    action_data[md_req_name] = md_req_data["default"]

    def GetMetadataValue(self, key):
        """ Returns the value for the given requirements key (IE. 'position') """
        return self.metadata["requirements"][key]["value"]

    def GetMetadataGlobal(self, key):
        """
        Returns the global value for the given requirements key (IE. 'position').

        This value is returned as a list, with the first index being the name of the category where the global is
        stored, and the second index being the name of the global value. If the specified parameter does not have a
        global value, then return None
        """
        try:
            return self.metadata["requirements"][key]["global"]
        except Exception as exc:
            print(f"Failed to retrieve global value for key '{key}' - {exc}")
            return None


class SoundAction(Action):
    # @TODO: Add Pause function
    def __init__(self, scene, action_data, a_manager):
        super().__init__(scene, action_data, a_manager)
        self.assigned_channel = None


# -------------- GRAPHICS ACTIONS --------------


class remove_renderable(Action):
    """ Based on a given key, remove the associated renderable from the renderable stack """
    def Start(self):
        self.LoadMetadata(__class__.__name__)

        renderable = self.scene.active_renderables.renderables[self.action_data['key']]
        children = []

        if isinstance(renderable, Container):
            # Collect a flattened list of all children in this container
            children = renderable.GetAllChildren()

        # Any transitions are applied to the sprite pre-unload
        if "None" not in self.action_data["transition"]["type"]:
            if children:
                # In order to apply the transition to each and every child of the container, we merge the surfaces
                # and combine them into the container surface. That way, the rendering only manages a single
                # surface. This causes containers to be non-functional once a transition starts, as the underlying
                # children are destroyed before the transition begins

                # Merge the surfaces, then delete the child (Grim, I know)
                for child in children:
                    renderable.surface.blit(child.GetSurface(), (child.rect.x, child.rect.y))
                    self.scene.active_renderables.Remove(child.key)

                renderable.visible = True

            self.active_transition = self.a_manager.CreateTransition(self.action_data["transition"], renderable)
            self.active_transition.Start()
        else:
            if children:
                # Remove all children first
                for child in children:
                    self.scene.active_renderables.Remove(child.key)

            self.scene.active_renderables.Remove(self.action_data["key"])
            self.scene.Draw()
            self.Complete()

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


class create_sprite(Action):
    """ Create a sprite renderable using passed in settings. Returns a 'SpriteRenderable' """
    def Start(self):
        self.LoadMetadata(__class__.__name__)

        new_sprite = SpriteRenderable(
            self.scene,
            self.action_data
        )

        if "flip" in self.action_data:
            if self.action_data["flip"]:
                new_sprite.Flip()

        if not self.no_draw:
            self.scene.active_renderables.Add(new_sprite)

            # Any transitions are applied to the sprite post-load
            if "None" not in self.action_data["transition"]["type"]:
                self.active_transition = self.a_manager.CreateTransition(self.action_data["transition"], new_sprite)
                self.active_transition.Start()
            else:
                self.scene.Draw()
                self.Complete()
        else:
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


class create_background(Action):
    """
    Creates a pre-configured 'SpriteRenderable' suitable as a background image. Returns a
    'SpriteRenderable'
    """
    def Start(self):
        self.LoadMetadata(__class__.__name__)

        self.skippable = False

        new_sprite = SpriteRenderable(
            self.scene,
            self.action_data,
        )

        if not self.no_draw:
            self.scene.active_renderables.Add(new_sprite)
            self.scene.Draw()
        self.Complete()

        return new_sprite


#class create_interactable(Action):  # AWAITING EDITOR IMPLEMENTATION - WILL BE UPDATED
#    """ Creates an interactable renderable, and adds it to the renderable stack. Returns an 'Interactable'"""
#    def Start(self):
#        self.LoadMetadata(__class__.__name__)
#        self.skippable = False
#
#        # OVERRIDES WITH NO PROJECT DEFAULTS
#        if 'position' not in self.action_data:
#            self.action_data['position'] = (0, 0)
#
#        # PROJECT DEFAULTS OVERRIDE
#        if 'z_order' not in self.action_data:
#            self.action_data['z_order'] = settings.project_settings['Interactable'][
#                'z_order']
#
#        if 'center_align' not in self.action_data:
#            self.action_data['center_align'] = settings.project_settings['Interactable'][
#                'center_align']
#
#        new_renderable = Interactable(
#            self.scene,
#            self.action_data,
#        )
#
#        # If the user requested a flip action, do so
#        if 'flip' in self.action_data:
#            if self.action_data['flip']:
#                new_renderable.Flip()
#
#        self.scene.active_renderables.Add(new_renderable)
#
#        self.scene.Draw()
#        self.Complete()
#
#        return new_renderable


class create_text(Action):
    """
    Create a TextRenderable at the target location, with the given settings. Returns a 'TextRenderable'
    """
    def Start(self):
        self.LoadMetadata(__class__.__name__)

        new_text_renderable = TextRenderable(
            self.scene,
            self.action_data
        )

        if not self.no_draw:
            self.scene.active_renderables.Add(new_text_renderable)

            if "None" not in self.action_data["transition"]["type"]:
                self.active_transition = self.a_manager.CreateTransition(self.action_data["transition"], new_text_renderable)
                self.active_transition.Start()
            else:
                self.scene.Draw()
                self.Complete()
        else:
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


class create_button(Action):
    """
    Creates a button interactable, and adds it to the renderable stack. Returns a 'Button'
    """
    def Start(self):
        self.LoadMetadata(__class__.__name__)
        self.skippable = False

        # System defined overrides
        self.action_data["button_text"]["z_order"] = self.action_data["z_order"] + 1

        new_renderable = Button(
            self.scene,
            self.action_data
        )

        if not self.no_draw:
            self.scene.active_renderables.Add(new_renderable)
            self.scene.Draw()
        self.Complete()

        return new_renderable


class create_text_button(Action):
    """
    Creates a text-only button interactable, and adds it to the renderable stack. Returns a 'Button'
    """
    def Start(self):
        self.LoadMetadata(__class__.__name__)
        self.skippable = False

        new_renderable = Button(
            self.scene,
            self.action_data
        )

        if not self.no_draw:
            self.scene.active_renderables.Add(new_renderable)
            self.scene.Draw()
        self.Complete()

        return new_renderable


#class create_container(Action): # AWAITING EDITOR IMPLEMENTATION - WILL BE UPDATED
#    """ Creates a simple container renderable with the provided action data. Returns a 'Container' """
#
#    # @TODO: Update to new workflow
#    def Start(self):
#        self.LoadMetadata(__class__.__name__)
#        self.skippable = False
#
#        # Container-specific adjustments
#        self.action_data['position'] = (0, 0)
#        self.action_data['z_order'] = 0
#        self.action_data['center_align'] = False
#
#        # Containers aren't rendered, so use defaults
#        new_renderable = Container(
#            self.scene,
#            self.action_data,
#        )
#
#        self.scene.active_renderables.Add(new_renderable)
#
#        self.scene.Draw()
#        self.Complete()
#
#        return new_renderable


# -------------- DIALOGUE ACTIONS --------------


#class create_dialogue_interface(Action):
#    """
#    Creates sprite renderables for the dialogue and speaker text, and assigns them to the renderable stack using
#    pre-configured settings
#    """
#    def Start(self):
#        self.LoadMetadata(__class__.__name__)
#        self.skippable = False
#
#        dialogue_frame = SpriteRenderable(
#            self.scene,
#            self.action_data
#        )
#
#        # Add the dialogue interface to the sprite group so they exist until explicitly unloaded
#        self.scene.active_renderables.Add(dialogue_frame)
#
#        self.scene.Draw()
#        self.Complete()


class dialogue(Action):
    """
    Create dialogue and speaker text renderables, and add them to the renderable stack using pre-configured settings.
    If the user specifies a 'character' block, create a speaker text using the character details instead. Returns None
    """
    def Start(self):
        self.LoadMetadata(__class__.__name__)

        new_speaker_text = TextRenderable(
            self.scene,
            self.action_data["speaker"]
        )

        new_dialogue_text = TextRenderable(
            self.scene,
            self.action_data["dialogue"]
        )

        self.scene.active_renderables.Add(new_speaker_text)
        self.scene.active_renderables.Add(new_dialogue_text)

        # Note: Speaker text does not support transitions currently
        if self.action_data["dialogue"]["transition"]["type"] != "None":
            self.active_transition = self.a_manager.CreateTransition(self.action_data["dialogue"]["transition"], new_dialogue_text)
            self.active_transition.Start()
        else:
            self.scene.Draw()
            self.Complete()

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


#class character_dialogue(Action):
#    """
#    A specialized variant of the 'dialogue' class that uses values from a character file instead of manual inputs
#    Returns None
#    """
#
#    def Start(self):
#        self.LoadMetadata(__class__.__name__)
#
#        # Dialogue-specific adjustments
#        assert type(self.scene) == Core.BaseClasses.scene_dialogue.DialogueScene, print(
#            "The active scene is not of the 'DialogueScene' type. This action can not be performed"
#        )
#
#        #@TODO: Can we consolidate to avoid duplicated if checks for global settings?
#        # If the user provides a 'character' block, use details from the relevant character data file if it exists, as
#        # well as any applicable global settings
#        if 'character' in self.action_data:
#            character_data = self.scene.character_data[self.action_data['character']]
#
#            # Dialogue-specific adjustments
#            character_data['key'] = 'SpeakerText'
#
#            # OVERRIDES WITH NO PROJECT DEFAULTS
#            assert 'name' in character_data, print(
#                f"Character file '{self.action_data['character']}' does not have a 'name' param")
#            character_data['text'] = character_data['name']
#
#            assert 'color' in character_data, print(
#                f"Character file '{self.action_data['character']}' does not have a 'color' param")
#            character_data['text_color'] = character_data['color']
#
#            # PROJECT DEFAULTS
#            character_data['position'] = settings.project_settings['Dialogue'][
#                'speaker_text_position']
#
#            character_data['z_order'] = settings.project_settings['Dialogue'][
#                'speaker_z_order']
#
#            character_data['center_align'] = settings.project_settings['Dialogue'][
#                'speaker_center_align']
#
#            character_data['font'] = settings.project_settings['Dialogue'][
#                'speaker_font']
#
#            character_data['text_size'] = settings.project_settings['Dialogue'][
#                'speaker_text_size']
#
#            new_character_text = TextRenderable(
#                self.scene,
#                character_data
#            )
#            # Speaker text does not support transitions currently
#            self.scene.active_renderables.Add(new_character_text)
#
#        # If the user has specified a 'speaker' block, build the speaker renderable details using any provided
#        # information, and / or any global settings
#        elif 'speaker' in self.action_data:
#            # Dialogue-specific adjustments
#            self.action_data['speaker']['key'] = 'SpeakerText'
#
#            # PROJECT DEFAULTS OVERRIDE
#            if 'position' not in self.action_data['speaker']:
#                self.action_data['speaker']['position'] = settings.project_settings['Dialogue'][
#                    'speaker_text_position']
#
#            if 'z_order' not in self.action_data['speaker']:
#                self.action_data['speaker']['z_order'] = settings.project_settings['Dialogue'][
#                    'speaker_z_order']
#
#            if 'center_align' not in self.action_data['speaker']:
#                self.action_data['speaker']['center_align'] = settings.project_settings['Dialogue'][
#                    'speaker_center_align']
#
#            if 'font' not in self.action_data['speaker']:
#                self.action_data['speaker']['font'] = settings.project_settings['Dialogue'][
#                    'speaker_font']
#
#            if 'text_size' not in self.action_data['speaker']:
#                self.action_data['speaker']['text_size'] = settings.project_settings['Dialogue'][
#                    'speaker_text_size']
#
#            if 'text_color' not in self.action_data['speaker']:
#                self.action_data['speaker']['text_color'] = settings.project_settings['Dialogue'][
#                    'speaker_text_color']
#
#            new_speaker_text = TextRenderable(
#                self.scene,
#                self.action_data['speaker']
#            )
#            # Speaker text does not support transitions currently
#            self.scene.active_renderables.Add(new_speaker_text)
#
#        # If the user has specified a 'dialogue' block, build the speaker renderable
#        if 'dialogue' in self.action_data:
#            # Dialogue-specific adjustments
#            self.action_data['dialogue']['key'] = 'DialogueText'
#
#            # PROJECT DEFAULTS OVERRIDE
#            if 'position' not in self.action_data['dialogue']:
#                self.action_data['dialogue']['position'] = settings.project_settings['Dialogue'][
#                    'dialogue_text_position']
#
#            if 'z_order' not in self.action_data['dialogue']:
#                self.action_data['dialogue']['z_order'] = settings.project_settings['Dialogue'][
#                    'dialogue_z_order']
#
#            if 'center_align' not in self.action_data['dialogue']:
#                self.action_data['dialogue']['center_align'] = settings.project_settings['Dialogue'][
#                    'dialogue_center_align']
#
#            if 'font' not in self.action_data['dialogue']:
#                self.action_data['dialogue']['font'] = settings.project_settings['Dialogue'][
#                    'dialogue_font']
#
#            if 'text_size' not in self.action_data['dialogue']:
#                self.action_data['dialogue']['text_size'] = settings.project_settings['Dialogue'][
#                    'dialogue_text_size']
#
#            if 'text_color' not in self.action_data['dialogue']:
#                self.action_data['dialogue']['text_color'] = settings.project_settings['Dialogue'][
#                    'dialogue_text_color']
#
#            new_dialogue_text = TextRenderable(
#                self.scene,
#                self.action_data['dialogue']
#            )
#
#            self.scene.active_renderables.Add(new_dialogue_text)
#
#            # By default, dialogue text fades in. However, allow the user to override this behaviour
#            if 'transition' in self.action_data['dialogue']:
#                self.active_transition = self.a_manager.CreateTransition(self.action_data['dialogue']['transition'],
#                                                                         new_dialogue_text)
#                self.active_transition.Start()
#            else:
#                self.action_data['dialogue']['transition'] = {
#                    'type': 'fade_in',
#                    'speed': 1000
#                }
#                self.active_transition = self.a_manager.CreateTransition(self.action_data['dialogue']['transition'],
#                                                                         new_dialogue_text)
#                self.active_transition.Start()
#
#        return None
#
#    def Update(self, events):
#        if self.active_transition.complete is True:
#            print("Transition Complete")
#            self.Complete()
#        else:
#            self.active_transition.Update()
#
#    def Skip(self):
#        if self.active_transition:
#            self.active_transition.Skip()
#        self.Complete()


#class create_character(Action):
#    """
#    Creates a specialized 'SpriteRenderable' based on character data settings, allowing the developer to move
#    references to specific sprites to a character yaml file, leaving the dialogue sequence agnostic.
#    Returns a 'SpriteRenderable'.
#    This action is only available in DialogueScenes, and requires a 'character' block be provided
#    """
#    def Start(self):
#        self.LoadMetadata(__class__.__name__)
#
#        # Character-specific adjustments
#        assert type(self.scene) == Core.BaseClasses.scene_dialogue.DialogueScene, print(
#            "The active scene is not of the 'DialogueScene' type. This action can not be performed")
#        assert 'character' in self.action_data, print(
#            f"No 'character' block assigned to {self}. This makes for an impossible action!")
#        assert 'name' in self.action_data['character'], print(
#            f"No 'name' value assigned to {self} character block. This makes for an impossible action!")
#        assert 'mood' in self.action_data['character'], print(
#            f"No 'mood' value assigned to {self} character block. This makes for an impossible action!")
#
#        # Get the character data from the scene
#        character_data = self.scene.character_data[self.action_data['character']['name']]
#
#        assert 'moods' in character_data, print(
#            f"Character file '{self.action_data['character']['name']}' does not have a 'moods' block")
#        self.action_data['sprite'] = character_data['moods'][self.action_data['character']['mood']]
#
#        # OVERRIDES WITH NO PROJECT DEFAULTS
#        if 'position' not in self.action_data:
#            self.action_data['position'] = (0, 0)
#
#        # PROJECT DEFAULTS OVERRIDE
#        if 'z_order' not in self.action_data:
#            self.action_data['z_order'] = settings.project_settings['Sprite'][
#                'z_order']
#
#        if 'center_align' not in self.action_data:
#            self.action_data['center_align'] = settings.project_settings['Sprite'][
#                'center_align']
#
#        new_sprite = SpriteRenderable(
#            self.scene,
#            self.action_data
#        )
#
#        # If the user requested a flip action, do so
#        if 'flip' in self.action_data:
#            if self.action_data['flip']:
#                new_sprite.Flip()
#
#        self.scene.active_renderables.Add(new_sprite)
#
#        # Any transitions are applied to the sprite post-load
#        if 'transition' in self.action_data:
#            self.active_transition = self.a_manager.CreateTransition(self.action_data['transition'], new_sprite)
#            self.active_transition.Start()
#        else:
#            self.scene.Draw()
#            self.Complete()
#
#        return new_sprite
#
#    def Update(self, events):
#        if self.active_transition.complete:
#            print("Transition Complete")
#            self.Complete()
#        else:
#            self.active_transition.Update()
#
#    def Skip(self):
#        if self.active_transition:
#            self.active_transition.Skip()
#        self.Complete()


class choice(Action):
    def Start(self):
        self.LoadMetadata(__class__.__name__)
        self.skippable = False

        # Create an object that acts as a parent for all the choice buttons. When this is deleted, the buttons
        # will be deleted with it
        self.action_data["position"] = (0, 0)
        self.action_data["z_order"] = 0
        self.action_data["center_align"] = False
        self.action_data["key"] = "Choice"
        new_renderable = Choice(
            self.scene,
            self.action_data
        )

        # Generate a button for each choice, adding them to the active renderables group for access to updates
        # and rendering. Then, add them as a child to the choice object so they're destroyed as a collective
        #
        # Because we the data comes from the 'template' key, we don't have a mechanism to load from the action
        for choice_name, choice_data in self.action_data["choices"].items():
            # Define what the button does when clicked
            choice_data["event"] = {
                "action": "choose_branch",
                "branch": choice_data["branch"]
            }

            # The key is generated dynamically instead of being provided by the file
            choice_data["key"] = choice_name

            new_child = Button(self.scene, choice_data)
            self.scene.active_renderables.Add(new_child)
            new_renderable.children.append(new_child)

        # Add the choice parent object to the render stack
        self.scene.active_renderables.Add(new_renderable)

        self.scene.Draw()
        self.Complete()

        return new_renderable


class choose_branch(Action):
    def Start(self):
        #self.LoadMetadata(__class__.__name__)

        # If a choice button lead to this, delete that whole choice container, otherwise it would persist
        # into the new branch
        if self.scene.active_renderables.Exists("Choice"):
            self.a_manager.PerformAction(
                {"key": "Choice", "transition": {"type": "None"}},
                "remove_renderable"
            )

        self.scene.SwitchDialogueBranch(self.action_data['branch'])

        self.scene.Draw()
        self.Complete()

        return None


# -------------- SOUND ACTIONS --------------


class play_sfx(SoundAction):
    """
    Possible Parameters:
    - key: str
    - sound: str
    - volume : float
    """

    def Start(self):
        self.LoadMetadata(__class__.__name__)

        new_sound = pygame.mixer.Sound(settings.ConvertPartialToAbsolutePath(self.action_data["sound"]))
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
        self.LoadMetadata(__class__.__name__)
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

    def Start(self):
        self.LoadMetadata(__class__.__name__)
        self.skippable = False

        # If the user hasn't removed the previous music, forcefully remove it here without any transition
        if self.scene.active_music:
            pygame.mixer.music.stop()  # This will invoke the end-event on the existing music action

        # The pygame music system doesn't use objects, but instead uses a stream. Any changes made against music
        # are made to the stream itself
        pygame.mixer.music.load(settings.ConvertPartialToAbsolutePath(self.action_data["music"]))
        pygame.mixer.music.set_volume(self.action_data["volume"])

        loop_count = 0
        if self.action_data["loop"]:
            loop_count = -1

        # Since there can only be one music item active, there is no need to use a key identifier
        pygame.mixer.music.play(loop_count)
        self.scene.active_music = self

        self.Complete()

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
        self.LoadMetadata(__class__.__name__)
        self.skippable = False

        pygame.mixer.music.stop()  # This will invoke the end-event on the existing music action
        self.scene.active_music.complete = True
        self.scene.active_music = None  # DEBUG: Remove once the end-event is implemented
        self.Complete()


# -------------- UTILITY ACTIONS --------------


class load_scene(Action):
    """ Switches scenes to the one specified in the action data """
    def Start(self):
        self.skippable = False

        self.scene.SwitchScene(self.action_data["scene_file"])
        self.Complete()


class wait(Action):
    """ Waits for a set amount of time before completing """
    def Start(self):
        self.LoadMetadata(__class__.__name__)
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
        self.LoadMetadata(__class__.__name__)
        self.skippable = False
        pygame.quit()
        exit()


# -------------- TRANSITION ACTIONS --------------
""" 
These actions function as transitions in their own right, but are not modifiers on existing actions like
those listed in the 'transitions' file
"""


class scene_fade_in(Action):
    """
    Creates a texture of the selected color covering the entire screen, then slowly fades it out

    Returns 'SpriteRenderable'
    """
    def Start(self):
        self.LoadMetadata(__class__.__name__)

        self.action_data['key'] = 'Transition_SceneFade'
        self.action_data['z_order'] = 9999999999999999999
        self.action_data['center_align'] = False

        if self.action_data["color"] == "black":
            self.action_data['sprite'] = "HBEngine/Content/Sprites/TransitionEffects/transition_fade_black.png"
        elif self.action_data["color"] == "white":
            self.action_data['sprite'] = "HBEngine/Content/Sprites/TransitionEffects/transition_fade_white.png"
        else:
            raise ValueError(f"'scene_fade_in' action Failed - Invalid color value provided: {self.action_data['color']}")

        if 'speed' in self.action_data:
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
            self.Complete()

    def Skip(self):
        self.renderable.GetSurface().set_alpha(self.goal)
        self.scene.Draw()
        self.Complete()


class scene_fade_out(Action):
    """
    Creates a texture of the selected color covering the entire screen, then slowly fades it in

    Returns 'SpriteRenderable'
    """
    def Start(self):
        self.LoadMetadata(__class__.__name__)

        self.action_data['key'] = 'Transition_SceneFade'
        self.action_data['z_order'] = 9999999999999999999
        self.action_data['center_align'] = False

        if self.action_data["color"] == "black":
            self.action_data['sprite'] = "HBEngine/Content/Sprites/TransitionEffects/transition_fade_black.png"
        elif self.action_data["color"] == "white":
            self.action_data['sprite'] = "HBEngine/Content/Sprites/TransitionEffects/transition_fade_white.png"
        else:
            raise ValueError(f"'scene_fade_out' action Failed - Invalid color value provided: {self.action_data['color']}")

        if 'speed' in self.action_data:
            self.speed = self.action_data['speed']

        new_sprite = SpriteRenderable(
            self.scene,
            self.action_data
        )
        new_sprite.GetSurface().set_alpha(0)

        self.scene.active_renderables.Add(new_sprite)
        self.scene.Draw()

        self.renderable = new_sprite
        self.progress = 0
        self.goal = 256

        return new_sprite

    def Update(self, events):
        self.progress += (self.speed * self.scene.delta_time)
        self.renderable.GetSurface().set_alpha(self.progress)

        self.scene.Draw()

        if self.progress >= self.goal:
            self.Complete()

    def Skip(self):
        self.renderable.GetSurface().set_alpha(self.goal)
        self.scene.Draw()
        self.Complete()


# -------------- INTERFACE ACTIONS --------------


class pause(Action):
    """ Requests that the active scene pause the game and show the pause interface. Returns 'None' """
    def Start(self):
        self.scene.Pause()
        self.Complete()
        return None

class unpause(Action):
    """ Requests that the active scene unpause the game and remove the pause interface. Returns 'None' """
    def Start(self):
        self.scene.Unpause()
        self.Complete()
        return None

class switch_page(Action):
    """ Requests a page load for the target interface. Returns 'None' """
    def Start(self):
        if self.scene.active_interfaces.Exists(self.action_data["owner"]):
            owner = self.scene.active_interfaces.GetFromKey(self.action_data["owner"])
            owner.LoadPage(self.action_data["page"])

        self.scene.Draw()
        self.Complete()
        return None

