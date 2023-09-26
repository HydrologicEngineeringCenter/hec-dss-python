"""Helper module to retrieve the binary libraries"""

from pathlib import Path
import shutil
import sys
import tempfile
import zipfile
import os
import hecdss
import urllib.request as request


def download_and_unzip(url, destination_dir):
    """Retrieves a compressed archive from the URL and extracts it in the destination dir.

    Parameters
    ----------
    url : str
        URL to the archive.
    destination_dir :
        Path to the local directory where the archive content is extracted to.

    """
    print(url)
    os.makedirs(destination_dir, exist_ok=True)
    with request.urlopen(url) as response:
        if response.status == 200:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                shutil.copyfileobj(response, tmp_file)
                with zipfile.ZipFile(tmp_file) as zip_ref:
                    zip_ref.extractall(destination_dir)
            print(f"Contents extracted successfully in {destination_dir!r}")

        else:
            print(f"Failed to download zip file. Status code: {response.status_code}")


def run():
    """Downloads and extracts the binary shared library into the current python environment."""
    destination_dir = Path(hecdss.__file__).parent.joinpath("lib")
    platform = sys.platform
    print(f"Installing shared library for {platform!r} OS")
    if platform == "linux" or platform == "darwin":
        zip_url = "https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hecdss/7-IS-linux-x86_64/hecdss-7-IS-linux-x86_64.zip"
        download_and_unzip(zip_url, destination_dir)
    elif platform == "win32":
        zip_url = "https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hecdss/7-IS-win-x86_64/hecdss-7-IS-win-x86_64.zip"
        download_and_unzip(zip_url, destination_dir)


if __name__ == "__main__":
    run()
