"""
Desktop Dog Pet — Animation Engine
PyQt5 + QPainter, fully vector (no images), single-instance-ready core.
Drop this in your PyInstaller project as dog_pet.py and import DogPet.
"""
import sys, math, random
from enum import Enum, auto
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QAction, QSystemTrayIcon
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QBrush, QPen, QFont, QIcon, QPixmap

try:
    import psutil
except ImportError:
    psutil = None


class DogState(Enum):
    IDLE = auto()
    WALK = auto()
    RUN = auto()
    SIT = auto()
    SLEEP = auto()
    JUMP = auto()
    EAT = auto()
    BARK = auto()
    DRAG = auto()
    HAPPY = auto()
    FETCH = auto()


class DogPet(QWidget):
    action_finished = pyqtSignal(DogState)   # emit when a one-shot action completes

    W, H = 160, 140
    FUR = QColor(139, 94, 60)
    FUR_DARK = QColor(105, 68, 42)
    BELLY = QColor(222, 184, 148)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(self.W, self.H)

        self.state = None
        self.frame = 0
        self.state_frame = 0
        self.facing = 1
        self.pos_x = 100.0
        self.jump_vel = 0.0
        self.jump_base_y = 0.0
        self._drag_offset = None
        self._pending_post_jump_state = None

        # 1. On app launch -> IDLE
        self.set_state(DogState.IDLE)

        # 2. Idle >6s w/ no interaction -> randomized via idle_timer
        self.timer = QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(16)   # 60 FPS
        self.idle_timer = QTimer(self); self.idle_timer.timeout.connect(self._idle_behavior); self.idle_timer.start(6000)

        # 9. CPU usage > 80% (psutil poll) -> set_state(DogState.RUN)
        self.cpu_timer = QTimer(self)
        self.cpu_timer.timeout.connect(self._check_cpu_usage)
        self.cpu_timer.start(2000)

        # 10. System idle > 5 min -> SLEEP
        self.sys_idle_timer = QTimer(self)
        self.sys_idle_timer.timeout.connect(self._check_system_idle)
        self.sys_idle_timer.start(5000)

        # 5, 6, 7. Tray & Context Menu Wiring
        self._setup_menus()

    # ---------------- state control ----------------
    def set_state(self, state: DogState):
        if state == self.state:
            return
        self.state = state
        self.state_frame = 0
        if state == DogState.JUMP:
            self.jump_vel = -9.0
            self.jump_base_y = 0.0
        if state in (DogState.WALK, DogState.RUN, DogState.FETCH):
            self.facing = random.choice([-1, 1])

    def _idle_behavior(self):
        if self.state == DogState.IDLE:
            self.set_state(random.choice(
                [DogState.SIT, DogState.SLEEP, DogState.BARK, DogState.WALK, DogState.IDLE]))

    # ---------------- triggers & integrations ----------------
    def _setup_menus(self):
        """Triggers 5, 6, 7: Right-click tray menu Feed, Play, Sleep"""
        self.tray_menu = QMenu()

        feed_action = QAction("Feed", self)
        feed_action.triggered.connect(lambda: self.set_state(DogState.EAT))

        play_action = QAction("Play", self)
        play_action.triggered.connect(lambda: self.set_state(DogState.FETCH))

        sleep_action = QAction("Sleep", self)
        sleep_action.triggered.connect(lambda: self.set_state(DogState.SLEEP))

        idle_action = QAction("Wake / Idle", self)
        idle_action.triggered.connect(lambda: self.set_state(DogState.IDLE))

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)

        self.tray_menu.addAction(feed_action)
        self.tray_menu.addAction(play_action)
        self.tray_menu.addAction(sleep_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(idle_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(exit_action)

        pixmap = QPixmap(16, 16)
        pixmap.fill(self.FUR)
        self.tray_icon = QSystemTrayIcon(QIcon(pixmap), self)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def contextMenuEvent(self, event):
        """Right-click on widget triggers context menu"""
        self.tray_menu.exec_(event.globalPos())

    def on_notification_received(self, notification=None):
        """Trigger 8: New notification received -> set_state(DogState.BARK)"""
        self.set_state(DogState.BARK)

    def trigger_notification(self, notification=None):
        """Alias for Trigger 8"""
        self.on_notification_received(notification)

    def _check_cpu_usage(self):
        """Trigger 9: CPU usage > 80% (psutil poll) -> set_state(DogState.RUN)"""
        if psutil is None:
            return
        try:
            cpu = psutil.cpu_percent(interval=None)
            if cpu > 80.0:
                self.set_state(DogState.RUN)
        except Exception:
            pass

    def _get_system_idle_seconds(self):
        """Trigger 10 helper: Get system idle time in seconds using Win32 API"""
        try:
            import ctypes
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                return millis / 1000.0
        except Exception:
            pass
        return 0.0

    def _check_system_idle(self):
        """Trigger 10: System idle > 5 min (300s) -> set_state(DogState.SLEEP)"""
        idle_sec = self._get_system_idle_seconds()
        if idle_sec >= 300.0:
            self.set_state(DogState.SLEEP)

    def trigger_work_session_end(self):
        """Trigger 11: Pomodoro/timer work-session end -> JUMP + HAPPY sequence"""
        self._pending_post_jump_state = DogState.HAPPY
        self.set_state(DogState.JUMP)

    def on_pomodoro_work_session_end(self):
        """Alias for Trigger 11"""
        self.trigger_work_session_end()

    # ---------------- main loop ----------------
    def _tick(self):
        self.frame += 1
        self.state_frame += 1

        if self.state == DogState.WALK:
            self.pos_x += 1.2 * self.facing
            self.move(int(self.pos_x), self.y())
            if self.state_frame > 180: self.set_state(DogState.IDLE)

        elif self.state == DogState.RUN:
            self.pos_x += 3.0 * self.facing
            self.move(int(self.pos_x), self.y())
            if self.state_frame > 120: self.set_state(DogState.IDLE)

        elif self.state == DogState.JUMP:
            self.jump_vel += 0.6
            self.jump_base_y += self.jump_vel
            if self.jump_base_y >= 0:
                self.jump_base_y = 0
                next_state = getattr(self, '_pending_post_jump_state', None)
                self._pending_post_jump_state = None
                if next_state:
                    self.set_state(next_state)
                else:
                    self.set_state(DogState.IDLE)

        elif self.state in (DogState.SIT, DogState.SLEEP, DogState.EAT,
                             DogState.BARK, DogState.HAPPY, DogState.FETCH):
            if self.state_frame > 240:
                finished = self.state
                self.set_state(DogState.IDLE)
                self.action_finished.emit(finished)

        self.update()

    # ---------------- painting ----------------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        t = self.frame
        cx, cy = self.W / 2, self.H / 2 + 10
        breathe = math.sin(t * 0.08) * 2
        jump_offset = self.jump_base_y if self.state == DogState.JUMP else 0

        p.save()
        p.translate(cx, cy + breathe + jump_offset)
        if self.facing < 0:
            p.scale(-1, 1)
        self._draw_tail(p, t)
        self._draw_legs(p, t)
        self._draw_body(p, t)
        self._draw_head(p, t)
        p.restore()

        if self.state == DogState.BARK and (self.state_frame // 10) % 2 == 0:
            self._draw_bark_fx(p, cx, cy - 40)
        if self.state == DogState.SLEEP:
            self._draw_zzz(p, cx + 30, cy - 50, t)

    def _draw_body(self, p, t):
        squash = 0.7 if self.state == DogState.SIT else 1.0
        path = QPainterPath()
        path.addRoundedRect(QRectF(-35, -20 * squash, 70, 40 * squash), 18, 18)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self.FUR)); p.drawPath(path)
        p.setBrush(QBrush(self.BELLY)); p.drawEllipse(QRectF(-20, -5, 40, 20 * squash))

    def _draw_head(self, p, t):
        head_bob = abs(math.sin(t * 0.3)) * 10 if self.state == DogState.EAT else 0
        if self.state == DogState.BARK:
            head_bob = -abs(math.sin(t * 0.5)) * 4
        hx, hy = 30, -15 + head_bob

        p.setBrush(QBrush(self.FUR)); p.drawEllipse(QRectF(hx - 18, hy - 18, 36, 36))

        ear_angle = 45 if self.state == DogState.SLEEP else 20
        p.setBrush(QBrush(self.FUR_DARK))
        p.save(); p.translate(hx - 10, hy - 15); p.rotate(-ear_angle)
        p.drawEllipse(QRectF(-6, -14, 12, 22)); p.restore()

        p.setBrush(QBrush(self.FUR)); p.drawEllipse(QRectF(hx + 8, hy - 4, 18, 14))
        p.setBrush(QBrush(QColor(40, 30, 25))); p.drawEllipse(QRectF(hx + 20, hy, 6, 6))

        if self.state in (DogState.BARK, DogState.EAT) and (t // 6) % 2 == 0:
            p.setBrush(QBrush(QColor(120, 40, 40)))
            p.drawEllipse(QRectF(hx + 10, hy + 6, 10, 8))

        if self.state == DogState.SLEEP:
            p.setPen(QPen(QColor(40, 30, 25), 2))
            p.drawLine(QPointF(hx - 6, hy - 2), QPointF(hx - 1, hy - 2))
            p.drawLine(QPointF(hx + 2, hy - 2), QPointF(hx + 7, hy - 2))
        else:
            blink = (t % 140) > 135
            p.setPen(Qt.NoPen); p.setBrush(QBrush(QColor(30, 20, 15)))
            if not blink:
                p.drawEllipse(QRectF(hx - 6, hy - 4, 6, 6))
                p.drawEllipse(QRectF(hx + 2, hy - 4, 6, 6))
            else:
                p.setPen(QPen(QColor(30, 20, 15), 2))
                p.drawLine(QPointF(hx - 6, hy - 1), QPointF(hx, hy - 1))
                p.drawLine(QPointF(hx + 2, hy - 1), QPointF(hx + 8, hy - 1))

    def _draw_tail(self, p, t):
        speed = {DogState.HAPPY: 0.9, DogState.FETCH: 0.7, DogState.BARK: 0.6}.get(
            self.state, 0.15 if self.state == DogState.IDLE else 0.05)
        if self.state == DogState.SLEEP:
            speed = 0
        angle = math.sin(t * speed) * 35
        p.save(); p.translate(-32, -5); p.rotate(angle - 20)
        p.setBrush(QBrush(self.FUR_DARK))
        path = QPainterPath()
        path.moveTo(0, 0)
        path.cubicTo(-15, -10, -25, -5, -30, 5)
        path.cubicTo(-25, 8, -12, 6, 0, 6)
        path.closeSubpath()
        p.drawPath(path); p.restore()

    def _draw_legs(self, p, t):
        p.setPen(Qt.NoPen); p.setBrush(QBrush(self.FUR_DARK))
        if self.state in (DogState.WALK, DogState.RUN, DogState.FETCH):
            spd = 0.5 if self.state == DogState.WALK else 0.9
            swing = math.sin(t * spd) * 12
            offsets = [swing, -swing, -swing, swing]
        else:
            offsets = [0, 0, 0, 0]
        base = [(-22, 18), (-8, 18), (10, 18), (24, 18)]
        for (bx, by), off in zip(base, offsets):
            leg_len = 8 if self.state == DogState.SIT else 16
            p.drawRoundedRect(QRectF(bx - 3, by, 6, leg_len + off * 0.2), 3, 3)

    def _draw_bark_fx(self, p, cx, cy):
        p.setPen(QPen(QColor(255, 255, 255, 200), 2))
        for r in (10, 18, 26):
            p.drawArc(QRectF(cx + 20 - r/2, cy - r/2, r, r), 30 * 16, 120 * 16)

    def _draw_zzz(self, p, x, y, t):
        p.setPen(QPen(QColor(80, 80, 80)))
        p.setFont(QFont("Arial", 12, QFont.Bold))
        off = (t % 60) / 60 * 15
        p.drawText(QPointF(x, y - off), "z")
        p.drawText(QPointF(x + 8, y - 10 - off), "Z")

    # ---------------- mouse interaction ----------------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_offset = e.pos()
            self.set_state(DogState.DRAG)

    def mouseMoveEvent(self, e):
        if self._drag_offset:
            self.move(self.mapToGlobal(e.pos() - self._drag_offset))

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_offset = None
            self.set_state(DogState.IDLE)

    def mouseDoubleClickEvent(self, e):
        self.set_state(DogState.HAPPY)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DogPet()
    pet.show()
    sys.exit(app.exec_())
