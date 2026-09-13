"""
Exact reference-sprite renderer for the user's White Meme Hamster.

The hamster artwork is NEVER redrawn procedurally.
The six supplied source images remain the only visual source of truth.
All animation happens by transforming the complete source sprite.
"""

import math
import sys
from collections import deque
from pathlib import Path

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage, QPainter, QPixmap, QColor


class WhiteHamsterAnimator:
    """Reference sprite animator with autonomous expression and motion."""

    ONE_SHOT_DURATIONS = {
        "laugh": 1.80,
        "smile": 1.50,
        "neutral": 1.50,
        "tongue_out": 1.80,
        "halo": 2.80,
        "costume": 4.50,
        "jump": 1.15,
        "celebrate": 1.80,
        "react_click": 1.20,
    }

    FRAME_FILES = {
        "laugh": "laugh.png",
        "smile": "smile.png",
        "neutral": "neutral.png",
        "tongue_out": "tongue_out.png",
        "halo": "halo.png",
        "costume": "costume.png",
    }

    EXPRESSION_SEQUENCE = (
        "laugh",
        "smile",
        "neutral",
        "tongue_out",
        "halo",
        "costume",
    )
    EXPRESSIONS = EXPRESSION_SEQUENCE

    AUTO_EXPRESSION_INTERVAL = 7.0
    AUTO_JUMP_INTERVAL = 11.0
    AUTO_JUMP_DURATION = 1.15
    JUMP_DURATION = 1.15

    def __init__(self, state_machine, asset_dir=None):
        self.state_machine = state_machine
        self.facing = 1
        self.elapsed = 0.0
        self._last_state = None

        self.auto_elapsed = 0.0
        self.auto_expression_elapsed = 0.0
        self.auto_jump_countdown = self.AUTO_JUMP_INTERVAL
        self.auto_jump_active_time = 0.0
        self.auto_expression_index = 0
        self.auto_expression = "laugh"
        self.manual_action_lock = 0.0

        default_dir = (
            Path(__file__).resolve().parents[1]
            / "assets"
            / "white_hamster"
        )

        if hasattr(sys, "_MEIPASS"):
            meipass_dir = Path(sys._MEIPASS) / "assets" / "white_hamster"
            if meipass_dir.exists():
                default_dir = meipass_dir

        self.asset_dir = Path(asset_dir) if asset_dir else default_dir

        self.frames = {}
        self._load_frames()

    def set_facing(self, direction):
        self.facing = 1 if direction >= 0 else -1

    def set_expression(self, expression):
        if expression in self.EXPRESSION_SEQUENCE:
            self.auto_expression = expression
            self.auto_expression_index = self.EXPRESSION_SEQUENCE.index(expression)
            self.auto_expression_elapsed = 0.0

    def get_expression(self):
        state = self.state_machine.get_state()
        return self._expression_for_state(state)

    @property
    def current_expression(self):
        return self.get_expression()

    @current_expression.setter
    def current_expression(self, expr):
        self.set_expression(expr)

    def clear_special(self):
        self.elapsed = 0.0
        self._last_state = None
        self.manual_action_lock = 0.0

    def reset_animation(self):
        self.elapsed = 0.0
        self._last_state = None
        self.auto_elapsed = 0.0
        self.auto_expression_elapsed = 0.0
        self.auto_jump_countdown = self.AUTO_JUMP_INTERVAL
        self.auto_jump_active_time = 0.0
        self.auto_expression_index = 0
        self.auto_expression = "laugh"
        self.manual_action_lock = 0.0

    @staticmethod
    def _near_white(pixel: QColor):
        return (
            pixel.alpha() > 0
            and pixel.red() >= 242
            and pixel.green() >= 242
            and pixel.blue() >= 242
        )

    @classmethod
    def _remove_connected_white_background(cls, image: QImage):
        image = image.convertToFormat(QImage.Format_ARGB32)

        w = image.width()
        h = image.height()

        if w <= 0 or h <= 0:
            return image

        removable = bytearray(w * h)
        queue = deque()

        def idx(x, y):
            return y * w + x

        def visit(x, y):
            i = idx(x, y)

            if removable[i]:
                return

            if not cls._near_white(image.pixelColor(x, y)):
                return

            removable[i] = 1
            queue.append((x, y))

        for x in range(w):
            visit(x, 0)
            if h > 1:
                visit(x, h - 1)

        for y in range(h):
            visit(0, y)
            if w > 1:
                visit(w - 1, y)

        while queue:
            x, y = queue.popleft()

            if x > 0:
                visit(x - 1, y)
            if x + 1 < w:
                visit(x + 1, y)
            if y > 0:
                visit(x, y - 1)
            if y + 1 < h:
                visit(x, y + 1)

        for y in range(h):
            for x in range(w):
                if removable[idx(x, y)]:
                    image.setPixelColor(x, y, QColor(0, 0, 0, 0))

        left = w
        top = h
        right = -1
        bottom = -1

        for y in range(h):
            for x in range(w):
                if image.pixelColor(x, y).alpha() > 0:
                    left = min(left, x)
                    top = min(top, y)
                    right = max(right, x)
                    bottom = max(bottom, y)

        if right < left or bottom < top:
            return image

        return image.copy(
            left,
            top,
            right - left + 1,
            bottom - top + 1,
        )

    def _load_frames(self):
        missing = []

        for state, filename in self.FRAME_FILES.items():
            path = self.asset_dir / filename
            image = QImage(str(path))

            if image.isNull():
                missing.append(str(path))
                continue

            cleaned = self._remove_connected_white_background(image)

            self.frames[state] = QPixmap.fromImage(
                cleaned,
                Qt.AutoColor,
            )

        if missing:
            raise FileNotFoundError(
                "White Meme Hamster reference assets missing:\n"
                + "\n".join(missing)
            )

    def _expression_for_state(self, state):
        if state == "laugh":
            return "laugh"
        if state == "smile":
            return "smile"
        if state == "neutral":
            return "neutral"
        if state == "tongue_out":
            return "tongue_out"
        if state == "halo":
            return "halo"
        if state == "costume":
            return "costume"
        if state in ("jump", "celebrate", "react_click"):
            return self.auto_expression
        return self.auto_expression

    def update(self):
        state = self.state_machine.get_state()
        dt = 0.025

        if state != self._last_state:
            self.elapsed = 0.0
            self._last_state = state

            if state in {
                "laugh",
                "smile",
                "neutral",
                "tongue_out",
                "halo",
                "costume",
                "jump",
                "celebrate",
                "react_click",
            }:
                self.manual_action_lock = self.ONE_SHOT_DURATIONS.get(
                    state,
                    1.0,
                )
        else:
            self.elapsed += dt

        if self.manual_action_lock > 0.0:
            self.manual_action_lock = max(
                0.0,
                self.manual_action_lock - dt,
            )

        duration = self.ONE_SHOT_DURATIONS.get(state)

        if duration is not None and self.elapsed >= duration:
            self.state_machine.force_state("idle")
            self.elapsed = 0.0
            self._last_state = "idle"
            self.manual_action_lock = 0.0

        self.auto_elapsed += dt

        autonomous_allowed = (
            self.manual_action_lock <= 0.0
            and state in {
                "idle",
                "wander",
                "wake",
                "sit",
            }
        )

        if not autonomous_allowed:
            return

        self.auto_expression_elapsed += dt

        if self.auto_expression_elapsed >= self.AUTO_EXPRESSION_INTERVAL:
            self.auto_expression_elapsed -= self.AUTO_EXPRESSION_INTERVAL
            self.auto_expression_index = (
                self.auto_expression_index + 1
            ) % len(self.EXPRESSION_SEQUENCE)
            self.auto_expression = (
                self.EXPRESSION_SEQUENCE[
                    self.auto_expression_index
                ]
            )

        self.auto_jump_countdown -= dt

        if self.auto_jump_active_time > 0.0:
            self.auto_jump_active_time = max(
                0.0,
                self.auto_jump_active_time - dt,
            )

        if (
            self.auto_jump_countdown <= 0.0
            and self.auto_jump_active_time <= 0.0
        ):
            self.auto_jump_active_time = self.AUTO_JUMP_DURATION
            self.auto_jump_countdown = self.AUTO_JUMP_INTERVAL

    def _draw_shadow(self, painter, y_offset):
        width = (
            155.0
            * max(
                0.55,
                1.0 - min(abs(y_offset) / 90.0, 0.50),
            )
        )

        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 42))
        painter.drawEllipse(
            QRectF(
                -width / 2,
                -3.5,
                width,
                7,
            )
        )
        painter.restore()

    def draw(self, painter, rect):
        state = self.state_machine.get_state()
        expression = self._expression_for_state(state)
        pixmap = (
            self.frames.get(expression)
            or self.frames["laugh"]
        )

        x_offset = 0.0
        y_offset = 0.0
        sx = 1.0
        sy = 1.0
        rotation = 0.0

        if state in {
            "idle",
            "wander",
            "wake",
            "sit",
        }:
            phase = self.auto_elapsed
            breathing = math.sin(phase * 2.4)

            sx = 1.0 - breathing * 0.008
            sy = 1.0 + breathing * 0.012

            x_offset = math.sin(phase * 1.15) * 2.0
            y_offset = -abs(
                math.sin(phase * 1.8)
            ) * 1.8
            rotation = math.sin(phase * 1.25) * 0.7

            if self.auto_expression == "laugh":
                y_offset += math.sin(phase * 4.0) * 1.0
            elif self.auto_expression == "smile":
                x_offset += math.sin(phase * 1.7) * 1.1
            elif self.auto_expression == "neutral":
                rotation += math.sin(phase * 1.8) * 0.35
            elif self.auto_expression == "tongue_out":
                y_offset += math.sin(phase * 3.6) * 1.2
            elif self.auto_expression == "halo":
                y_offset -= abs(
                    math.sin(phase * 1.5)
                ) * 1.5
            elif self.auto_expression == "costume":
                rotation += math.sin(phase * 1.6) * 0.45

        if self.auto_jump_active_time > 0.0:
            progress = 1.0 - (
                self.auto_jump_active_time
                / self.AUTO_JUMP_DURATION
            )
            progress = max(
                0.0,
                min(1.0, progress),
            )

            y_offset -= 46.0 * math.sin(
                progress * math.pi
            )

            if progress < 0.16:
                u = progress / 0.16
                sx = 1.0 + 0.07 * (1.0 - u)
                sy = 1.0 - 0.08 * (1.0 - u)
            elif progress > 0.84:
                u = (progress - 0.84) / 0.16
                sx = 1.0 + 0.09 * u
                sy = 1.0 - 0.07 * u
            else:
                sx = 0.965
                sy = 1.035

            rotation += math.sin(
                progress * math.pi * 2.0
            ) * 2.0

        if (
            state == "jump"
            and self.auto_jump_active_time <= 0.0
        ):
            duration = self.ONE_SHOT_DURATIONS["jump"]
            progress = max(
                0.0,
                min(
                    1.0,
                    self.elapsed / duration,
                ),
            )

            y_offset = -58.0 * math.sin(
                progress * math.pi
            )
            sx = 0.95
            sy = 1.05
            rotation = math.sin(
                progress * math.pi * 2.0
            ) * 2.5

        elif state == "sleep":
            sx = 1.02
            sy = 0.97
            y_offset = 3.0

        painter.save()

        painter.translate(
            rect.center().x() + x_offset,
            rect.bottom() + y_offset,
        )

        painter.scale(self.facing, 1.0)

        self._draw_shadow(
            painter,
            y_offset,
        )

        painter.rotate(rotation)
        painter.scale(sx, sy)

        target_h = max(
            175.0,
            min(
                float(rect.height()) * 1.15,
                300.0,
            ),
        )

        scaled = pixmap.scaledToHeight(
            max(1, int(target_h)),
            Qt.FastTransformation,
        )

        painter.drawPixmap(
            int(-scaled.width() / 2),
            -scaled.height(),
            scaled,
        )

        painter.restore()

