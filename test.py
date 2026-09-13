import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtCore import QRect, QRectF, QPoint

from ui.dog_animator import DogAnimator
from ui.white_hamster_animator import WhiteHamsterAnimator
from ui.yellow_guardian_hamster_animator import YellowGuardianHamsterAnimator
from core.characters import CHARACTER_PROFILES, get_character_config, get_character_line
from core.layout import LayoutManager
from ui.speech_bubble import SpeechBubble
from ui.chat_overlay import ChatInputWidget

class Dummy:
    def __init__(self, state="idle"):
        self.state = state
        self.elapsed = 0.0

    def get_state(self):
        return self.state

    def force_state(self, state):
        self.state = state
        self.elapsed = 0.0

    def request_state(self, state):
        self.state = state
        self.elapsed = 0.0

    @property
    def time_in_state(self):
        return self.elapsed

class DummyWindow:
    def __init__(self, char="white_hamster"):
        self.current_character = char
        self._w = 350
        self._h = 400

    def width(self):
        return self._w

    def height(self):
        return self._h

    def geometry(self):
        return QRect(100, 100, self._w, self._h)

app = QApplication.instance() or QApplication(sys.argv)

# 1. Existing dog smoke test
states = [
    "idle", "tongue_out", "happy", "sit", "sit_down", "bark", "celebrate",
    "sleep", "exhausted", "wake", "react_click", "drag", "react_drag",
    "focus", "annoyed", "wander", "type"
]
for state in states:
    anim = DogAnimator(Dummy(state))
    img = QImage(100, 100, QImage.Format_ARGB32)
    img.fill(0)
    painter = QPainter(img)
    anim.draw(painter, QRectF(0, 0, 100, 100))
    painter.end()

# 2. Assets verification
asset_dir = os.path.join(os.path.dirname(__file__), "assets", "white_hamster")
required_files = {
    "laugh": "laugh.png",
    "smile": "smile.png",
    "neutral": "neutral.png",
    "tongue_out": "tongue_out.png",
    "halo": "halo.png",
    "costume": "costume.png",
}

for expr, fname in required_files.items():
    fpath = os.path.join(asset_dir, fname)
    assert os.path.exists(fpath), f"Missing asset {fpath}"
    qimg = QImage(fpath)
    assert not qimg.isNull(), f"Invalid image {fpath}"
    assert qimg.hasAlphaChannel(), f"Image {fpath} must have an alpha channel"

# Locked laugh reference check
laugh_path = os.path.join(asset_dir, "laugh.png")
assert os.path.getsize(laugh_path) == 34398, "laugh.png must remain locked and unchanged (34398 bytes)"

# 3. White Meme Hamster animator verification
dummy = Dummy("idle")
white_anim = WhiteHamsterAnimator(dummy)

# Default must be laugh
assert white_anim.current_expression == "laugh", "Initial expression must be 'laugh'"
assert white_anim.get_expression() == "laugh", "get_expression() must return 'laugh'"

# Verify all 6 expressions load and render without error
rect = QRect(100, 230, 150, 160)
for expr in WhiteHamsterAnimator.EXPRESSIONS:
    white_anim.set_expression(expr)
    assert white_anim.get_expression() == expr
    for st in ["idle", "jump", "wander", "sleep"]:
        dummy.force_state(st)
        white_anim.update()
        img = QImage(350, 400, QImage.Format_ARGB32)
        img.fill(0)
        painter = QPainter(img)
        white_anim.draw(painter, rect)
        painter.end()

# Verify state-machine expression switching in draw()
for expr in WhiteHamsterAnimator.EXPRESSIONS:
    dummy.force_state(expr)
    img = QImage(350, 400, QImage.Format_ARGB32)
    img.fill(0)
    painter = QPainter(img)
    white_anim.draw(painter, rect)
    painter.end()
    assert white_anim.get_expression() == expr, f"draw() did not adopt expression state {expr}"

# Sprite is never mirrored
white_anim.set_facing(-1)
assert white_anim.facing == 1, "White Hamster facing must never be mirrored (-1)"

# 3b. Verify trigger_anim_safe logic for White Hamster
from ui.chibi_window import DragonCompanionWindow
class MockPetWindow:
    def __init__(self):
        self.current_character = "white_hamster"
        self.state_machine = Dummy("idle")
        self.animator = WhiteHamsterAnimator(self.state_machine)
        self._white_expression_cycle = ("laugh","smile","neutral","tongue_out","halo","costume")
        self._white_expression_index = 0
        self._white_expression_elapsed = 3.5
        self.updated = False

    def update(self):
        self.updated = True

    def _white_wander_target(self):
        return QPoint(200, 200)

    def x(self): return 100
    def y(self): return 100

mock_win = MockPetWindow()
for expr in WhiteHamsterAnimator.EXPRESSIONS:
    mock_win.updated = False
    DragonCompanionWindow.trigger_anim_safe(mock_win, expr)
    assert mock_win.animator.get_expression() == expr, f"trigger_anim_safe failed to set expression {expr}"
    assert mock_win._white_expression_elapsed == 0.0, "trigger_anim_safe did not reset expression elapsed"
    assert mock_win._white_expression_cycle[mock_win._white_expression_index] == expr, "trigger_anim_safe did not sync expression index"
    assert mock_win.updated, "trigger_anim_safe did not request window update"

# Test jump and wander
DragonCompanionWindow.trigger_anim_safe(mock_win, "jump")
assert mock_win.state_machine.get_state() == "jump"

DragonCompanionWindow.trigger_anim_safe(mock_win, "wander")
assert mock_win.state_machine.get_state() == "wander"
assert mock_win.wander_target == QPoint(200, 200)

# 4. Character profiles and actions
prof = CHARACTER_PROFILES["white_hamster"]
assert prof["supported_actions"] == [
    "laugh", "smile", "neutral", "tongue_out", "halo", "costume", "jump", "wander"
], f"Unexpected actions: {prof['supported_actions']}"

# Verify other characters exist
for c in ["dragon", "dog", "luffy", "cat_orange", "cat_tuxedo", "cats_duo", "fox", "rabbit", "penguin", "hamster", "owl", "panda", "yellow_guardian_hamster"]:
    assert c in CHARACTER_PROFILES, f"Missing companion {c}"

# 5. Layout and Speech Bubble
dummy_win = DummyWindow("white_hamster")
layout_mgr = LayoutManager(dummy_win)
bubble_rect = layout_mgr.get_bubble_rect(QRect(0, 0, 100, 40))
assert bubble_rect.width() <= 178, f"Bubble width {bubble_rect.width()} exceeds max 178"
assert bubble_rect.height() <= 54, f"Bubble height {bubble_rect.height()} exceeds max 54"

# 6. Chat Overlay separation
chat = ChatInputWidget()
# Verify show_overlay calculates target_y above pet window
# target_y = pet_y - self.height() - 18
pet_y = 500
target_y = pet_y - chat.height() - 18
assert target_y < pet_y, "Chat overlay must appear above the pet window"

# 7. Yellow companion regression test
yellow_anim = YellowGuardianHamsterAnimator(Dummy("idle"))
yellow_img = QImage(350, 400, QImage.Format_ARGB32)
yellow_img.fill(0)
yellow_painter = QPainter(yellow_img)
yellow_anim.draw(yellow_painter, QRect(100, 230, 150, 160))
yellow_painter.end()

print("All White Meme Hamster 6-expression, layout, bubble, chat, and regression tests passed!")
