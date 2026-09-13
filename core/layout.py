from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect, QPoint


class LayoutManager:
    """Screen-aware layout engine for the desktop companion."""

    def __init__(self, window):
        self.window = window
        self.dragon_size = (150, 160)
        self.padding = 15
        self._screen_rect = None
        self._refresh_screen()

    def _refresh_screen(self):
        screen = QApplication.screenAt(self.window.geometry().center())

        if not screen:
            screen = QApplication.primaryScreen()

        self._screen_rect = screen.availableGeometry()

    def update(self):
        self._refresh_screen()

    def get_dragon_rect(self):
        win_w = self.window.width()
        win_h = self.window.height()
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

        x = max(
            screen.left() - win_w + 60,
            min(global_pos.x(), screen.right() - 60),
        )

        y = max(
            screen.top(),
            min(global_pos.y(), screen.bottom() - 60),
        )

        return QPoint(x, y)

    def get_wander_target(self):
        import random

        screen = self._screen_rect
        win_w = self.window.width()
        win_h = self.window.height()

        min_x = screen.left() + 20
        max_x = max(min_x, screen.right() - win_w - 20)

        min_y = screen.top() + 20
        max_y = max(min_y, screen.bottom() - win_h - 20)

        return QPoint(
            random.randint(min_x, max_x),
            random.randint(min_y, max_y),
        )

    def get_bubble_rect(self, text_size):
        dragon_rect = self.get_dragon_rect()

        is_white_hamster = (
            getattr(self.window, "current_character", "")
            == "white_hamster"
        )

        if is_white_hamster:
            max_width = 200
            max_height = 62
            horizontal_padding = 18
            vertical_padding = 16
            gap = 18
        else:
            max_width = 220
            max_height = 72
            horizontal_padding = self.padding * 2
            vertical_padding = self.padding * 2
            gap = 15

        bw = min(
            max(130, text_size.width() + horizontal_padding),
            max_width,
        )

        bh = min(
            max(40, text_size.height() + vertical_padding),
            max_height,
        )

        bx = dragon_rect.center().x() - bw // 2
        by = dragon_rect.top() - bh - gap

        bx = max(
            8,
            min(
                bx,
                self.window.width() - bw - 8,
            ),
        )

        by = max(8, by)

        return QRect(
            int(bx),
            int(by),
            int(bw),
            int(bh),
        )
