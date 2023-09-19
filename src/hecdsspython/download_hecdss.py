import requests
import zipfile
import os


def downloadAndUnzip(url,zipFile,destination_dir):
    print(url)
    os.makedirs(destination_dir, exist_ok=True)
    response = requests.get(zip_url)
    if response.status_code == 200:
        zip_file_path = os.path.join(destination_dir, zipFile)
        with open(zip_file_path, "wb") as zip_file:
            zip_file.write(response.content)
        print("Zip file downloaded successfully.")

        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(destination_dir)
        print("Contents extracted successfully.")
    else:
        print(f"Failed to download zip file. Status code: {response.status_code}")


destination_dir = "lib"
zip_url = "https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hecdss/7-IS-win-x86_64/hecdss-7-IS-win-x86_64.zip"
downloadAndUnzip(zip_url,"hecdss-7-IS-win-x86_64.zip",destination_dir)
zip_url = "https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hecdss/7-IS-linux-x86_64/hecdss-7-IS-linux-x86_64.zip"
downloadAndUnzip(zip_url,"hecdss-7-IS-linux-x86_64.zip",destination_dir)