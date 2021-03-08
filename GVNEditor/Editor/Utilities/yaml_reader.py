import yaml


class Reader:
    def ReadAll(file_path: str):
        with open(file_path) as f:
            return yaml.load(f, Loader=yaml.FullLoader)

