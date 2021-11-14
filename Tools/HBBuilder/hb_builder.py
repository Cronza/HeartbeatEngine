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


class HBBuilder:
    @staticmethod
    def Build(logger, engine_dir: str, project_dir: str):
        """ Generate an executable based on the provided information and project """
        logger.Log(f"*** Starting build for: '{project_dir}'... ***")
        print(project_dir)
        build_dir = project_dir + "/build"
        working_dir = build_dir + "/intermediate"
        output_dir = build_dir + "/output"

        #temp_build_dir = build_dir + "/temp"

        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

        # We need to bring the engine and project together so we can bundle them up without
        # having to mess with multiple places
        #logger.Log(f"Cloning engine into: '{temp_build_dir}'...")
        #try:
        #    shutil.copytree(engine_dir, temp_build_dir)
        #except Exception as exc:
        #    logger.Log(f"Failed to copy the engine to the build directory:\n {exc}", 4)
        #    logger.Log("*** BUILD FAILED ***", 4)
        #    print(exc)

        #"""
        # Since pyinstaller can't be invoked within a script, invoke it from a subprocess
        logger.Log(f"Generating executable...")

        args = f"venv/Scripts/pyinstaller.exe "\
               f"--workpath {working_dir} "\
               f"--distpath {output_dir} "\
               f"--specpath {working_dir} "\
               f"--add-data {project_dir}/Content;Content " \
               f"--add-data {project_dir}/Config;Config " \
               f"--add-data {engine_dir}/Content;HBEngine/Content " \
               f"HBEngine/hb_engine.py"

        result = subprocess.Popen(
            args,
            stdout=True,
            stderr=True
        )
        print(result)
        logger.Log("Engine Launched - Editor temporarily unavailable")
        result.wait()

        logger.Log("Engine closed - Editor functionality resumed")
