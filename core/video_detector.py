import ctypes

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

class VideoDetector:
    """Detects whether the user is watching a video app on Windows.
    
    IMPORTANT: Only triggers on known video player window class names or
    well-known video streaming site titles. Does NOT trigger on generic
    fullscreen windows (e.g. maximized code editors, browsers, etc.)
    to avoid false positives that trap the pet in sleep mode.
    """
    
    # Titles must match these exact streaming site keywords in the tab title
    VIDEO_TITLE_KEYWORDS = [
        'youtube', 'netflix', 'prime video', 'hulu', 'twitch',
        'disney+', 'hotstar', 'mubi', 'crunchyroll', 'peacock',
    ]
    
    # Known video player window class names (reliable, no false positives)
    VIDEO_WINDOW_CLASSES = [
        'Qt5QWindowIcon',         # VLC / mpv on Qt
        'MediaPlayerClassicW',    # MPC-HC
        'PotPlayerMainW',         # PotPlayer
        'WMPlayerApp',            # Windows Media Player
        'MPCVideoRenderer',       # MPC-BE
        'SMPlayer',               # SMPlayer
        'Dragon Player',          # Dragon Player (Linux port)
    ]

    def __init__(self):
        self.user32 = ctypes.windll.user32

    def is_watching_video(self):
        """Returns True ONLY if the foreground window is a known video player or streaming site."""
        try:
            hwnd = self.user32.GetForegroundWindow()
            if not hwnd:
                return False

            # Get window class name
            class_name = ctypes.create_unicode_buffer(256)
            self.user32.GetClassNameW(hwnd, class_name, 256)
            cls = class_name.value

            # Match known video player window classes
            for video_cls in self.VIDEO_WINDOW_CLASSES:
                if video_cls.lower() in cls.lower():
                    return True

            # Get window title
            title_buf = ctypes.create_unicode_buffer(512)
            self.user32.GetWindowTextW(hwnd, title_buf, 512)
            window_title = title_buf.value.lower()

            # Only match streaming service titles (browser tab names include the site)
            for kw in self.VIDEO_TITLE_KEYWORDS:
                if kw in window_title:
                    return True

        except Exception:
            pass

        return False
