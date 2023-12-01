import shutil
import tempfile
import os

class TestFileManager:
    def __init__(self, test_data_dir):
        self.test_data_dir = test_data_dir
        self.temp_dir = tempfile.mkdtemp()

    def get_copy(self, filename):
        """Copies a file to the temporary directory."""
        src = os.path.join(self.test_data_dir, filename)
        if not os.path.isfile(src):
            raise FileNotFoundError(f"No such file: {src}")

        dest = os.path.join(self.temp_dir, filename)
        shutil.copy(src, dest)
        return dest

    def cleanup(self):
        """Deletes the temporary directory and its contents."""
        #shutil.rmtree(self.temp_dir)
