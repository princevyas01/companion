import os
import sys
import winreg

APP_NAME = "BabyDragonDesktopPet"

def enable_autostart():
    try:
        # Use pythonw.exe to run without a console window
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        script_path = os.path.abspath("c:\\Pet\\main.py")
        
        # Command to run on startup
        cmd = f'"{python_exe}" "{script_path}"'
        
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS) as registry_key:
            winreg.SetValueEx(registry_key, APP_NAME, 0, winreg.REG_SZ, cmd)
        return True
    except Exception as e:
        print(f"Failed to enable autostart: {e}")
        return False

def disable_autostart():
    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS) as registry_key:
            winreg.DeleteValue(registry_key, APP_NAME)
        return True
    except FileNotFoundError:
        pass # Already disabled
    except Exception as e:
        print(f"Failed to disable autostart: {e}")
        return False

def is_autostart_enabled():
    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_READ) as registry_key:
            winreg.QueryValueEx(registry_key, APP_NAME)
            return True
    except FileNotFoundError:
        return False
    except Exception:
        return False
