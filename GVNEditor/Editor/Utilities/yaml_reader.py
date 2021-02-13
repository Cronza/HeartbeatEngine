import yaml

class Reader:
    def ReadAll(file_path):
        with open(file_path) as f:
            return yaml.load(f, Loader=yaml.FullLoader)

