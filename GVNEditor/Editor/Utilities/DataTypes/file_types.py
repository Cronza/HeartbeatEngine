from enum import Enum


class FileType(Enum):
    Scene_Point_And_Click = 1
    Scene_Dialogue = 2
    Character = 3
    Project_Settings = 4


class FileTypeDescriptions:
    descriptions = {
        FileType.Scene_Dialogue: "A scene containing a sequence of dialogue between characters. "
                                 "These files may contain additional branches",

        FileType.Scene_Point_And_Click: "A scene with interactable objects. Perfect for designing "
                                        "Point & Click scenes, or interactive maps",

        FileType.Character: "A file containing details on a character, such as a special font for "
                            "their name, their unique color, or various sprites representing their moods"
    }
