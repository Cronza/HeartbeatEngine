import yaml


class Reader:
    def ReadAll(file_path: str):
        with open(file_path) as f:
            return yaml.load(f, Loader=yaml.FullLoader)

class Writer:
    def WriteFile(self, data, write_loc, file_name):
        """ Given a dict, write it as a .yaml file to the target location"""


