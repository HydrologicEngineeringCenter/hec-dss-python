"""Helper module to retrieve the binary libraries"""

import logging
from pathlib import Path
import shutil
import requests
import zipfile
import os

# Get logger for this module
logger = logging.getLogger(__name__)


def download_and_unzip(url, zip_file, destination_dir):
    """Retrieves a compressed archive from the URL and extracts it in the destination dir.

    Parameters
    ----------
    url : str
        URL to the archive.
    zip_file : str
        Name of the local target archive.
    destination_dir :
        Path to the local directory where the archive content is extracted to.
    """
    print(url)  # Keep for user feedback during download
    logger.info("Downloading from URL: %s", url)
    os.makedirs(destination_dir, exist_ok=True)
    response = requests.get(zip_url, timeout=300)
    if response.status_code == 200:
        zip_file_path = os.path.join(destination_dir, zip_file)
        with open(zip_file_path, "wb") as zip_file:
            zip_file.write(response.content)
        print("Zip file downloaded successfully.")  # Keep for user feedback
        logger.info("Zip file downloaded successfully")

        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(destination_dir)
        print(f"Contents extracted successfully to.'{destination_dir}'")  # Keep for user feedback
        logger.info("Contents extracted successfully to '%s'", destination_dir)
        os.remove(zip_file_path)
    else:
        error_msg = f"Failed to download zip file. Status code: {response.status_code}"
        print(error_msg)  # Keep for user feedback
        logger.error(error_msg)

base_url = "https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hecdss/"
version = "7-IU-16"

destination_dir = Path(__file__).parent.joinpath("lib")
zip_url = f"{base_url}{version}-win-x86_64/hecdss-{version}-win-x86_64.zip"
download_and_unzip(zip_url, f"hecdss-{version}-win-x86_64.zip", destination_dir)

zip_url = f"{base_url}{version}-linux-x86_64/hecdss-{version}-linux-x86_64.zip"
download_and_unzip(zip_url, f"hecdss-{version}-linux-x86_64.zip", destination_dir)
