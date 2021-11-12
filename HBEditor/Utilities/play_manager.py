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
from PyQt5.QtWidgets import QMessageBox


class PlayManager:
    """
    A manager for operations relating to launch the HBEngine. This class requires that the HBEngine be available
    alongside the HBEditor so the subprocess call works correctly
    """

    def Play(self, parent, logger,  project_path):
        logger.Log("Launching engine...")
        try:
            # Launch the engine, and wait until it shuts down before continuing
            result = subprocess.Popen(
                [
                    f"venv/Scripts/python",
                    "HBEngine/hb_engine.py",
                    project_path
                ],
                stdout=True,
                stderr=True            )
            logger.Log("Engine Launched - Editor temporarily unavailable")
            result.wait()

            logger.Log("Engine closed - Editor functionality resumed")

        except Exception as exc:
            QMessageBox.about(
                parent,
                "Unable to Launch Engine",
                "The HBEngine could not be launched.\n\n"
                "Please make sure the engine is available alongside the editor, or that you're\n"
                "PYTHONPATH is configured correctly to include the engine."
            )
            print(exc)

