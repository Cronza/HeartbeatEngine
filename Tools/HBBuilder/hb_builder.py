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
import subprocess
import os
import shutil
import time


class HBBuilder:
    @staticmethod
    def Build(logger, engine_dir: str, project_dir: str, project_name: str):
        """ Generate an executable based on the provided information and project """
        logger.Log(f"*** Starting build for: '{project_dir}'... ***")

        build_dir = f"{project_dir}/build"
        working_dir = f"{build_dir}/intermediate"
        output_dir = f"{build_dir}/output"

        # Remove the build folder if it exists, just in case the state changed significantly
        HBBuilder.Clean(logger, build_dir)

        # Use a subprocess call to invoke PyInstaller so it can fail independently
        args = f"venv/Scripts/pyinstaller.exe " \
               "--noconsole " \
               f"--workpath {working_dir} "\
               f"--distpath {output_dir} "\
               f"--specpath {working_dir} "\
               f"--add-data {project_dir}/Content;Content "\
               f"--add-data {project_dir}/Config;Config "\
               f"--add-data {engine_dir}/Content;HBEngine/Content "\
               f"--name {project_name} "\
               f"HBEngine/hb_engine.py"

        logger.Log(f"Generating executable...")
        result = subprocess.Popen(
            args,
            stdout=True,
            stderr=True
        )

        # Wait for the build to finish, then collect and report the result
        result_code = result.wait()
        if result_code == 0:
            logger.Log("*** BUILD SUCCESS ***", 2)
        else:
            logger.Log("*** BUILD FAILED ***", 4)

    @staticmethod
    def Clean(logger, project_dir: str):
        """ Deletes the active project's build directory """
        build_dir = f"{project_dir}/build"
        if os.path.exists(build_dir):
            logger.Log(f"Build folder exists - Cleaning...", 3)
            try:
                shutil.rmtree(build_dir)
                logger.Log(f"Build folder deleted!", 2)
            except Exception as exc:
                logger.Log(f"Failed to delete the build folder: {exc}", 4)
        else:
            logger.Log(f"Build folder does not exist - Skipping the clean", 3)
