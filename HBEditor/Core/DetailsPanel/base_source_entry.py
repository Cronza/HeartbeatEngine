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


class SourceEntry:
    """ A base class for all widgets that may be considered "Source" or "Active" entries to the details panel """
    def Refresh(self, change_tree: list = None):
        """
        Called when a relevant change was made in the details panel, and the active source needs to be informed. If
        'change_tree' was not provided, then consider this a "full" refresh

        Optional: change_tree - A descending list, starting with the top-most parent, of all action_data names
        leading to the specific entry that was edited (IE. ["parent", "parent", "center_align"])
        """
        raise NotImplementedError("'Refresh' not implemented - This is mandatory'")
