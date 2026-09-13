from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics, QPainterPath
from PyQt5.QtCore import Qt, QRect, QRectF, QPointF


class SpeechBubble:
    def __init__(self, window):
        self.window = window
        self.text = ""
        self.font = QFont("Segoe UI", 10, QFont.DemiBold)
        self.metrics = QFontMetrics(self.font)
        self.visible = False
        self.show_caret = False

        # Visual-only state.
        self._visual_phase = 0.0
        self._caret_alpha = 1.0

    def set_text(self, text):
        self.text = text

    def set_caret(self, visible):
        self.show_caret = visible

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
        self.text = ""
        self.show_caret = False
        self._visual_phase = 0.0

    def is_visible(self):
        return self.visible

    def get_text_size(self):
        if not self.text and not self.show_caret:
            return self.metrics.boundingRect(" ")

        display_text = self.text + ("|" if self.show_caret else "")

        flags = Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop

        return self.metrics.boundingRect(
            0,
            0,
            172,
            56,
            flags,
            display_text
        )

    def draw(self, painter: QPainter, rect: QRect):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # -------------------------------------------------
        # Soft shadow
        # -------------------------------------------------

        shadow_rect = QRectF(rect).adjusted(
            2,
            4,
            2,
            6
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 35))

        painter.drawRoundedRect(
            shadow_rect,
            14,
            14
        )

        # -------------------------------------------------
        # Bubble body
        # -------------------------------------------------

        bubble_rect = QRectF(rect)

        painter.setPen(
            QPen(
                QColor(55, 45, 42, 210),
                1.4
            )
        )

        painter.setBrush(
            QBrush(
                QColor(255, 252, 247, 248)
            )
        )

        painter.drawRoundedRect(
            bubble_rect,
            14,
            14
        )

        # -------------------------------------------------
        # Tiny top highlight
        # -------------------------------------------------

        highlight_rect = QRectF(
            bubble_rect.left() + 10,
            bubble_rect.top() + 6,
            bubble_rect.width() - 20,
            2
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 85))
        painter.drawRoundedRect(
            highlight_rect,
            1,
            1
        )

        # -------------------------------------------------
        # Tail
        # -------------------------------------------------

        cx = bubble_rect.center().x()
        bottom = bubble_rect.bottom()

        tail = QPainterPath()
        tail.moveTo(
            QPointF(cx - 6, bottom - 1)
        )
        tail.lineTo(
            QPointF(cx, bottom + 7)
        )
        tail.lineTo(
            QPointF(cx + 6, bottom - 1)
        )
        tail.closeSubpath()

        painter.setPen(
            QPen(
                QColor(55, 45, 42, 210),
                1.1
            )
        )

        painter.setBrush(
            QColor(255, 252, 247, 248)
        )

        painter.drawPath(tail)

        # -------------------------------------------------
        # Text
        # -------------------------------------------------

        painter.setFont(self.font)
        painter.setPen(
            QColor(48, 39, 37)
        )

        text_rect = QRect(
            int(bubble_rect.left() + 10),
            int(bubble_rect.top() + 7),
            int(bubble_rect.width() - 20),
            int(bubble_rect.height() - 14)
        )

        display_text = self.text

        if self.show_caret:
            display_text += "|"

        painter.drawText(
            text_rect,
            Qt.TextWordWrap |
            Qt.AlignLeft |
            Qt.AlignTop,
            display_text
        )

        painter.restore()
