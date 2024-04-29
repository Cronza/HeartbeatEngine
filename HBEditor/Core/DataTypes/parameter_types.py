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
from enum import Enum


class ParameterType(Enum):
    String = 1
    Bool = 2
    Int = 3
    Float = 4
    Vector2 = 5
    Paragraph = 6
    Color = 7
    Scene = 8
    Dialogue = 9
    Interface = 10
    Asset_Data = 11
    Asset_Font = 12
    Asset_Image = 13
    Asset_Sound = 14
    Dropdown = 15
    Container = 16
    Array_Element = 17
    Array = 18
    Event = 19
    CUST_Resolution = 20
