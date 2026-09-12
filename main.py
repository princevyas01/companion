import sys
import os

# Ensure the working directory is always the script directory or MEIPASS
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.chibi_window import DragonCompanionWindow
from core.installer import check_and_install
from core.single_instance import notify_existing_instance, SingleInstanceServer

def main():
    app = QApplication(sys.argv)
    
    if check_and_install():
        sys.exit(0)

    # Enforce Single Instance: If another instance is running, tell it to show Control Panel and exit
    if notify_existing_instance():
        sys.exit(0)
        
    app.setQuitOnLastWindowClosed(False)
    
    window = DragonCompanionWindow()
    # Keep pet stopped initially, show control panel
    window.stop_pet()
    window.show_control_panel()
    
    # Start IPC server for single instance control
    ipc_server = SingleInstanceServer(window)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
