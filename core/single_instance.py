import sys
import ctypes
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

SERVER_NAME = "DragonCompanionSingleInstanceLock_v1"
MUTEX_NAME = "DragonCompanion_GlobalLock_v1"
_mutex_handle = None

def notify_existing_instance():
    """
    Attempts to connect to an existing running instance using an atomic Windows Named Mutex
    and QLocalSocket. Returns True if an instance is already running so the duplicate exits.
    """
    global _mutex_handle
    is_duplicate = False
    try:
        kernel32 = ctypes.windll.kernel32
        _mutex_handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            is_duplicate = True
    except Exception:
        pass

    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if socket.waitForConnected(800):
        socket.write(b"SHOW_CONTROL_PANEL")
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        return True

    return is_duplicate

class SingleInstanceServer(QLocalServer):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.removeServer(SERVER_NAME)
        self.listen(SERVER_NAME)
        self.newConnection.connect(self.handle_connection)
        
    def handle_connection(self):
        socket = self.nextPendingConnection()
        if socket:
            socket.waitForReadyRead(500)
            msg = socket.readAll().data().decode('utf-8', errors='ignore')
            if msg == "SHOW_CONTROL_PANEL":
                self.main_window.show_control_panel()
                if getattr(self.main_window, 'control_panel', None):
                    self.main_window.control_panel.show()
                    self.main_window.control_panel.raise_()
                    self.main_window.control_panel.activateWindow()
            socket.disconnectFromServer()
