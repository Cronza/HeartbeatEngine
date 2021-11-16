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
from PyQt5 import QtGui, QtWidgets, QtCore
from HBEditor.Interface.Primitives.input_entry_base import InputEntryBase
from HBEditor.Interface.Primitives.input_entry_dropdown import InputEntryDropdown
from HBEditor.Interface.Primitives.input_entry_container import InputEntryContainer
from HBEditor.Interface.Primitives.input_entry_text import InputEntryText

class InputEntryChoice(InputEntryBase):
    """
    A heavily specialized widget built to allow an optionally-expandable list of drop-downs,
    each presenting a choice of an existing branch

    Given this class has user-control over generating the children, it needs access to adding and
    rendering children
    """

    def __init__(self, settings, data, add_to_parent_func, create_input_widget_func, branches_list, project_settings):
        super().__init__(settings, None)

        # Since this class does a large amount of manual work in the creation of it's children, it needs
        # access to a number of things from it's parent:
        # - the entire data block from the ActionDatabase
        # - A function that can add given entries to the main containing widget (QTree, QList, etc)
        # - A function that creates the possible input widgets needed (This helps avoid having those
        #   potentially numerous dependencies in here)
        self.data = data
        self.add_to_parent_func = add_to_parent_func
        self.create_input_widget_func = create_input_widget_func
        self.branches_list = branches_list

        self.main_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.project_settings = project_settings

        self.button_styles = f"""
            QToolButton {{
                background-color: rgb({self.settings.general_button_background_color});
                border-style: outset;
                border-radius: 6px;
                border-width: 1px;
                border-color: rgb({self.settings.general_button_border_color});
            }}
        """

        # Add Choice Button
        self.add_choice_button = QtWidgets.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Small_Plus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.add_choice_button.setIcon(icon)
        self.add_choice_button.setStyleSheet(self.button_styles)

        # Add input elements to the layout
        self.main_layout.addWidget(self.add_choice_button)

        # Connect Signals
        self.add_choice_button.clicked.connect(self.AddChoice)

    def Get(self):
        # Since the choice entry is so custom, we have to build the entire dict, children included to be returned
        branch_list = []
        for container_index in range(0, self.childCount()):
            choice_container = self.child(container_index)
            branch_dict = {}
            for input_index in range(0, choice_container.childCount()):
                input_widget = choice_container.child(input_index)
                # Omit the value if the global toggle is enabled
                if not input_widget.show_global_toggle or not input_widget.GetGlobal():
                    branch_dict[input_widget.name_widget.text()] = input_widget.Get()

            branch_list.append(branch_dict)
        return branch_list

    def Set(self, data) -> None:
        for choice_data in data:
            self.AddChoice(choice_data)

    def AddChoice(self, data=None):
        """
        Adds a choice entry to the choice list, filling it with input widgets for every item
        in the 'templates' dict. If 'data' is provided, use it to populate the input widgets
        """
        # Each choice is given a parent container to help organize the choice's input widgets. This is also customized
        # to have a close button which deletes the choice from the list
        new_choice_container = InputEntryContainer(self.settings, self.data)

        # Delete button
        delete_choice_button = QtWidgets.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Small_Minus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        delete_choice_button.setIcon(icon)
        delete_choice_button.setStyleSheet(self.button_styles)
        new_choice_container.input_widget = delete_choice_button
        new_choice_container.input_widget.clicked.connect(lambda delete: self.DeleteChoice(new_choice_container))
        new_choice_container.main_layout.addWidget(new_choice_container.input_widget)
        self.add_to_parent_func(new_choice_container, self)

        # Collect the current list of available branch names
        branch_names = []
        for index in range(0, self.branches_list.count()):
            branch_names.append(self.branches_list.itemWidget(self.branches_list.item(index)).Get()[0])

        # Add special options before we add the requirements from the template
        branch_dropdown = InputEntryDropdown(self.settings, branch_names, None)
        branch_dropdown.name_widget.setText("branch")
        self.add_to_parent_func(branch_dropdown, new_choice_container)
        key_input = InputEntryText(self.settings, lambda change: self.UpdateChoiceName(new_choice_container))
        key_input.name_widget.setText("key")
        self.add_to_parent_func(key_input, new_choice_container)

        if data:
            key_input.Set(data["key"])
            branch_dropdown.Set(data["branch"])
        else:
            key_input.Set(f"Choice_{self.childCount()}")

        # Add an input widget for each item in the 'template' dict
        for item in self.data["template"]:
            new_choice_detail = self.create_input_widget_func(item)
            self.add_to_parent_func(new_choice_detail, new_choice_container)
            if data:
                if item["name"] in data:
                    new_choice_detail.Set(data[item["name"]])

        # Change the entry to use the key name (Faster than using the update function since we already have the ref)
        new_choice_container.name_widget.setText(key_input.Get())

    def UpdateChoiceName(self, choice_container):
        """ Updates the name of the choic entry to use the value of the 'key' entry """
        # While we could loop through the children for the key input, it's a bit inefficient. Let's lazily
        # assume which index it is
        key_input = choice_container.child(1)
        choice_container.name_widget.setText(key_input.Get())

    def DeleteChoice(self, choice_container_widget):
        """ Deletes the chosen choice entry """
        self.removeChild(choice_container_widget)
