import sys
import os
import shutil
import subprocess
from PyQt5.QtWidgets import QMessageBox, QApplication

def check_and_install():
    """
    Checks if the app is running as a standalone exe outside of AppData.
    If so, prompts the user to install it.
    Returns True if the app should exit (because it spawned the installed version).
    """
    if not getattr(sys, 'frozen', False):
        return False # Not a pyinstaller exe
        
    exe_path = sys.executable
    appdata = os.environ.get('APPDATA')
    if not appdata:
        return False
        
    install_dir = os.path.join(appdata, 'DragonCompanion')
    installed_exe = os.path.join(install_dir, 'DragonCompanion.exe')
    
    # If we are already running from the install dir, just continue normal execution
    if os.path.normcase(exe_path) == os.path.normcase(installed_exe):
        return False
        
    # We are running from a random location (e.g. Downloads folder)
    # Ask the user if they want to install
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    reply = QMessageBox.question(None, 'Install Dragon Companion?',
                                 'Would you like to install Dragon Companion on your laptop?\n\n'
                                 'This will add it to your Start Menu so you can search for it and pin it to your taskbar.',
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                                 
    if reply == QMessageBox.No:
        return False # Just run from current location
        
    # Proceed with installation
    try:
        # Kill running instance in AppData if present to avoid file lock
        subprocess.run(["taskkill", "/F", "/IM", "DragonCompanion.exe"], 
                       creationflags=subprocess.CREATE_NO_WINDOW, 
                       stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        os.makedirs(install_dir, exist_ok=True)
        shutil.copy2(exe_path, installed_exe)
        
        # Create start menu shortcut using powershell
        start_menu = os.path.join(appdata, r'Microsoft\Windows\Start Menu\Programs')
        shortcut_path = os.path.join(start_menu, 'Dragon Companion.lnk')
        
        ps_script = f"""
$wshell = New-Object -ComObject WScript.Shell
$shortcut = $wshell.CreateShortcut('{shortcut_path}')
$shortcut.TargetPath = '{installed_exe}'
$shortcut.WorkingDirectory = '{install_dir}'
$shortcut.Save()
"""
        subprocess.run(["powershell", "-Command", ps_script], creationflags=subprocess.CREATE_NO_WINDOW)
        
        QMessageBox.information(None, 'Installation Complete',
                                'Dragon Companion has been installed!\n\n'
                                'It will now launch from the installed location. You can safely delete this original file later.')
                                
        # Launch the installed version
        subprocess.Popen([installed_exe])
        return True # Exit this instance
        
    except Exception as e:
        QMessageBox.critical(None, 'Installation Failed', f'Failed to install:\n{e}')
        return False
