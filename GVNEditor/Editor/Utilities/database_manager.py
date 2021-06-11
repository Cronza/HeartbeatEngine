class DBManager:
    def ConvertDialogueFileToEngineFormat(self, action_data: dict):
        """
        Given a full dict of dialogue file data (branches and all), convert it to a format used by the engine.
        Return the converted dict
        """
        converted_dict = {}

        for branch in action_data.items():
            branch_name = branch[0]

            action_list = []
            for editor_action in branch[1]:
                # Get the action name
                converted_action = {'action': editor_action['action_name']}

                # Collect a converted dict of all requirements for this action
                converted_action.update(self.ConvertActionRequirementsToEngineFormat(editor_action))

                # Add it to the final list of actions
                action_list.append(converted_action)

            # Add the list of actions under the target branch
            converted_dict[branch_name] = action_list

        return converted_dict

    def ConvertActionRequirementsToEngineFormat(self, editor_action_data, has_parent=None):
        """ Given an editor action requirements / children data dict, convert it to a format usable by the engine"""
        converted_action = {}

        term = "requirements"
        if has_parent:
            term = "children"

        for requirement in editor_action_data[term]:
            if requirement["type"] != "container":

                # Exclude requirements that are pointing to a global setting. The engine will take care of this at
                # runtime since any global value stored in a file will become outdated as soon as the global setting
                # is changed
                if "global" in requirement:
                    if not requirement["global"]["active"]:
                        converted_action[requirement["name"]] = requirement["cache"]
                else:
                    converted_action[requirement["name"]] = requirement["cache"]
            else:
                converted_action[requirement["name"]] = self.ConvertActionRequirementsToEngineFormat(requirement, True)

        return converted_action
