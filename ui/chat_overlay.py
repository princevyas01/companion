from PyQt5.QtWidgets import (
    QWidget,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QGraphicsDropShadowEffect
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ChatInputWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.resize(320, 58)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(0)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText(
            "Talk to your companion..."
        )

        self.input_field.setMinimumHeight(44)

        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(20, 22, 28, 238);
                color: #F5F5F5;
                border: 1px solid rgba(255, 255, 255, 28);
                border-radius: 15px;
                padding: 0 15px;
                selection-background-color: rgba(255, 255, 255, 50);
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 14px;
                font-weight: 500;
            }

            QLineEdit:hover {
                border: 1px solid rgba(255, 255, 255, 55);
            }

            QLineEdit:focus {
                background: rgba(24, 26, 34, 248);
                border: 1px solid rgba(255, 170, 120, 170);
            }

            QLineEdit:disabled {
                color: rgba(245, 245, 245, 100);
                background: rgba(20, 22, 28, 180);
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(26)
        shadow.setColor(QColor(0, 0, 0, 130))
        shadow.setOffset(0, 7)

        self.input_field.setGraphicsEffect(shadow)

        layout.addWidget(self.input_field)

        self.input_field.returnPressed.connect(
            self.on_submit
        )

        self.submit_callback = None

    def set_callback(self, callback):
        self.submit_callback = callback

    def show_overlay(self, pet_x, pet_y, pet_width):
        target_x = (
            pet_x +
            (pet_width // 2) -
            (self.width() // 2)
        )

        target_y = pet_y + 100

        self.move(
            target_x,
            target_y
        )

        self.show()
        self.activateWindow()

        self.input_field.clear()
        self.input_field.setFocus()

    def on_submit(self):
        text = self.input_field.text().strip()

        self.hide()

        if text and self.submit_callback:
            self.submit_callback(text)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)
