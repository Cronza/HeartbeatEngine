Notes
=============================

Project Settings TBD
------------------------------------
* Project Settings are organized by category when viewed in the 'Game.yaml' file and the editor, but when viewed in
* other .yaml files, they're represented in name only with an '_' prepended to them. This is a unique format only
* applicable to Project Settings

Project Settings v Project Variables
------------------------------------
* Project Setting primarily differ from Project Variables as the latter are authored by users, while the former are authored by the engine developer. 
  While users can customize the project Settings, this is not considered common practice and involves some work
* Project Settings are also uniquely tied to engine logic. For example, connecting actions to the 'mute' Project 
  Setting doesn't magically control the ability to mute the game. Instead, there are actions available to set or control many
  of the project settings, such as 'set_mute' for muting or unmuting the game

