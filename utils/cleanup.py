import atexit
import os
import shutil
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup():
    # Specific cleanup for PyInstaller temp directories
    temp_dir = tempfile.gettempdir()
    for folder_name in os.listdir(temp_dir):
        folder_path = os.path.join(temp_dir, folder_name)
        if folder_name.startswith("_MEI"):
            try:
                shutil.rmtree(folder_path)
                logger.info(f"Removed temporary directory: {folder_path}")
            except Exception as e:
                logger.error(f"Failed to remove {folder_path}: {e}")


# Register the cleanup function to be called on exit
atexit.register(cleanup)
