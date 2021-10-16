from enum import Enum


class ParameterType(Enum):
    String = 1
    Bool = 2
    Int = 3
    Float = 4
    Vector2 = 5
    Paragraph = 6
    Color = 7
    File = 8
    File_Font = 9
    File_Image = 10
    Dropdown = 11
    Container = 12
    CUST_Resolution = 13
