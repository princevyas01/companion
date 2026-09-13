import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtCore import QRect, QRectF

from ui.dog_animator import DogAnimator
from ui.white_hamster_animator import WhiteHamsterAnimator
from ui.yellow_guardian_hamster_animator import YellowGuardianHamsterAnimator


class Dummy:
    def __init__(self, state):
        self.state = state
        self.elapsed = 0.0

    def get_state(self):
        return self.state

    def force_state(self, state):
        self.state = state
        self.elapsed = 0.0

    @property
    def time_in_state(self):
        return self.elapsed


app = QApplication(sys.argv)

# Existing dog smoke test.
states = [
    "idle",
    "tongue_out",
    "happy",
    "sit",
    "sit_down",
    "bark",
    "celebrate",
    "sleep",
    "exhausted",
    "wake",
    "react_click",
    "drag",
    "react_drag",
    "focus",
    "annoyed",
    "wander",
    "type",
]

for state in states:
    anim = DogAnimator(Dummy(state))
    img = QImage(100, 100, QImage.Format_ARGB32)
    img.fill(0)
    painter = QPainter(img)
    anim.draw(painter, QRectF(0, 0, 100, 100))
    painter.end()


# White Meme Hamster verification.
white_dummy = Dummy("idle")
white_anim = WhiteHamsterAnimator(white_dummy)

required_frames = {
    "laugh",
    "smile",
    "neutral",
    "tongue_out",
    "halo",
    "costume",
}

assert required_frames.issubset(set(white_anim.frames.keys())), (
    "Missing White Meme Hamster frames: "
    + str(required_frames - set(white_anim.frames.keys()))
)

# The requested default is the humorous laugh source.
assert white_anim._expression_for_state("idle") == "laugh"
assert white_anim._expression_for_state("wake") == "laugh"
assert white_anim._expression_for_state("wander") == "laugh"
assert white_anim._expression_for_state("jump") == "laugh"

for state in [
    "idle",
    "laugh",
    "smile",
    "neutral",
    "tongue_out",
    "halo",
    "costume",
    "jump",
    "wander",
]:
    expression = white_anim._expression_for_state(state)
    assert expression in white_anim.frames, (
        f"{state!r} resolved to missing frame {expression!r}"
    )

# White rendering smoke test.
white_img = QImage(350, 400, QImage.Format_ARGB32)
white_img.fill(0)
white_painter = QPainter(white_img)
white_anim.draw(
    white_painter,
    QRect(100, 230, 150, 160),
)
white_painter.end()


# Yellow companion regression test.
yellow_anim = YellowGuardianHamsterAnimator(Dummy("idle"))

yellow_img = QImage(350, 400, QImage.Format_ARGB32)
yellow_img.fill(0)
yellow_painter = QPainter(yellow_img)
yellow_anim.draw(
    yellow_painter,
    QRect(100, 230, 150, 160),
)
yellow_painter.end()

print(
    "White Meme Hamster default/source-frame smoke tests "
    "and existing companion tests passed."
)
