import os
import zipfile
import shutil

ROOT_DIR = r"d:\Downloads\lnk"
MACOSX_DIR = os.path.join(ROOT_DIR, "macOSx")
ZIP_PATH = os.path.join(ROOT_DIR, "macOSx.zip")

print("Zipping macOSx...")
def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, os.path.dirname(path))
            ziph.write(file_path, arcname)

# Remove old zip if exists
if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)

with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir(MACOSX_DIR, zipf)

print(f"Created {ZIP_PATH} successfully.")
print("Upload this file to your GitHub Releases.")

