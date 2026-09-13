"""Exact six-source-sprite White Meme Hamster animator. No facial redraw."""
from pathlib import Path
import sys
import math
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage, QPainter, QPixmap, QColor

class WhiteHamsterAnimator:
    EXPRESSIONS = ("laugh","smile","neutral","tongue_out","halo","costume")
    FRAME_FILES = {
        "laugh": "laugh.png",
        "smile": "smile.png",
        "neutral": "neutral.png",
        "tongue_out": "tongue_out.png",
        "halo": "halo.png",
        "costume": "costume.png",
    }
    JUMP_DURATION = 1.15

    def __init__(self, state_machine, asset_dir=None):
        self.state_machine = state_machine
        self.facing = 1
        self.elapsed = 0.0
        self._last_state = None
        self.current_expression = "laugh"

        default_dir = Path(__file__).resolve().parents[1] / "assets" / "white_hamster"
        if hasattr(sys, "_MEIPASS"):
            bundled = Path(sys._MEIPASS) / "assets" / "white_hamster"
            if bundled.exists():
                default_dir = bundled
        self.asset_dir = Path(asset_dir) if asset_dir else default_dir
        self.frames = {}
        self._load_frames()

    def set_facing(self, direction):
        self.facing = 1

    def set_expression(self, expression):
        if expression not in self.EXPRESSIONS:
            raise ValueError(f"Unsupported expression: {expression}")
        self.current_expression = expression

    def get_expression(self):
        return self.current_expression

    def clear_special(self):
        self.elapsed = 0.0
        self._last_state = None
        self.current_expression = "laugh"

    def reset_animation(self):
        self.clear_special()

    def _load_frames(self):
        missing = []
        for expression, filename in self.FRAME_FILES.items():
            path = self.asset_dir / filename
            image = QImage(str(path))
            if image.isNull():
                missing.append(str(path))
                continue
            if not image.hasAlphaChannel():
                raise ValueError(
                    f"{path} has no alpha channel. Prepare a transparent sprite from "
                    "the supplied reference without altering visible artwork."
                )
            image = image.convertToFormat(QImage.Format_ARGB32)
            self.frames[expression] = QPixmap.fromImage(image, Qt.AutoColor)
        if missing:
            raise FileNotFoundError("Missing White Meme Hamster assets:\n" + "\n".join(missing))

    def update(self):
        state = self.state_machine.get_state()
        if state != self._last_state:
            self.elapsed = 0.0
            self._last_state = state
        else:
            self.elapsed += 0.025
        if state == "jump" and self.elapsed >= self.JUMP_DURATION:
            self.state_machine.force_state("idle")
            self.elapsed = 0.0
            self._last_state = "idle"

    def _draw_shadow(self, painter, y_offset):
        width = 110.0 * max(0.55, 1.0 - min(abs(y_offset) / 90.0, 0.45))
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0,0,0,30))
        painter.drawEllipse(QRectF(-width/2.0,-2.5,width,5))
        painter.restore()

    def draw(self, painter, rect):
        state = self.state_machine.get_state()
        if state in self.EXPRESSIONS:
            self.current_expression = state
        pixmap = self.frames[self.current_expression]
        y_offset = 0.0
        if state == "jump":
            p = max(0.0, min(1.0, self.elapsed / self.JUMP_DURATION))
            y_offset = -54.0 * math.sin(p * math.pi)
        elif state == "wander":
            y_offset = -2.5 * abs(math.sin(self.elapsed * 4.0))
        elif state == "sleep":
            y_offset = 2.0

        painter.save()
        painter.translate(rect.center().x(), rect.bottom())
        self._draw_shadow(painter, y_offset)
        painter.translate(0.0, y_offset)
        scaled = pixmap.scaled(148,142,Qt.KeepAspectRatio,Qt.FastTransformation)
        painter.drawPixmap(int(-scaled.width()/2), -scaled.height(), scaled)
        painter.restore()
