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

        build_dir = project_dir + "/.build"
        temp_build_dir = build_dir + "/temp"
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

        # We need to bring the engine and project together so we can bundle them up without
        # having to mess with multiple places
        logger.Log(f"Cloning engine into: '{temp_build_dir}'...")
        try:
            shutil.copytree(engine_dir, temp_build_dir)
        except Exception as exc:
            logger.Log(f"Failed to copy the engine to the build directory:\n {exc}", 4)
            logger.Log("*** BUILD FAILED ***", 4)
            print(exc)

        """
        # Since pyinstaller can't be invoked within a script, invoke it from a subprocess
        result = subprocess.Popen(
            [
                f"venv/Scripts/python -m PyInstaller --noconsole HBEngine/hb_engine.py",
                project_dir
            ],
            stdout=True,
            stderr=True)
        logger.Log("Engine Launched - Editor temporarily unavailable")
        result.wait()

        logger.Log("Engine closed - Editor functionality resumed")
        #python -m PyInstaller --noconsole --name WorkLogger F:\KivyApps\WorkLogger\main.py")
        """



