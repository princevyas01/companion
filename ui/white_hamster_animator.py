"""
White Meme Hamster exact reference-sprite renderer.

The six original expression images are the visual source of truth.
The additional sticker images are action-specific reference sprites.

IMPORTANT:
- Never redraw the hamster's face/body procedurally.
- Never generate replacement artwork.
- Animate the complete sprite only.
- Preserve all hand-drawn imperfections.
- Background transparency is derived without changing RGB artwork.
"""

import math
import sys
from collections import deque
from pathlib import Path

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage, QPainter, QPixmap, QColor


class WhiteHamsterAnimator:
    """Exact sprite renderer plus autonomous movement and action stickers."""

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

        # Additional supplied sticker actions.
        "magic": 2.50,
        "type": 2.00,
        "focus": 2.00,
        "eat": 2.50,
        "sad": 2.20,
        "happy": 2.00,
        "paint": 3.00,
        "cook": 3.00,
    }

    FRAME_FILES = {
        # Existing six expression assets. DO NOT replace their artwork.
        "laugh": "laugh.png",
        "smile": "smile.png",
        "neutral": "neutral.png",
        "tongue_out": "tongue_out.png",
        "halo": "halo.png",
        "costume": "costume.png",
    }

    ACTION_FRAME_FILES = {
        # These are the eight additional user-supplied sticker references.
        "laugh_action": "actions/laugh_action.png",
        "magic": "actions/magic.png",
        "type": "actions/type.png",
        "eat": "actions/eat.png",
        "sad": "actions/sad.png",
        "happy": "actions/happy.png",
        "paint": "actions/paint.png",
        "cook": "actions/cook.png",
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

    ACTIONS = (
        "magic",
        "type",
        "focus",
        "eat",
        "sad",
        "happy",
        "paint",
        "cook",
    )

    AUTO_EXPRESSION_INTERVAL = 7.0
    AUTO_JUMP_INTERVAL = 11.0
    AUTO_JUMP_DURATION = 1.15

    BASE_TARGET_HEIGHT = 300.0
    ACTION_TARGET_HEIGHT = 280.0

    def __init__(self, state_machine, asset_dir=None):
        self.state_machine = state_machine
        self.facing = 1

        # State-machine animation time.
        self.elapsed = 0.0
        self._last_state = None

        # Autonomous expression system.
        self.auto_elapsed = 0.0
        self.auto_expression_elapsed = 0.0
        self.auto_expression_index = 0
        self.auto_expression = "laugh"

        # Autonomous jump system.
        self.auto_jump_countdown = self.AUTO_JUMP_INTERVAL
        self.auto_jump_active_time = 0.0

        # Manual/action sticker state.
        self.manual_action_lock = 0.0
        self.special_action = None
        self.special_action_elapsed = 0.0
        self.special_action_duration = 0.0

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
        self.action_frames = {}

        self._load_frames()

    # ------------------------------------------------------------
    # Public state/control API
    # ------------------------------------------------------------

    def set_facing(self, direction):
        self.facing = 1 if direction >= 0 else -1

    def set_expression(self, expression):
        if expression in self.EXPRESSION_SEQUENCE:
            self.auto_expression = expression
            self.auto_expression_index = (
                self.EXPRESSION_SEQUENCE.index(expression)
            )
            self.auto_expression_elapsed = 0.0

    def get_expression(self):
        state = self.state_machine.get_state()

        if self.special_action:
            return self.special_action

        return self._expression_for_state(state)

    @property
    def current_expression(self):
        return self.get_expression()

    @current_expression.setter
    def current_expression(self, expression):
        self.set_expression(expression)

    def set_special_action(self, action, duration=None, persistent=False):
        """
        Show one of the supplied additional sticker references.

        persistent=True is used for keyboard typing so the type/read sticker
        remains visible while the user continues typing.
        """
        if action == "laugh":
            action = "laugh_action"

        if action == "focus":
            action = "type"

        if action not in self.action_frames:
            return False

        self.special_action = action
        self.special_action_elapsed = 0.0

        if persistent:
            self.special_action_duration = float("inf")
        else:
            self.special_action_duration = float(
                duration
                if duration is not None
                else self.ONE_SHOT_DURATIONS.get(
                    action,
                    2.0,
                )
            )

        self.manual_action_lock = (
            0.0
            if persistent
            else self.special_action_duration
        )

        return True

    def clear_special_action(self):
        self.special_action = None
        self.special_action_elapsed = 0.0
        self.special_action_duration = 0.0
        self.manual_action_lock = 0.0

    def clear_special(self):
        self.elapsed = 0.0
        self._last_state = None
        self.clear_special_action()

    def reset_animation(self):
        self.elapsed = 0.0
        self._last_state = None

        self.auto_elapsed = 0.0
        self.auto_expression_elapsed = 0.0
        self.auto_expression_index = 0
        self.auto_expression = "laugh"

        self.auto_jump_countdown = self.AUTO_JUMP_INTERVAL
        self.auto_jump_active_time = 0.0

        self.clear_special_action()

    # ------------------------------------------------------------
    # Safe reference-image background extraction
    # ------------------------------------------------------------

    @staticmethod
    def _near_white(pixel):
        return (
            pixel.alpha() > 0
            and pixel.red() >= 242
            and pixel.green() >= 242
            and pixel.blue() >= 242
        )

    @classmethod
    def _prepare_reference_image(cls, image):
        """
        Preserve the original RGB artwork and only derive transparency.

        The old implementation flood-filled white pixels directly from the
        border. Hand-drawn outlines have tiny gaps, so the white body could
        become connected to the outside and turn transparent on a dark
        desktop. This method closes only the temporary barrier mask before
        flood-filling. Artwork pixels themselves are never altered.
        """
        image = image.convertToFormat(QImage.Format_ARGB32)

        w = image.width()
        h = image.height()

        if w <= 0 or h <= 0:
            return image

        # If the supplied image already has real transparency, preserve it.
        has_transparency = False
        for y in range(h):
            for x in range(w):
                if image.pixelColor(x, y).alpha() < 250:
                    has_transparency = True
                    break
            if has_transparency:
                break

        if has_transparency:
            return cls._trim_alpha_only(image)

        # Temporary "ink barrier": all non-near-white pixels.
        ink = bytearray(w * h)

        def idx(x, y):
            return y * w + x

        for y in range(h):
            for x in range(w):
                p = image.pixelColor(x, y)
                if not cls._near_white(p):
                    ink[idx(x, y)] = 1

        # Dilate ONLY the temporary barrier.
        # This seals small hand-drawn outline gaps without touching RGB data.
        radius = 3
        sealed = bytearray(w * h)

        for y in range(h):
            for x in range(w):
                found = False
                for oy in range(-radius, radius + 1):
                    yy = y + oy
                    if yy < 0 or yy >= h:
                        continue
                    for ox in range(-radius, radius + 1):
                        xx = x + ox
                        if xx < 0 or xx >= w:
                            continue
                        if ink[idx(xx, yy)]:
                            found = True
                            break
                    if found:
                        break

                if found:
                    sealed[idx(x, y)] = 1

        # Flood-fill outer near-white background, blocked by the sealed ink.
        background = bytearray(w * h)
        queue = deque()

        def visit(x, y):
            i = idx(x, y)

            if background[i] or sealed[i]:
                return

            if not cls._near_white(image.pixelColor(x, y)):
                return

            background[i] = 1
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

        # Change ONLY alpha of actual outside background pixels.
        for y in range(h):
            for x in range(w):
                if background[idx(x, y)]:
                    image.setPixelColor(
                        x,
                        y,
                        QColor(0, 0, 0, 0),
                    )

        return cls._trim_alpha_only(image)

    @staticmethod
    def _trim_alpha_only(image):
        w = image.width()
        h = image.height()

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

            prepared = self._prepare_reference_image(image)

            self.frames[state] = QPixmap.fromImage(
                prepared,
                Qt.AutoColor,
            )

        for action, filename in self.ACTION_FRAME_FILES.items():
            path = self.asset_dir / filename
            image = QImage(str(path))

            if image.isNull():
                missing.append(str(path))
                continue

            prepared = self._prepare_reference_image(image)

            self.action_frames[action] = QPixmap.fromImage(
                prepared,
                Qt.AutoColor,
            )

        if missing:
            raise FileNotFoundError(
                "White Meme Hamster reference assets missing:\n"
                + "\n".join(missing)
            )

    # ------------------------------------------------------------
    # Animation state
    # ------------------------------------------------------------

    def _expression_for_state(self, state):
        if state in self.EXPRESSIONS:
            return state

        return self.auto_expression

    def _is_manual_expression_state(self, state):
        return state in {
            "laugh",
            "smile",
            "neutral",
            "tongue_out",
            "halo",
            "costume",
            "jump",
            "celebrate",
            "react_click",
        }

    def update(self):
        state = self.state_machine.get_state()
        dt = 0.025

        if state != self._last_state:
            self.elapsed = 0.0
            self._last_state = state

            if self._is_manual_expression_state(state):
                self.manual_action_lock = self.ONE_SHOT_DURATIONS.get(
                    state,
                    1.0,
                )

        else:
            self.elapsed += dt

        # Special action lifecycle.
        if self.special_action:
            self.special_action_elapsed += dt

            if (
                not math.isinf(self.special_action_duration)
                and self.special_action_elapsed
                >= self.special_action_duration
            ):
                self.clear_special_action()

        if self.manual_action_lock > 0.0:
            self.manual_action_lock = max(
                0.0,
                self.manual_action_lock - dt,
            )

        duration = self.ONE_SHOT_DURATIONS.get(state)

        if (
            duration is not None
            and self.elapsed >= duration
            and state not in self.EXPRESSIONS
        ):
            self.state_machine.force_state("idle")
            self.elapsed = 0.0
            self._last_state = "idle"
            self.manual_action_lock = 0.0

        self.auto_elapsed += dt

        # When an action sticker is active, keep its artwork until the action ends.
        if self.special_action:
            return

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

        # Six original expression sprites remain the ONLY automatic cycle.
        self.auto_expression_elapsed += dt

        if (
            self.auto_expression_elapsed
            >= self.AUTO_EXPRESSION_INTERVAL
        ):
            self.auto_expression_elapsed -= (
                self.AUTO_EXPRESSION_INTERVAL
            )

            self.auto_expression_index = (
                self.auto_expression_index + 1
            ) % len(self.EXPRESSION_SEQUENCE)

            self.auto_expression = (
                self.EXPRESSION_SEQUENCE[
                    self.auto_expression_index
                ]
            )

        # Autonomous whole-sprite jump.
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
            self.auto_jump_active_time = (
                self.AUTO_JUMP_DURATION
            )
            self.auto_jump_countdown = (
                self.AUTO_JUMP_INTERVAL
            )

    # ------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------

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

    def _current_pixmap(self, state):
        if self.special_action:
            pixmap = self.action_frames.get(
                self.special_action,
            )
            if pixmap is not None:
                return pixmap

        expression = self._expression_for_state(state)

        return (
            self.frames.get(expression)
            or self.frames["laugh"]
        )

    def draw(self, painter, rect):
        state = self.state_machine.get_state()

        pixmap = self._current_pixmap(state)

        x_offset = 0.0
        y_offset = 0.0
        scale_x = 1.0
        scale_y = 1.0
        rotation = 0.0

        # Normal autonomous idle movement.
        if not self.special_action and state in {
            "idle",
            "wander",
            "wake",
            "sit",
        }:
            phase = self.auto_elapsed
            breathing = math.sin(phase * 2.4)

            scale_x = 1.0 - breathing * 0.008
            scale_y = 1.0 + breathing * 0.012

            x_offset = math.sin(
                phase * 1.15
            ) * 2.0

            y_offset = -abs(
                math.sin(phase * 1.8)
            ) * 1.8

            rotation = math.sin(
                phase * 1.25
            ) * 0.7

            if self.auto_expression == "laugh":
                y_offset += (
                    math.sin(phase * 4.0) * 1.0
                )
            elif self.auto_expression == "smile":
                x_offset += (
                    math.sin(phase * 1.7) * 1.1
                )
            elif self.auto_expression == "neutral":
                rotation += (
                    math.sin(phase * 1.8) * 0.35
                )
            elif self.auto_expression == "tongue_out":
                y_offset += (
                    math.sin(phase * 3.6) * 1.2
                )
            elif self.auto_expression == "halo":
                y_offset -= (
                    abs(math.sin(phase * 1.5)) * 1.5
                )
            elif self.auto_expression == "costume":
                rotation += (
                    math.sin(phase * 1.6) * 0.45
                )

        # Additional action-specific whole-sprite movement.
        if self.special_action:
            phase = self.special_action_elapsed

            if self.special_action == "type":
                y_offset = math.sin(
                    phase * 5.5
                ) * 1.8
                rotation = math.sin(
                    phase * 3.0
                ) * 0.45

            elif self.special_action == "magic":
                y_offset = -abs(
                    math.sin(phase * 2.8)
                ) * 3.0
                rotation = math.sin(
                    phase * 2.1
                ) * 0.8

            elif self.special_action == "eat":
                y_offset = math.sin(
                    phase * 5.0
                ) * 2.0
                scale_x = 1.0 + (
                    math.sin(phase * 5.0) * 0.01
                )
                scale_y = 1.0 - (
                    math.sin(phase * 5.0) * 0.01
                )

            elif self.special_action == "sad":
                y_offset = (
                    math.sin(phase * 2.0) * 1.2
                    + 3.0
                )
                rotation = math.sin(
                    phase * 1.6
                ) * 0.5

            elif self.special_action == "happy":
                y_offset = -abs(
                    math.sin(phase * 5.0)
                ) * 4.0
                rotation = math.sin(
                    phase * 5.0
                ) * 1.2

            elif self.special_action == "paint":
                x_offset = math.sin(
                    phase * 2.4
                ) * 2.0
                rotation = math.sin(
                    phase * 1.7
                ) * 0.7

            elif self.special_action == "cook":
                y_offset = math.sin(
                    phase * 3.0
                ) * 1.6
                rotation = math.sin(
                    phase * 1.4
                ) * 0.6

            elif self.special_action == "laugh_action":
                y_offset = -abs(
                    math.sin(phase * 6.0)
                ) * 4.0
                rotation = math.sin(
                    phase * 6.0
                ) * 1.2

        # Autonomous jump remains available during normal expressions.
        if (
            self.auto_jump_active_time > 0.0
            and not self.special_action
            and state in {
                "idle",
                "wander",
                "wake",
                "sit",
            }
        ):
            progress = 1.0 - (
                self.auto_jump_active_time
                / self.AUTO_JUMP_DURATION
            )

            progress = max(
                0.0,
                min(1.0, progress),
            )

            y_offset -= (
                46.0
                * math.sin(
                    progress * math.pi
                )
            )

            if progress < 0.16:
                u = progress / 0.16
                scale_x = 1.0 + (
                    0.07 * (1.0 - u)
                )
                scale_y = 1.0 - (
                    0.08 * (1.0 - u)
                )
            elif progress > 0.84:
                u = (
                    progress - 0.84
                ) / 0.16
                scale_x = 1.0 + 0.09 * u
                scale_y = 1.0 - 0.07 * u
            else:
                scale_x = 0.965
                scale_y = 1.035

            rotation += math.sin(
                progress * math.pi * 2.0
            ) * 2.0

        # Manual jump remains functional.
        if (
            state == "jump"
            and not self.special_action
            and self.auto_jump_active_time <= 0.0
        ):
            progress = max(
                0.0,
                min(
                    1.0,
                    self.elapsed / self.AUTO_JUMP_DURATION,
                ),
            )

            y_offset = (
                -58.0
                * math.sin(
                    progress * math.pi
                )
            )

            scale_x = 0.95
            scale_y = 1.05

            rotation = math.sin(
                progress * math.pi * 2.0
            ) * 2.5

        elif state == "sleep":
            scale_x = 1.02
            scale_y = 0.97
            y_offset = 3.0

        painter.save()

        # Preserve source pixel look. No smooth vector redraw.
        painter.translate(
            rect.center().x() + x_offset,
            rect.bottom() + y_offset,
        )

        painter.scale(
            self.facing,
            1.0,
        )

        self._draw_shadow(
            painter,
            y_offset,
        )

        painter.rotate(rotation)
        painter.scale(
            scale_x,
            scale_y,
        )

        target_h = (
            self.ACTION_TARGET_HEIGHT
            if self.special_action
            else self.BASE_TARGET_HEIGHT
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
