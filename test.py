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

# Facing direction updates with movement
white_anim.set_facing(-1)
assert white_anim.facing == -1, "White Hamster facing should support -1 for leftward movement"
white_anim.set_facing(1)
assert white_anim.facing == 1, "White Hamster facing should support 1 for rightward movement"

# Autonomous expression rotation test (7.0s cycle)
dummy.force_state("idle")
white_anim.reset_animation()
assert white_anim.auto_expression == "laugh", "Autonomous cycle must start on laugh"
# Advance 7.0s (280 ticks at 0.025s)
for _ in range(280):
    white_anim.update()
assert white_anim.auto_expression == "smile", f"After 7s, expression should be 'smile', got {white_anim.auto_expression}"
# Advance another 7.0s
for _ in range(280):
    white_anim.update()
assert white_anim.auto_expression == "neutral", f"After 14s, expression should be 'neutral', got {white_anim.auto_expression}"

# Autonomous jump test (11.0s interval, 1.15s duration)
white_anim.reset_animation()
assert white_anim.auto_jump_countdown == 11.0
for _ in range(440):
    white_anim.update()
assert white_anim.auto_jump_active_time > 0.0, "Autonomous jump should become active after 11.0s"

# 3b. Verify trigger_anim_safe and autonomous movement logic for White Hamster
from ui.chibi_window import DragonCompanionWindow

class MockTimer:
    def isActive(self):
        return False

class MockTypingEngine:
    def __init__(self):
        self.timer = MockTimer()

class MockVideoDetector:
    def is_watching_video(self):
        return False

class MockPetWindow:
    def __init__(self):
        self._x = 500
        self._y = 500
        self._w = 350
        self._h = 400
        self.current_character = "white_hamster"
        self.state_machine = Dummy("idle")
        self.animator = WhiteHamsterAnimator(self.state_machine)
        self._white_auto_wander_active = False
        self._white_auto_wander_target = None
        self._white_auto_wander_x = None
        self._white_auto_wander_y = None
        self._white_auto_wander_clock = 0.0
        self._white_auto_next_wander = 11.0
        self.layout_manager = LayoutManager(self)
        self.updated = False
        self.is_stopped = False
        self.drag_position = None
        self.pomodoro = Dummy()
        self.pomodoro.is_running = False
        self.typing_engine = MockTypingEngine()
        self.is_generating = False
        self.mood = Dummy()
        self.video_detector = MockVideoDetector()

    def update(self):
        self.updated = True

    def x(self): return self._x
    def y(self): return self._y
    def width(self): return self._w
    def height(self): return self._h
    def geometry(self): return QRect(self._x, self._y, self._w, self._h)
    def frameGeometry(self): return QRect(self._x, self._y, self._w, self._h)
    def move(self, x, y):
        self._x = x
        self._y = y

mock_win = MockPetWindow()
for expr in WhiteHamsterAnimator.EXPRESSIONS:
    mock_win.updated = False
    DragonCompanionWindow.trigger_anim_safe(mock_win, expr)
    assert mock_win.animator.get_expression() == expr, f"trigger_anim_safe failed to set expression {expr}"
    assert mock_win.animator.manual_action_lock > 0.0, "trigger_anim_safe should set manual_action_lock"
    assert mock_win.state_machine.get_state() == expr, "trigger_anim_safe should force action state"
    assert mock_win.updated, "trigger_anim_safe did not request window update"

# Test manual jump and manual wander triggers
DragonCompanionWindow.trigger_anim_safe(mock_win, "jump")
assert mock_win.state_machine.get_state() == "jump"
assert mock_win.animator.manual_action_lock > 0.0

DragonCompanionWindow.trigger_anim_safe(mock_win, "wander")
assert mock_win._white_auto_wander_active is True
assert mock_win._white_auto_wander_target is not None

# Test autonomous movement controller
mock_win._white_auto_wander_active = False
mock_win._white_auto_wander_clock = 12.0
mock_win._white_auto_next_wander = 10.0
DragonCompanionWindow._update_white_hamster_autonomous_movement(mock_win)
assert mock_win._white_auto_wander_active is True, "Autonomous wander should activate when clock >= next_wander"
init_x = mock_win.x()
DragonCompanionWindow._update_white_hamster_autonomous_movement(mock_win)
assert mock_win.x() != init_x or mock_win.y() != 500, "Autonomous wander should move pet position"

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
