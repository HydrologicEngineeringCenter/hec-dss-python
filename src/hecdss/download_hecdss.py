"""Helper module to retrieve the binary libraries"""

from pathlib import Path
import shutil
import requests
import zipfile
import os


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
    print(url)
    os.makedirs(destination_dir, exist_ok=True)
    response = requests.get(zip_url, timeout=300)
    if response.status_code == 200:
        zip_file_path = os.path.join(destination_dir, zip_file)
        with open(zip_file_path, "wb") as zip_file:
            zip_file.write(response.content)
        print("Zip file downloaded successfully.")

        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(destination_dir)
        print(f"Contents extracted successfully to.'{destination_dir}'")
        os.remove(zip_file_path)
    else:
        print(f"Failed to download zip file. Status code: {response.status_code}")

base_url = "https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hecdss/"
version = "7-JA-4"

destination_dir = Path(__file__).parent.joinpath("lib")
zip_url = f"{base_url}{version}-win-x86_64/hecdss-{version}-win-x86_64.zip"
download_and_unzip(zip_url, f"hecdss-{version}-win-x86_64.zip", destination_dir)

zip_url = f"{base_url}{version}-linux-x86_64/hecdss-{version}-linux-x86_64.zip"
download_and_unzip(zip_url, f"hecdss-{version}-linux-x86_64.zip", destination_dir)
