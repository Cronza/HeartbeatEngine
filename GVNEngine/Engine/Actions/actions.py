"""
This file lists available actions that can be defined in various .yaml files throughout the GVNEngine project.
All actions take in two parameters:

    - scene - Simply a reference to the scene object. This is handled by the engine
    - action_data - This is a dictionary that is created by reading in a section of .yaml. A .yaml example looks like:
        - action: "load_sprite"
          key: "Speaker_01"
          sprite: "Content/Sprites/Characters/Mary/Mary_Happy.png"
          position:
            x: 0.2
            y: 1.4

All actions can be designed to accept and use a variety of different parameters. To learn more, review some of the
provided actions
"""
from threading import Thread

from Engine.BaseClasses.renderable_sprite import SpriteRenderable
from Engine.BaseClasses.renderable_text import TextRenderable
from Engine.BaseClasses.interactable import Interactable

def load_background(scene, action_data):
    """ Create a background renderable with pre-set settings"""
    new_sprite = SpriteRenderable(
        action_data['sprite'],
        (0,0)
    )

    new_sprite.key = "Background"
    new_sprite.z_order = -9999
    new_sprite.center_align = False

    scene.renderables_group.Add(new_sprite)

def create_interactable(scene, action_data):
    new_renderable = Interactable(
        action_data['data'],
        tuple(action_data['position'].values())
    )

    new_renderable.scene = scene
    new_renderable.key = action_data['key']

    scene.renderables_group.Add(new_renderable)

def load_sprite(scene, action_data):
    """ Create a sprite renderable using passed in settings """
    new_sprite = SpriteRenderable(
        action_data['sprite'],
        tuple([action_data['position']['x'], action_data['position']['y']])
    )

    # Assign the key to the sprite so it can be unloaded in the future
    if 'key' in action_data:
        new_sprite.key = action_data['key']
    else:
        print('Load Sprite action has no defined key. This will cause unload attempts to fail')

    # If the user requested a flip action, do so
    if 'flip' in action_data:
        if action_data['flip'] is not False:
            new_sprite.surface = scene.pygame_lib.transform.flip(new_sprite.surface, True, False)

    scene.renderables_group.Add(new_sprite)

def unload_sprite(scene, action_data):
    """ Based on a given key, remove the associated sprite from the renderable stack """
    if 'key' in action_data:
        sprite = scene.renderables_group.renderables[action_data['key']]
        scene.renderables_group.Remove(action_data['key'])
    else:
        print("Unload Sprite action Failed - Key not specified")

def dialogue(scene, action_data):
    """
    Create dialogue and speaker text renderables, and add them to the renderable stack using pre-configured settings
    """

    new_speaker_text = TextRenderable(
        (0.08, 0.675),
        action_data['speaker_text'],
        action_data['speaker_font'],
        action_data['speaker_text_size'],
        action_data['speaker_text_color']
    )
    new_speaker_text.z_order = 200
    new_speaker_text.key = "SpeakerText"

    new_dialogue_text = TextRenderable(
        (0.08, 0.77),
        action_data['dialogue_text'],
        action_data['dialogue_font'],
        action_data['dialogue_text_size'],
        action_data['dialogue_text_color']
    )
    new_dialogue_text.z_order = 200
    new_dialogue_text.key = "DialogueText"

    # Add the text to the renderables list instead of the sprite group as text is a temporary element that is
    # meant to be drawn over
    scene.renderables_group.Add(new_speaker_text)
    scene.renderables_group.Add(new_dialogue_text)


def load_dialogue_interface(scene, action_data):
    """
    Creates sprite renderables for the dialogue and speaker text, and assigns them to the renderable stack using
    pre-configured settings
    """
    dialogue_frame = SpriteRenderable(
        scene.settings.dialogue_frame_sprite,
        (0.5, 0.85)
    )
    dialogue_frame.z_order = 100
    dialogue_frame.key = 'DialogueFrame'
    speaker_frame = SpriteRenderable(
        scene.settings.dialogue_speaker_frame_sprite,
        (0.2, 0.7)
    )
    speaker_frame.z_order = 100
    speaker_frame.key = 'SpeakerFrame'

    # Add the dialogue interface to the sprite group so they exist until explicitly unloaded
    scene.renderables_group.Add(dialogue_frame)
    scene.renderables_group.Add(speaker_frame)

def load_scene(scene, action_data):
    """ Switches scenes to the one specified in the action data. Requires an applicable scene type be provided """
    if 'scene_file' in action_data and 'scene_type' in action_data:
        scene.SwitchScene(action_data['scene_file'], action_data['scene_type'])
    else:
        print('Load Scene Failed - No scene file provided, or a scene type was not provided')
