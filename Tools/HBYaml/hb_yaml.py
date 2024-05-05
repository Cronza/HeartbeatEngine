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
import yaml
from Tools.HBYaml.CustomTags import connection


class Reader:
    @staticmethod
    def ReadAll(file_path: str):
        """
        Given a file path, read in the contents of the file and return them
        """
        loader = yaml.FullLoader

        # Add custom constructors that may be needed
        loader.add_constructor("!Connection", connection.connection_constructor)

        with open(file_path) as f:
            return yaml.load(f, Loader=loader)


class Writer:
    @staticmethod
    def WriteFile(data: dict, file_path: str, metadata: str = ""):
        """
        Given a dict, write it to the provided file path. If 'metadata' is provided, prepend that to the beginning
        of the file (Useful for comments)
        """
        with open(file_path, 'w') as file:
            if metadata:
                file.write(metadata + "\n\n")

            dumper = yaml.SafeDumper

            # Add custom representors that may be needed
            dumper.add_representer(connection.Connection, connection.connection_representer)

            # By default, yaml dumps data in a 'sorted order' instead of by 'insertion order'. As per this:
            # https://github.com/yaml/pyyaml/issues/110, you can specify 'sort_keys=False' to force the dump to
            # skip the sorting and use insertion order
            return yaml.dump(data, file, sort_keys=False, Dumper=dumper)

