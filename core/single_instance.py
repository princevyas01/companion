from PyQt5.QtNetwork import QLocalServer, QLocalSocket
import sys

SERVER_NAME = "DragonCompanionSingleInstanceLock_v1"

def notify_existing_instance():
    """
    Attempts to connect to an existing running instance.
    If successful, asks it to show its control panel and returns True.
    """
    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if socket.waitForConnected(500):
        socket.write(b"SHOW_CONTROL_PANEL")
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        return True
    return False

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
