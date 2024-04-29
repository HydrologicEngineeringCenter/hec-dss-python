import shutil
import tempfile
import os
import uuid

class TestFileManager:
    """
    This TestFileManager is used to create uniquely named copies of test input files
    in a unique temporary directory.

    This ensures that file operations in tests do not interfere with the original files 
    and provides a clean, isolated environment for each test.
    """

    def __init__(self, test_data_dir):
        self.test_data_dir = test_data_dir
        self.temp_dir = tempfile.mkdtemp()

    def get_copy(self, filename):
        """Copies a file to the temporary directory."""
        src = os.path.join(self.test_data_dir, filename)
        if not os.path.isfile(src):
            raise FileNotFoundError(f"No such file: {src}")

        basename, extension = os.path.splitext(filename)
        unique_id = uuid.uuid4()

        # Creating a unique filename
        unique_filename = f"{basename}_{unique_id}{extension}"
        dest = os.path.join(self.temp_dir, unique_filename)

        shutil.copy(src, dest)
        return dest

    def cleanup(self):
        """Deletes the temporary directory and its contents."""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            pass

