import sys
import time
import datetime
import random
import ctypes
import threading
from PyQt5.QtWidgets import QWidget, QApplication, QMenu, QSystemTrayIcon, QAction
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSlot, QMetaObject, Q_ARG
from PyQt5.QtGui import QPainter, QMouseEvent
from core.state_machine import StateMachine
from core.layout import LayoutManager
from core.typing_engine import TypingEngine
from core.pomodoro import PomodoroTimer
from ui.animator import DragonAnimator
from ui.sprite_animator import SpriteAnimator
from ui.dog_animator import DogAnimator
from ui.cat_animator import CatAnimator
from ui.chibi_animator import ChibiAnimalAnimator
from ui.white_hamster_animator import WhiteHamsterAnimator
from ui.yellow_guardian_hamster_animator import YellowGuardianHamsterAnimator
from ui.speech_bubble import SpeechBubble
from ui.chat_overlay import ChatInputWidget
from core.mood import MoodSystem
from ui.control_panel import ControlPanel
from core.web_server import PetWebServer
from core.dialogue import LINES
from core.characters import CHARACTER_PROFILES, get_character_line
from core.weather import WeatherService
from core.video_detector import VideoDetector

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint),
                ("dwTime", ctypes.c_ulong)]

class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_byte),
        ("BatteryFlag", ctypes.c_byte),
        ("BatteryLifePercent", ctypes.c_byte),
        ("SystemStatusFlag", ctypes.c_byte),
        ("BatteryLifeTime", ctypes.c_ulong),
        ("BatteryFullLifeTime", ctypes.c_ulong)
    ]

class GlobalKeyboardTracker:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
    def get_idle_time(self):
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if self.user32.GetLastInputInfo(ctypes.byref(lii)):
            tick_count = self.kernel32.GetTickCount() & 0xFFFFFFFF
            millis = (tick_count - lii.dwTime) & 0xFFFFFFFF
            return millis / 1000.0
        return 0.0
        
    def is_typing(self):
        # Check standard character keys A-Z (0x41 to 0x5A)
        for i in range(0x41, 0x5A + 1):
            if self.user32.GetAsyncKeyState(i) & 0x8000:
                return True
        # Check space (0x20) and backspace (0x08)
        if self.user32.GetAsyncKeyState(0x20) & 0x8000: return True
        if self.user32.GetAsyncKeyState(0x08) & 0x8000: return True
        return False

class DragonCompanionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.wander_chance = 0.02
        self.control_panel = None
        self.initUI()
        
        # Core Systems
        self.mood = MoodSystem()
        
        # Action locking
        self.is_generating = False
        self.is_destroyed = False
        
        # State machine
        self.state_machine = StateMachine()
        
        # Animators
        self.animator_dragon = DragonAnimator(self.state_machine)
        self.animator_dog = DogAnimator(self.state_machine)
        self.animator_luffy = SpriteAnimator(self.state_machine, "assets/luffy.png")
        self.animator_cat_orange = CatAnimator(self.state_machine, cat_variant="cat_orange")
        self.animator_cat_tuxedo = CatAnimator(self.state_machine, cat_variant="cat_tuxedo")
        self.animator_cats_duo = CatAnimator(self.state_machine, cat_variant="cats_duo")
        self.chibi_animators = {
            sp: ChibiAnimalAnimator(self.state_machine, species=sp)
            for sp in ['fox', 'rabbit', 'penguin', 'hamster', 'owl', 'panda']
        }
        self.chibi_animators["white_hamster"] = WhiteHamsterAnimator(self.state_machine)
        self.chibi_animators["yellow_guardian_hamster"] = YellowGuardianHamsterAnimator(self.state_machine)
        self.current_character = "dragon"
        self.animator = self.animator_dragon
        
        from core.ai_companion import AICompanion
        self.ai = AICompanion()
        
        self.typing_engine = TypingEngine(self)
        self.layout_manager = LayoutManager(self)
        self.speech_bubble = SpeechBubble(self)
        
        self.chat_overlay = ChatInputWidget(self)
        self.chat_overlay.set_callback(self.process_chat_safe)
        
        self.pomodoro = PomodoroTimer(self)
        self.weather = WeatherService(self, enabled=False) # Off by default per user request
        self.keyboard_tracker = GlobalKeyboardTracker()
        self.video_detector = VideoDetector()
        self.is_stopped = False
        self._was_watching_video = False
        
        # Main Loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(25) # ~40fps
        
        # Behavior Loop
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.do_behavior_tick)
        self.idle_timer.start(500) # Check every half second
        
        # Fire breathe Timer (every 5 seconds)
        self.fire_timer = QTimer(self)
        self.fire_timer.timeout.connect(self.do_fire_breathe)
        self.fire_timer.start(5000)
        
        # Posture Timer (50 minutes)
        self.posture_timer = QTimer(self)
        self.posture_timer.timeout.connect(lambda: self.say(get_character_line(self.current_character, "posture")))
        self.posture_timer.start(50 * 60 * 1000)
        
        # Battery Timer (Check every 5 minutes)
        self.battery_timer = QTimer(self)
        self.battery_timer.timeout.connect(self.check_battery)
        self.battery_timer.start(5 * 60 * 1000)
        
        # Mood Timer (Update stats every 8 seconds)
        self.mood_timer = QTimer(self)
        self.mood_timer.timeout.connect(self.mood.tick)
        self.mood_timer.start(8000)
        
        # Interaction State
        self.drag_position = None
        self.click_count = 0
        self.wander_target = None
        self._wander_float_x = None
        self._wander_float_y = None
        
        # White Meme Hamster dedicated autonomous desktop movement.
        self._white_auto_wander_active = False
        self._white_auto_wander_target = None
        self._white_auto_wander_x = None
        self._white_auto_wander_y = None
        self._white_auto_wander_clock = 0.0
        self._white_auto_next_wander = random.uniform(7.0, 12.0)
        
        self.setup_tray()
        
        # Initial placement
        self.layout_manager._refresh_screen()
        screen = self.layout_manager._screen_rect
        self.move(screen.right() - self.width(), screen.bottom() - self.height())
        self.state_machine.force_state('wake')
        QTimer.singleShot(2000, lambda: self.say(self.mood.get_time_greeting()))
        
        # Start Web Server Dashboard
        self.web_server = PetWebServer(self)
        
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(350, 400)
        
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Baby Dragon Companion")
        tray_menu = QMenu()
        
        feed_action = QAction("Feed", self)
        feed_action.triggered.connect(lambda: self.say("Yummy! Rawr!", force_state='celebrate'))
        tray_menu.addAction(feed_action)
        
        pomo_action = QAction("Start 25m Focus", self)
        pomo_action.triggered.connect(self.pomodoro.start_work)
        tray_menu.addAction(pomo_action)
        
        stop_pomo_action = QAction("Stop Timer", self)
        stop_pomo_action.triggered.connect(self.pomodoro.stop)
        tray_menu.addAction(stop_pomo_action)
        
        tray_menu.addSeparator()
        
        start_action = QAction("Start Pet", self)
        start_action.triggered.connect(self.start_pet_safe)
        tray_menu.addAction(start_action)
        
        stop_action = QAction("Stop Pet", self)
        stop_action.triggered.connect(self.stop_pet_safe)
        tray_menu.addAction(stop_action)
        
        tray_menu.addSeparator()
        
        char_menu = tray_menu.addMenu("Switch Character")
        for char_id, profile in CHARACTER_PROFILES.items():
            action = QAction(profile.get("name", char_id.title()), self)
            action.triggered.connect(lambda checked=False, c=char_id: self.switch_character_safe(c))
            char_menu.addAction(action)
        
        tray_menu.addSeparator()
        
        settings_action = QAction("Control Panel", self)
        settings_action.triggered.connect(self.show_control_panel)
        tray_menu.addAction(settings_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_control_panel(self):
        if self.control_panel is None:
            self.control_panel = ControlPanel(self)
        self.control_panel.show()
        self.control_panel.activateWindow()

    @pyqtSlot()
    def start_pet_safe(self):
        self.start_pet()

    @pyqtSlot()
    def stop_pet_safe(self):
        self.stop_pet()

    @pyqtSlot(bool)
    def set_video_sleep_safe(self, enabled):
        self.mood.sleep_on_video = enabled

    def closeEvent(self, event):
        self.is_destroyed = True
        self.web_server.stop()
        self.web_server.wait()
        super().closeEvent(event)

    def stop_pet(self):
        self.is_stopped = True
        self._reset_white_hamster_autonomous_movement()
        self.wander_target = None
        self._wander_float_x = None
        self._wander_float_y = None
        if hasattr(self, 'typing_engine'):
            self.typing_engine.stop_typing()
        self.hide()
        if hasattr(self, 'speech_bubble'):
            self.speech_bubble.hide()
        if hasattr(self, 'chat_overlay'):
            self.chat_overlay.hide()

    def start_pet(self):
        self.is_stopped = False
        self.show()
        self.mood.wake_up_refresh()
        self.state_machine.force_state('wake')
        self.say("I'm back!")

    @pyqtSlot(str)
    def switch_character_safe(self, name):
        if hasattr(self.animator, "clear_special"):
            self.animator.clear_special()
        self._reset_white_hamster_autonomous_movement()
        self._wander_float_x = None
        self._wander_float_y = None
        self.current_character = name

        if name == "white_hamster":
            self.animator = self.chibi_animators["white_hamster"]
            if hasattr(self.animator, "reset_animation"):
                self.animator.reset_animation()
            self.state_machine.force_state("idle")
            self.update()
            return

        if name == "dog":
            self.animator = self.animator_dog
        elif name == "cat_orange":
            self.animator = self.animator_cat_orange
        elif name in ["cat_tuxedo", "cat_grey"]:
            self.animator = self.animator_cat_tuxedo
        elif name in ["cats_duo", "cat"]:
            self.animator = self.animator_cats_duo
        elif name == "luffy":
            self.animator = self.animator_luffy
        elif hasattr(self, 'chibi_animators') and name in self.chibi_animators:
            self.animator = self.chibi_animators[name]
        else:
            self.animator = self.animator_dragon
        self.update()

    @pyqtSlot(str)
    def trigger_anim_safe(self, state):
        if (
            self.current_character == "white_hamster"
            or isinstance(self.animator, WhiteHamsterAnimator)
        ):
            # Original six expression controls.
            if state in WhiteHamsterAnimator.EXPRESSIONS:
                self.animator.clear_special_action()
                self.animator.set_expression(state)
                self.animator.manual_action_lock = WhiteHamsterAnimator.ONE_SHOT_DURATIONS.get(
                    state,
                    1.5,
                )
                self.animator.elapsed = 0.0
                self.state_machine.force_state(state)
                self.update()
                return

            # Additional supplied sticker controls.
            if state in WhiteHamsterAnimator.ACTIONS:
                self.animator.set_special_action(
                    state,
                    duration=WhiteHamsterAnimator.ONE_SHOT_DURATIONS.get(
                        state,
                        2.0,
                    ),
                    persistent=False,
                )
                self.state_machine.force_state("idle")
                self.update()
                return

            # Manual jump.
            if state == "jump":
                self.animator.clear_special_action()
                self.animator.manual_action_lock = WhiteHamsterAnimator.ONE_SHOT_DURATIONS["jump"]
                self.animator.elapsed = 0.0
                self.state_machine.force_state("jump")
                self.update()
                return

            # Manual wander.
            if state == "wander":
                target = self.layout_manager.get_wander_target()
                self._white_auto_wander_active = True
                self._white_auto_wander_target = target
                self._white_auto_wander_x = float(self.x())
                self._white_auto_wander_y = float(self.y())
                self._white_auto_wander_clock = 0.0
                self.update()
                return

        if state in {"gum_stretch", "gear2", "gear3", "gear5"}:
            if hasattr(self.animator, "trigger_special"):
                self.animator.trigger_special(state)
            elif hasattr(self.animator_luffy, "trigger_special"):
                self.animator_luffy.trigger_special(state)
            self.state_machine.force_state("celebrate")
        else:
            self.state_machine.force_state(state)
        self.update()
        
    def say_safe(self, text):
        if not self.is_destroyed:
            self.say(text)

    def process_chat_safe(self, message):
        if not self.is_destroyed:
            self.process_chat(message)
            
    @pyqtSlot()
    def clear_chat_safe(self):
        if not self.is_destroyed:
            self.ai.clear_memory()
            self.say("Memory cleared!")
            
    def _finish_chat(self):
        """Cooldown timer callback."""
        self.is_generating = False
        if self.control_panel:
            self.control_panel.set_ai_loading(False)

    def process_chat(self, message):
        """Processes a chat message by showing a thinking indicator and running the AI in a background thread."""
        if not message or not message.strip():
            return
        
        if self.is_generating:
            return
            
        self.is_generating = True
        if self.control_panel:
            self.control_panel.set_ai_loading(True)
        
        # Show thinking indicator
        self.say("Thinking...", force_state="think")
        
        # Run AI generation in background to prevent UI freeze
        thread = threading.Thread(target=self._run_ai_chat, args=(message,))
        thread.daemon = True
        thread.start()

    def _run_ai_chat(self, message):
        """Runs in background thread to call Gemini API."""
        try:
            response = self.ai.generate_response(message)
            if not self.is_destroyed:
                QMetaObject.invokeMethod(self, "say_safe", Qt.QueuedConnection, Q_ARG(str, response))
        except Exception:
            if not self.is_destroyed:
                QMetaObject.invokeMethod(self, "say_safe", Qt.QueuedConnection, Q_ARG(str, "Oops, my brain broke!"))
        finally:
            if not self.is_destroyed:
                # 1 second cooldown
                QTimer.singleShot(1000, self._finish_chat)

    @pyqtSlot(int, int)
    def start_pomo_safe(self, w, b):
        self.pomodoro.work_duration = w * 60
        self.pomodoro.break_duration = b * 60
        self.pomodoro.start_work()
        
    @pyqtSlot()
    def stop_pomo_safe(self):
        self.pomodoro.stop()
        
    @pyqtSlot()
    def feed_safe(self):
        if self.current_character == "dog":
            self.say("Yummy! Woof woof!", force_state='eat')
        elif "cat" in self.current_character:
            self.say("Yummy fish! Purrrr...", force_state='clean')
        elif self.current_character == "luffy":
            self.say("MEAAAT! *nom nom nom*", force_state='celebrate')
        elif self.current_character == "white_hamster":
            if hasattr(self.animator, "set_special_action"):
                self.animator.set_special_action(
                    "eat",
                    duration=WhiteHamsterAnimator.ONE_SHOT_DURATIONS["eat"],
                    persistent=False,
                )
            self.say("CRUNCH CRUNCH!")
        elif self.current_character == "yellow_guardian_hamster":
            self.say("CRUNCH.", force_state='happy')
        elif self.current_character == "hamster":
            self.say("Crunch crunch! Delicious!", force_state='celebrate')
        elif self.current_character == "fox":
            self.say("Yum yum! Tasty treat!", force_state='celebrate')
        elif self.current_character == "penguin":
            self.say("Fish! Flap flap flap!", force_state='celebrate')
        elif self.current_character == "panda":
            self.say("Bamboo snack! Omnomnom!", force_state='celebrate')
        elif self.current_character == "owl":
            self.say("Hoot! A tasty morsel!", force_state='celebrate')
        else:
            self.say("Yummy! Rawr!", force_state='celebrate')
        
    @pyqtSlot()
    def annoy_safe(self):
        self.mood.annoy()
        self.state_machine.force_state('annoyed')
        self.say("Grrr... put me down!")
        
    @pyqtSlot()
    def sleep_safe(self):
        self.mood.energy = 0
        self.state_machine.force_state('sleep')
        
    @pyqtSlot(float)
    def update_wander_safe(self, val):
        self.wander_chance = val

    def say(self, text, force_state=None):
        if getattr(self, 'is_stopped', False):
            return
        now = time.time()
        min_interval = getattr(self, '_speech_interval', 6.0)
        if hasattr(self, '_last_speech_time') and (now - self._last_speech_time) < min_interval:
            if not force_state:
                return
        self._last_speech_time = now
        self._speech_interval = random.uniform(5.0, 7.0)
        self.typing_engine.start_typing(text, on_complete=lambda: self.state_machine.request_state(force_state or 'idle') if force_state else None)

    def check_battery(self):
        power_status = SYSTEM_POWER_STATUS()
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(power_status)):
            if power_status.ACLineStatus == 0 and power_status.BatteryLifePercent <= 20:
                self.say(get_character_line(self.current_character, "lowBattery"))

    def do_fire_breathe(self):
        if getattr(self, 'is_stopped', False):
            return
        if self.pomodoro.is_running:
            return
        if self.typing_engine.timer.isActive() or self.is_generating:
            return
        
        current_state = self.state_machine.get_state()
        if current_state in ['idle', 'sit', 'wander']:
            if self.current_character == "dragon":
                # Dragon fire breathe - DO NOT TOUCH!
                self.state_machine.request_state('fire_breathe')
                QTimer.singleShot(2000, lambda: self.state_machine.request_state('idle'))
            elif self.current_character == "dog":
                # Dog: calm, relaxed occasional jump (once every ~20s)
                if random.random() < 0.25:
                    self.state_machine.request_state('jump')
                    QTimer.singleShot(2200, lambda: self.state_machine.request_state('idle'))
            elif "cat" in self.current_character:
                # Cats: calm, relaxed occasional pounce/lick_paw (once every ~20s)
                if random.random() < 0.25:
                    action = 'pounce' if random.random() < 0.5 else 'clean'
                    self.state_machine.request_state(action)
                    QTimer.singleShot(2200, lambda: self.state_machine.request_state('idle'))

    def _reset_white_hamster_autonomous_movement(self):
        self._white_auto_wander_active = False
        self._white_auto_wander_target = None
        self._white_auto_wander_x = None
        self._white_auto_wander_y = None
        self._white_auto_wander_clock = 0.0
        self._white_auto_next_wander = random.uniform(7.0, 12.0)

    def _update_white_hamster_autonomous_movement(self):
        if self.current_character != "white_hamster":
            return

        if getattr(self, "is_stopped", False):
            return

        if self.drag_position is not None:
            self._white_auto_wander_active = False
            self._white_auto_wander_target = None
            self._white_auto_wander_x = None
            self._white_auto_wander_y = None
            return

        if self.pomodoro.is_running:
            return

        if self.typing_engine.timer.isActive():
            return

        if self.is_generating:
            return

        if (
            getattr(self.mood, "sleep_on_video", True)
            and self.video_detector.is_watching_video()
        ):
            self._white_auto_wander_active = False
            self._white_auto_wander_target = None
            return

        dt = 0.025

        if not self._white_auto_wander_active:
            self._white_auto_wander_clock += dt

            if (
                self._white_auto_wander_clock
                >= self._white_auto_next_wander
            ):
                target = self.layout_manager.get_wander_target()

                current_x = float(self.x())
                current_y = float(self.y())

                dx = float(target.x()) - current_x
                dy = float(target.y()) - current_y
                distance = (dx * dx + dy * dy) ** 0.5

                if distance < 180.0:
                    self._white_auto_wander_clock = 0.0
                    self._white_auto_next_wander = random.uniform(
                        3.0,
                        5.0,
                    )
                    return

                self._white_auto_wander_active = True
                self._white_auto_wander_target = target
                self._white_auto_wander_x = current_x
                self._white_auto_wander_y = current_y
                self._white_auto_wander_clock = 0.0
                return

        if (
            self._white_auto_wander_active
            and self._white_auto_wander_target is not None
        ):
            target = self._white_auto_wander_target

            dx = (
                float(target.x())
                - self._white_auto_wander_x
            )
            dy = (
                float(target.y())
                - self._white_auto_wander_y
            )

            distance = (dx * dx + dy * dy) ** 0.5

            if distance <= 6.0:
                self._white_auto_wander_active = False
                self._white_auto_wander_target = None
                self._white_auto_wander_x = None
                self._white_auto_wander_y = None
                self._white_auto_wander_clock = 0.0
                self._white_auto_next_wander = random.uniform(
                    7.0,
                    12.0,
                )
                return

            speed = 2.2

            self._white_auto_wander_x += (
                dx / distance
            ) * speed

            self._white_auto_wander_y += (
                dy / distance
            ) * speed

            direction = 1.0 if dx >= 0 else -1.0

            if hasattr(self.animator, "set_facing"):
                self.animator.set_facing(direction)

            self.move(
                int(round(self._white_auto_wander_x)),
                int(round(self._white_auto_wander_y)),
            )


    def _white_autonomous_tick(self, dt, idle_secs):
        """
        White Meme Hamster-specific autonomous behavior.

        The automatic six-expression cycle remains inside the animator.
        This method only connects real user activity to the supplied
        action-specific sticker sprites.
        """

        if self.current_character != "white_hamster":
            return

        # Keyboard activity -> ALWAYS show the supplied reading/typing sticker.
        if idle_secs < 2.0:
            self.mood.register_typing(dt)

            if hasattr(self.animator, "set_special_action"):
                self.animator.set_special_action(
                    "type",
                    persistent=True,
                )

            return

        self.mood.stop_typing()

        # Release the typing sticker as soon as typing stops.
        if (
            hasattr(self.animator, "special_action")
            and self.animator.special_action == "type"
        ):
            self.animator.clear_special_action()

    def do_behavior_tick(self):
        # Update logic that happens regularly
        if getattr(self, 'is_stopped', False):
            return

        if self.current_character == "white_hamster":
            return

        if self.timer.isActive() and self.idle_timer.isActive():
            
            idle_secs = self.keyboard_tracker.get_idle_time()
            current_state = self.state_machine.get_state()
            
            if self.pomodoro.is_running:
                return # Skip autonomous behaviors if locked in Pomodoro
            
            # Check Video Detection
            watching_video = getattr(self.mood, 'sleep_on_video', True) and self.video_detector.is_watching_video()
            if watching_video:
                self._was_watching_video = True
                if current_state != 'sleep':
                    self.state_machine.force_state('sleep')
                    self.speech_bubble.hide()
                return

            # WAKE UP: video just ended — always wake regardless of idle time
            if self._was_watching_video and current_state == 'sleep':
                self._was_watching_video = False
                self.mood.wake_up_refresh()
                self.state_machine.force_state('wake')
                self.say("Movie over! I'm awake!")
                return
            self._was_watching_video = False

            if self.current_character == "white_hamster":
                if idle_secs < 1.0 and current_state == "sleep":
                    self.mood.wake_up_refresh()
                    self.state_machine.force_state("idle")
                    return

                self._white_autonomous_tick(
                    0.5,
                    idle_secs,
                )
                return

            # WAKE UP on ANY system input (mouse or keyboard)
            if idle_secs < 1.0 and current_state == 'sleep':
                self.mood.wake_up_refresh()
                self.state_machine.force_state('wake')
                self.say("You're back!")
                return
                
            # 1. Check Global Activity (Working)
            if idle_secs < 2.0:
                self.mood.register_typing(0.5)
                if self.mood.is_exhausted_from_typing():
                    if current_state != 'exhausted':
                        self.state_machine.force_state('exhausted')
                else:
                    # Randomly switch between typing, focusing, and thinking while user works
                    if current_state not in ['type', 'focus', 'think']:
                        self.state_machine.request_state('focus')
                    elif random.random() < 0.1:
                        self.state_machine.request_state('think')
                    elif random.random() < 0.2:
                        self.state_machine.request_state('focus')
                    elif random.random() < 0.2:
                        self.state_machine.request_state('type')
            else:
                self.mood.stop_typing()
                
                # 2. Short pause (user is reading, moving mouse, or thinking)
                if idle_secs < 10.0:
                    if current_state == 'exhausted':
                        self.state_machine.force_state('sit')
                    elif current_state in ['type', 'focus']:
                        if random.random() < 0.3:
                            self.state_machine.request_state('think')
                        else:
                            self.state_machine.request_state('idle')
                            
                    # Allow wandering during short pauses!
                    if current_state in ['idle', 'think'] and random.random() < 0.04:
                        self.wander_target = self.layout_manager.get_wander_target()
                        self.state_machine.request_state('wander')
                
                # 3. Truly idle (hands off mouse/keyboard for > 10s)
                else:
                    if current_state in ['type', 'focus', 'think', 'exhausted']:
                        self.state_machine.force_state('idle')
                        
                    if current_state == 'idle':
                        dt = datetime.datetime.now()
                        now = time.time()
                        if not hasattr(self, '_last_idle_dialogue_time'):
                            self._last_idle_dialogue_time = 0
                            
                        # Only attempt dialogue pops if at least 5.0 to 7.0 seconds passed
                        if (now - self._last_idle_dialogue_time) >= random.uniform(5.0, 7.0):
                            if self.mood.is_hungry() and random.random() < 0.3:
                                self._last_idle_dialogue_time = now
                                self.say(get_character_line(self.current_character, "hungry"))
                            elif self.mood.is_sleepy():
                                self.state_machine.force_state('sleep')
                                if self.mood.is_late_night():
                                    self._last_idle_dialogue_time = now
                                    self.say(get_character_line(self.current_character, "lateNight"))
                            elif random.random() < getattr(self, 'wander_chance', 0.05):
                                self.wander_target = self.layout_manager.get_wander_target()
                                self.state_machine.request_state('wander')
                            elif random.random() < 0.2:
                                self._last_idle_dialogue_time = now
                                self.say(get_character_line(self.current_character, "idle"))
                            self.state_machine.request_state('sit')
                            
                    elif current_state == 'sit':
                        if random.random() < 0.05:
                            self.state_machine.request_state('idle')

    def update_frame(self):
        if getattr(self, 'is_stopped', False):
            return
        self.state_machine.tick(0.025)
        self.animator.update()
        if self.current_character == "white_hamster":
            self._update_white_hamster_autonomous_movement()
        self.layout_manager.update()
        
        if self.pomodoro.is_running and not self.typing_engine.timer.isActive():
            # Update the speech bubble text directly without triggering typing animation
            prefix = "Break" if self.pomodoro.is_break else "Focus"
            self.speech_bubble.set_text(f"{prefix}: {self.pomodoro.get_remaining_str()}")
            self.speech_bubble.show()
            
        if self.state_machine.get_state() == 'wander' and self.wander_target:
            if self._wander_float_x is None or self._wander_float_y is None:
                self._wander_float_x = float(self.x())
                self._wander_float_y = float(self.y())

            dx = float(self.wander_target.x()) - self._wander_float_x
            dy = float(self.wander_target.y()) - self._wander_float_y
            dist = (dx**2 + dy**2)**0.5
            if dist < 5:
                self.state_machine.request_state('idle')
                self.wander_target = None
                self._wander_float_x = None
                self._wander_float_y = None
            else:
                direction = 1.0 if dx >= 0 else -1.0
                if hasattr(self.animator, 'set_facing'):
                    self.animator.set_facing(direction)

                speed = 3.0
                self._wander_float_x += (dx / dist) * speed
                self._wander_float_y += (dy / dist) * speed
                self.move(int(round(self._wander_float_x)), int(round(self._wander_float_y)))
        else:
            self._wander_float_x = None
            self._wander_float_y = None
                
        self.update() # trigger paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        dragon_rect = self.layout_manager.get_dragon_rect()
        self.animator.draw(painter, dragon_rect)
        
        if self.speech_bubble.is_visible():
            bubble_rect = self.layout_manager.get_bubble_rect(self.speech_bubble.get_text_size())
            self.speech_bubble.draw(painter, bubble_rect)
            
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        if getattr(self, 'is_stopped', False):
            start_act = menu.addAction("Start Pet")
            start_act.triggered.connect(self.start_pet_safe)
        else:
            stop_act = menu.addAction("Stop Pet")
            stop_act.triggered.connect(self.stop_pet_safe)
        menu.addSeparator()
        panel_act = menu.addAction("Control Panel")
        panel_act.triggered.connect(self.show_control_panel)
        menu.addSeparator()
        quit_act = menu.addAction("Quit")
        quit_act.triggered.connect(QApplication.instance().quit)
        menu.exec_(event.globalPos())

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Show the chat overlay, passing the pet's global position and width
            global_pos = self.mapToGlobal(self.rect().topLeft())
            self.chat_overlay.show_overlay(global_pos.x(), global_pos.y(), self.width())
            event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.current_character == "white_hamster":
                self._white_auto_wander_active = False
                self._white_auto_wander_target = None
            self._wander_float_x = None
            self._wander_float_y = None
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.state_machine.force_state('drag')
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            new_pos = event.globalPos() - self.drag_position
            clamped_pos = self.layout_manager.clamp_window_pos(new_pos)
            self.move(clamped_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            self.mood.register_interaction()
            
            self.click_count += 1
            if self.click_count > 4:
                self.mood.annoy()
                
            if self.mood.is_annoyed():
                self.state_machine.force_state('annoyed')
                self.say("Grrr... put me down!")
                self.click_count = 0
            else:
                if self.current_character == "dog":
                    actions = [
                        ("react_click", "Woof!"),
                        ("celebrate", "Happy tail wag!"),
                        ("jump", "Boing boing!"),
                        ("bark", "Arf arf!"),
                    ]
                elif "cat" in self.current_character:
                    actions = [
                        ("meow", "Meow~"),
                        ("happy", "Purrrrr..."),
                        ("pounce", "Pounce!"),
                        ("clean", "*Licks paw*"),
                    ]
                elif self.current_character == "luffy":
                    actions = [
                        ("celebrate", "Shishishi! I'm gonna be King of the Pirates!"),
                        ("react_click", "Yahoo!"),
                        ("curious", "Is that meat?!"),
                    ]
                elif self.current_character == "white_hamster":
                    self.chibi_animators["white_hamster"].set_expression("smile")
                    self._white_expression_elapsed = 0.0
                    if hasattr(self, "_white_expression_cycle") and "smile" in self._white_expression_cycle:
                        self._white_expression_index = self._white_expression_cycle.index("smile")
                    self.say("hehe.", force_state="idle")
                    self.update()
                    event.accept()
                    return
                elif hasattr(self, 'chibi_animators') and self.current_character in self.chibi_animators:
                    line = get_character_line(self.current_character, "click")
                    actions = [
                        ("celebrate", line or "Yay!"),
                        ("react_click", line or "Hehe!"),
                    ]
                else:
                    actions = [
                        ("react_click", "Hehe!"),
                        ("celebrate", "Wheee!"),
                        ("fire_breathe", "RAWR!"),
                        ("curious", "What are we doing?"),
                    ]
                action, text = random.choice(actions)
                self.say(text, force_state=action)
                
            QTimer.singleShot(2000, lambda: setattr(self, 'click_count', 0))
            event.accept()
