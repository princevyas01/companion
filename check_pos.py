import win32gui

def get_pet_window():
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            # PyQt5 windows usually have class name starting with QWidget or similar
            # Our app doesn't set a title, so title might be empty. But we can check process.
            pass

# simpler approach, check via wmic
