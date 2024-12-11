import yaml

""" 
A custom YAML tag designed to create a 'Connection' object that denotes when action data parameters are assigned to 
variables as opposed to having normal values.
"""


class Connection:
    def __init__(self, category, variable, source):
        self.category = category
        self.variable = variable
        self.source = source


""" Define the YAML -> Python representation"""
def connection_constructor(loader: yaml.FullLoader, node: yaml.nodes.MappingNode):
    return Connection(**loader.construct_mapping(node))


""" Define the Python -> YAML representation """
def connection_representer(dumper: yaml.SafeDumper, connection: Connection) -> yaml.nodes.MappingNode:
    return dumper.represent_mapping("!Connection", {
        "category": connection.category,
        "variable": connection.variable,
        "source": connection.source,
    })
