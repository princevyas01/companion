import time
from PyQt5.QtCore import QTimer
from core.dialogue import get_line

class PomodoroTimer:
    """Focus/Pomodoro timer that integrates with the dragon's behavior."""
    
    def __init__(self, window):
        self.window = window
        self.work_duration = 25 * 60   # 25 minutes
        self.break_duration = 5 * 60   # 5 minutes
        self.elapsed = 0
        self.is_running = False
        self.is_break = False
        self.timer = QTimer(self.window)
        self.timer.timeout.connect(self._tick)

    def start_work(self):
        self.elapsed = 0
        self.is_running = True
        self.is_break = False
        self.timer.start(1000)
        self.window.state_machine.force_state('focus')
        self.window.typing_engine.start_typing(get_line("pomodoroStart"))

    def start_break(self):
        self.elapsed = 0
        self.is_running = True
        self.is_break = True
        self.timer.start(1000)
        self.window.state_machine.force_state('break_time')
        self.window.typing_engine.start_typing(get_line("pomodoroEnd"))

    def stop(self):
        self.is_running = False
        self.timer.stop()
        self.window.state_machine.request_state('idle')

    def _tick(self):
        self.elapsed += 1
        duration = self.break_duration if self.is_break else self.work_duration
        
        if self.elapsed >= duration:
            self.timer.stop()
            self.is_running = False
            
            if self.is_break:
                self.window.state_machine.force_state('celebrate')
                self.window.typing_engine.start_typing(get_line("pomodoroStart"))
                QTimer.singleShot(3000, lambda: self.window.state_machine.request_state('idle'))
            else:
                self.window.state_machine.force_state('celebrate')
                self.window.typing_engine.start_typing(get_line("pomodoroEnd"))
                QTimer.singleShot(3000, self.start_break)

    def get_remaining_str(self):
        if not self.is_running:
            return ""
        duration = self.break_duration if self.is_break else self.work_duration
        remaining = max(0, duration - self.elapsed)
        mins = remaining // 60
        secs = remaining % 60
        prefix = "Break" if self.is_break else "Focus"
        return f"{prefix}: {mins:02d}:{secs:02d}"
