# Heartbeat Engine
![ScreenShot](Images/HeartbeatEngine_Banner.jpg?raw=true "Heartbeat Engine Banner")
[![License](https://img.shields.io/badge/license-GPLv3-blue?label=license&style=flat-square)](LICENSE.txt)
[![GitHub issues](https://img.shields.io/github/issues-raw/Cronza/HeartbeatEngine?style=flat-square)](https://github.com/Cronza/HeartbeatEngine/issues)
[![Python Version](https://img.shields.io/badge/python-3.12-4B8BBE?style=flat-square)](https://www.python.org/downloads/release/python-380/)
[![Twitter Badge](https://img.shields.io/badge/Twitter-Profile-informational?style=flat-square&logo=twitter&logoColor=white&color=1CA2F1)](https://twitter.com/SomeCronzaGuy)

<p align="center"><em>A Visual Novel / Point & Click Game Engine Designed for Creative Developers</em></p>

# What is the 'Heartbeat Engine'?
![ScreenShot](Images/v02_Dialogue_Scene.png?raw=true "Dialogue Scene")
<p align="center"><em>Fig 1 - An example of branching dialogue in Visual Novel Format</em></p>

The Heartbeat Engine is a Visual Novel / Point & Click game engine written in Python using the PyGame framework, with a fully-fledged editor built in PyQt6. It is meant as a lightweight, user-friendly engine that allows developers to focus more on making games, and less on worrying about coding them.

# What can I do with the 'Heartbeat Engine'?
![ScreenShot](Images/General_Editor_Example.png?raw=true "General Editor Example")
<p align="center"><em>Fig 2 - Designing a Scene with the Drag 'n Drop Scene Editor</em></p>

Using the Heartbeat Editor, users are given a platform to design and build their projects. From importing external assets such as Art and Music to creating levels and scenes, the users have the tools to succeed.

Within the Heartbeat Editor are a collection of "Sub-editors" which allow users to create custom formats representing levels, interfaces, dialogue sequences, etc. The editors for each of these formats are designed to be as user-friendly as possible, and require no prior experience with coding to use.

![ScreenShot](Images/Interface_Editor_Template_Options.jpg?raw=true "Interface Template Options")
<p align="center"><em>Fig 3 - Available templates when creating Interfaces</em></p>

To further assist in the development of user projects, the Heartbeat Editor provides free templates and samples of custom formats, as well as free assets to fulfill a variety of needs such as:

1. Sprites (Buttons, backgrounds, etc)
2. Fonts
3. Audio (Music, SFX)

These are all accessible directly through the Heartbeat Editor, and require no additional software or downloads to use.

# Getting Started
Currently, the Heartbeat Engine is in core development, so there are no compiled releases available. As such, you will need to setup your local environment to use the engine from source. Please follow these steps to do so:

1. Get the Engine Source

    ```
    git clone <https://github.com/Cronza/HeartbeatEngine.git>
    ```

2. Create a virtual environment (venv) in the repo folder

    *Note*: This is technically optional, although it is highly advised as to isolate this project and its dependencies. In addition, some utility terminal scripts which come with the engine explicitly refer to a local venv, and will fail if you do not do this.
    ```
    python -m venv <repo_root>/venv
    ```
    
3. Install from `requirements.txt`

    ```
    <repo_root>/venv/Scripts/pip.exe install -r <repo_root>/requirements.txt
    ```
   
4. Launch the Editor
    
    - Option 1: Run `launch_editor.bat`. This will launch the editor with a CMD terminal for debug output. However, the lack of debugger will mean fatal crashes are not caught.
    - Option 2: Use PyCharm / another IDE and invoke `python.exe main.py`. This offers more debugging functions and error handling, and is the advised workflow if you intend to modify the engine source (I personally use PyCharm)
   

# License
The Heartbeat Engine is licensed under the GPL version 3 (GPLv3) license. Details can be found in the `LICENSE.txt` file, but essentially any projects created with the engine are entirely, 100% yours. You may use your own license for them, keep them as private works, and release them commercially without worry. 

However, if you decide to fork the engine and alter or extend its behaviour (which I wholeheartedly welcome!), then that code must abide by the GPLv3 license and remain open source.
 
# Features
## Simplified File Formats
![ScreenShot](Images/HBEditor_Dialogue_Editor.png?raw=true "Dialogue Scene")
<p align="center"><em>Fig 4 - The Dialogue Editor with an example of numerous configurable properties for an action</em></p>

The Heartbeat Engine uses YAML for its proprietary file formats such as `.scene`, `.dialogue`, etc so that the underlying files are human-readable and easy to edit outside of the Heartbeat Editor.

For example, if you were to create a Dialogue sequence within the Heartbeat Editor that contains a `create_sprite` action, and then open the underlying file in a text editor, you would see the following:

```
- create_sprite:
    key: ExampleKey
    sprite: HBEngine/Content/Sprites/Interface/Buttons/Menu_Button_Normal.png
    position:
    - 0.5
    - 0.5
    center_align: true
    z_order: 0
    flip: false
    transition:
      type: None
      speed: 500
    conditions: {}
    post_wait: wait_for_input
```

While the Heartbeat Editor acts as a wrapper for these files, anyone can edit these files directly if they need to perform a hotfix, or need to make changes through automation.

## Action Manager
The Action Manager was created in order to allow developers (and the engine) to access any number of possible in-game actions in a flexible, YAML-accessible manner.

'Actions' are defined as classes in the `actions.py` file. When an action is requested, such as by a YAML file (Dialogue, clicking interactables, etc), it looks to this file using Python's reflection capabilities for the corresponding action class. For example: `class load_scene(Action)`. Once found, it calls it, passing it any additional pieces of information provided. An example of a dialogue YAML block:

```
 - dialogue:
    speaker:
      text: Cronza
      transition: {}
    dialogue:
      text: Seg Faults Suck
      transition: {}
    conditions: {}
    post_wait: wait_for_input
```
The above is an example of an action used to display dialogue text to the screen. The action name is called `dialogue`. In the `actions.py` file, there is a corresponding `class dialogue(Action)` class. The engine is capable of correlating these strings to the classes found in the `actions.py` file. 

Additionally, each action is fed the entire data block that was provided when it was called. In the example above, we see a variety of parameters such as `post_wait` which are used to alter the function of the corresponding action. 
