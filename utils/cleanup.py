import atexit
import os
import shutil
import tempfile


def cleanup():
    # Specific cleanup for PyInstaller temp directories
    temp_dir = tempfile.gettempdir()
    for folder_name in os.listdir(temp_dir):
        folder_path = os.path.join(temp_dir, folder_name)
        if folder_name.startswith("_MEI"):
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                print(f"Failed to remove {folder_path}: {e}")


# Register the cleanup function to be called on exit
atexit.register(cleanup)
