import subprocess
from PyQt5.QtWidgets import QMessageBox


class PlayManager:
    """
    A manager for operations relating to launch the GVNEngine. This class requires that the GVNEngine be available
    alongside the GVNEditor so the subprocess call works correctly
    """

    def Play(self, parent, logger,  project_path):
        logger.Log("Launching engine...")
        try:
            # Launch the engine, and wait until it shuts down before continuing
            result = subprocess.Popen("GVNEngine/venv/Scripts/python GVNEngine/gvn_engine.py", stdout=True, stderr=True)
            logger.Log("Engine Launched - Editor temporarily unavailable")
            result.wait()


            logger.Log("Engine closed - Editor functionality resumed")
            print(result)
        except Exception as exc:
            QMessageBox.about(
                parent,
                "Unable to Launch Engine",
                "The GVNEngine could not be launched.\n\n"
                "Please make sure the engine is available alongside the editor, or that you're\n"
                "PYTHONPATH is configured correctly to include the engine."
            )
            print(exc)

