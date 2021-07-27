import yaml


class Reader:
    def ReadAll(file_path: str):
        """ Given a file path, read in the contents of the file and return them """
        with open(file_path) as f:
            return yaml.load(f, Loader=yaml.FullLoader)

class Writer:
    def WriteFile(data: dict, file_path: str, metadata: str = ""):
        """
        Given a dict, write it as a .yaml file to the target location. If 'metadata' is provided, prepend that
        to the beginning of the file (Useful for comments)
        """
        with open(file_path, 'w') as file:
            if metadata:
                file.write(metadata + "\n\n")

            # By default, yaml dumps data in a 'sorted order' instead of by 'insertion order'. As per this:
            # https://github.com/yaml/pyyaml/issues/110, you can specify 'sort_keys=False' to force the dump to
            # skip the sorting and use insertion order
            return yaml.dump(data, file, sort_keys=False)

