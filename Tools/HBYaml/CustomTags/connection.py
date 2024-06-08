import yaml

""" 
A custom YAML tag designed to create a 'Connection' object that denotes when action data parameters are assigned to 
variables as opposed to having normal values.
"""


class Connection:
    def __init__(self, variable):
        self.variable = variable


""" Define the YAML -> Python representation"""
def connection_constructor(loader: yaml.FullLoader, node: yaml.nodes.ScalarNode):
    return Connection(loader.construct_scalar(node))


""" Define the Python -> YAML representation """
def connection_representer(dumper: yaml.SafeDumper, connection: Connection) -> yaml.nodes.ScalarNode:
    return dumper.represent_scalar('!Connection', connection.variable)
