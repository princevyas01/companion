from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect, QPoint

class LayoutManager:
    """Screen-aware layout engine. Clamps dragon and bubble inside safe bounds."""
    
    def __init__(self, window):
        self.window = window
        self.dragon_size = (150, 160)
        self.padding = 15
        self._screen_rect = None
        self._refresh_screen()

    def _refresh_screen(self):
        # Use the screen the window is currently occupying
        screen = QApplication.screenAt(self.window.geometry().center())
        if not screen:
            screen = QApplication.primaryScreen()
        self._screen_rect = screen.availableGeometry()

    def update(self):
        self._refresh_screen()

    def get_dragon_rect(self):
        win_w = self.window.width()
        win_h = self.window.height()
        if getattr(self.window, "current_character", "") == "white_hamster":
            # White Meme Hamster is rendered as a ~300px-tall sprite. The
            # generic 150x160 rect caused the speech bubble to be positioned
            # in the middle of the enlarged sprite, creating overlap.
            dw, dh = 220, 300
        else:
            dw, dh = self.dragon_size

        return QRect(
            (win_w - dw) // 2,
            win_h - dh - 10,
            dw,
            dh,
        )

    def clamp_window_pos(self, global_pos):
        screen = self._screen_rect
        win_w = self.window.width()
        win_h = self.window.height()
        
        x = max(screen.left() - win_w + 60, min(global_pos.x(), screen.right() - 60))
        y = max(screen.top(), min(global_pos.y(), screen.bottom() - 60))
        
        return QPoint(x, y)

    def get_wander_target(self):
        """Returns a random safe position for the dragon to wander to."""
        import random
        screen = self._screen_rect
        win_w = self.window.width()
        win_h = self.window.height()
        
        x = random.randint(screen.left() + 20, screen.right() - win_w - 20)
        y = random.randint(screen.top() + 20, screen.bottom() - win_h - 20)
        
        return QPoint(x, y)

    def get_bubble_rect(self, text_size):
        dragon_rect = self.get_dragon_rect()
        is_white = getattr(self.window, "current_character", "") == "white_hamster"
        if is_white:
            max_width, pad_x, pad_y, gap, max_height = 178, 10, 7, 18, 54
        else:
            max_width, pad_x, pad_y, gap, max_height = 220, self.padding, self.padding, 18, 90

        bw = min(text_size.width() + pad_x * 2, max_width)
        bh = min(max(text_size.height() + pad_y * 2, 32), max_height)
        bx = dragon_rect.center().x() - bw // 2
        by = dragon_rect.top() - bh - gap
        bx = max(5, min(bx, self.window.width() - bw - 5))

        if by < 5:
            by = dragon_rect.bottom() + gap
            if by + bh > self.window.height() - 5:
                by = max(5, dragon_rect.top() - bh - gap)

        return QRect(int(bx), int(by), int(bw), int(bh))
