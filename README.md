# GVNEngine
**Version: 0.2**

# What is the 'GVNEngine'?
![ScreenShot](Progress_Examples/GVNEngine_v02_Dialogue_Scene.png?raw=true "GVNEngine Dialogue Scene")

The GVNEngine is a visual novel / dating simulator game engine created in Python, using the PyGame framework. It is meant as a lightweight, user-friendly engine that offers a content-driven workflow that lets developers focus more on making games, and less on worrying about coding them.

# How to Use the 'GVNEngine'?
Currently, the GVNEngine is heavily in development, and not setup for installation quite yet. However, if you're interested in playing with the engine while it's in development, please contact the developer Garrett Fredley at:<br/>
https://twitter.com/SomeCronzaGuy :shipit: (Dev Twitter)<br/>
https://twitter.com/Nixenneth 🎨 (Art Twitter)<br/>

# License
The GVNEngine is licensed under the Open-Source MIT license. Details can be found in the `LICENSE.txt` file in `/GVNEngine`. Basically, enjoy the engine to it's fullest, and make games without worrying about whether you're allowed to muck around in the source code :smiley:

# Features

## Content-Driven Workflow
The GVNEngine is designed to allow developers to focus more on developing games without worrying about knowing how to code. It makes use of a data language called YAML, which was designed for human readability to simplify the process of creating all sorts of content, such as:

- Scenes
- Dialogue sequences
- Renderables (Objects, interactables, buttons, etc)
- Effects (Fades, scene transitions, etc)

Here is an example of a 'Point & Click' scene created using YAML:
![ScreenShot](Progress_Examples/GVNEngine_v02_Main_Menu_Scene_01.png?raw=true "GVNEngine Main Menu Scene")
```
type: 'PointAndClick'
background: "Content/Sprites/Backgrounds/Background_Space_01_1280.jpg"

buttons:
  - sprite: "Content/Sprites/Interface/Buttons/Menu_Button_Normal.png"
    sprite_hover: "Content/Sprites/Interface/Buttons/Menu_Button_Hover.png"
    sprite_clicked: "Content/Sprites/Interface/Buttons/Menu_Button_Clicked.png"
    action:
      action: "load_scene"
      scene_file: "Content/Scenes/Test_Dialogue_Scene_01.yaml"
      scene_type: "Dialogue"
    position:
      - 0.5
      - 0.5
    text: "Start Game"
    key: "Main_Menu_Start_Button"

  - sprite: "Content/Sprites/Interface/Buttons/Menu_Button_Normal.png"
    sprite_hover: "Content/Sprites/Interface/Buttons/Menu_Button_Hover.png"
    sprite_clicked: "Content/Sprites/Interface/Buttons/Menu_Button_Clicked.png"
    action:
      action: "quit_game"
    position:
      - 0.5
      - 0.65
    text: "Quit Game"
    key: "Main_Menu_Exit_Button"

text:
  - text: "To Infinity"
    text_size: 72
    text_color: [240, 240, 240]
    font: 'Content/Fonts/Comfortaa/Comfortaa-Regular.ttf'
    center_align: True
    position:
      - 0.5
      - 0.3
    z_order: 500
    key: "Title"
    
  - text: "GVNEngine v0.2 - 'To Infinity' Project Example"
    text_size: 16
    text_color: [255, 255, 255]
    font: 'Content/Fonts/Comfortaa/Comfortaa-Regular.ttf'
    center_align: False
    position:
      - 0.01
      - 0.95
    z_order: 9999
    key: "VersionIdentity"
```
Additional examples of how to create the various YAML files for the engine are provided as a part of the repo.

## Action Manager
The Action Manager was developed in order to allow developers (and the engine) to access any number of possible in-game actions in a flexible, YAML-accessible manner.

'Actions' are defined as classes in the `actions.py` file. When an action is requested, such as by a YAML file (Dialogue, clicking interactables, etc), it looks to this file for the corresponding action class. For example: `class load_scene(Action)`. Once found, it calls it, passing it any additional pieces of information provided. An example of a dialogue YAML block:

```
- action: "dialogue"
  character: "Isea"
  dialogue:
    text: "Who are you?"
  wait_for_input: True
```
The above is an example of an action used to display dialogue text to the screen. The action name is called `dialogue`. In the `actions.py` file, there is a corresponding `class dialogue(Action)` class. The engine is capable of correlating these strings to the classes found in the `actions.py` file. 

Additionally, each action is fed the entire data block that was provided when it was called. In the example above, we see that various parameters such as `character` are provided. For the above `dialogue` action, which is one of the provided engine default actions, `character` is used to determine the speaker's name, the color of their name, and the font for their name text.

# GVNEditor
:warning: *This feature is heavily in development, and will most likely be a while before its release
![ScreenShot](Progress_Examples/GVNEditor_v02_Dialogue_Editor.png?raw=true "GVNEditor Main Interface")

The GVNEditor is an editing tool for designing the YAML files used by the GVNEngine. It is built using Python and the PyQt5 binding for the Qt framework. 

## License
The GVNEditor, due to its extensive usage of the Qt framework, is licensed under the Open Source GPL license. Details can be found in the `LICENSE.txt` file in `/GVNEditor`. Basically, you can use the editor in most projects besides private, proprietary ones (Where the source code is not available to the general public). This license does not extend to the GVNEngine, and as long as any edits you make to the editor are pushed back to the repo, you are covered :+1:
