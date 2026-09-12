import math
import random
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont, QPixmap
from PyQt5.QtCore import Qt, QPointF, QRectF
from ui.animator import DragonAnimator


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def ease_in_out_sine(x):
    x = max(0.0, min(1.0, x))
    return -(math.cos(math.pi * x) - 1.0) / 2.0


def ping_pong01(x):
    x = x % 2.0
    return x if x <= 1.0 else 2.0 - x


def ease_out_back(x):
    c1 = 1.70158
    c3 = c1 + 1.0
    return 1.0 + c3 * (x - 1.0)**3 + c1 * (x - 1.0)**2


def draw_rubber_arm(painter, shoulder, target, width=9.0, bend_override=None, outline_col=None, skin_col=None):
    sx, sy = shoulder
    tx, ty = target

    dx = tx - sx
    dy = ty - sy
    length = math.hypot(dx, dy)

    if length < 0.01:
        return

    nx = -dy / length
    ny = dx / length

    bend = bend_override if bend_override is not None else min(16.0, length * 0.18)

    p = QPainterPath()
    p.moveTo(sx + nx * width, sy + ny * width)
    p.quadTo(
        sx + dx * 0.45 + nx * bend,
        sy + dy * 0.45 + ny * bend,
        tx + nx * (width * 0.72),
        ty + ny * (width * 0.72)
    )
    p.quadTo(
        tx - nx * (width * 0.72),
        ty - ny * (width * 0.72),
        sx - nx * width,
        sy - ny * width
    )
    p.closeSubpath()

    painter.save()
    if outline_col:
        painter.setPen(QPen(outline_col, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    if skin_col:
        painter.setBrush(skin_col)
    painter.drawPath(p)
    painter.restore()


class VisualParticle:
    def __init__(self, x, y, kind, life=0.55, vx=0.0, vy=-12.0, size=4.0, color=None):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.life = float(life)
        self.max_life = float(life)
        self.vx = float(vx)
        self.vy = float(vy)
        self.size = float(size)
        self.color = color

    def update(self, dt=0.025):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.kind in ['dust', 'landing_puff']:
            self.vy += 14.0 * dt
        elif self.kind in ['sparkle', 'star']:
            self.vy += 3.0 * dt
        elif self.kind in ['steam', 'smoke_ribbon']:
            self.vy += -4.0 * dt
        elif self.kind in ['sleepy_dot']:
            self.vy += -3.0 * dt

    def alive(self):
        return self.life > 0

    def draw(self, painter: QPainter):
        if not self.alive():
            return
        ratio = max(0.0, min(1.0, self.life / self.max_life))
        alpha = int(240 * ratio)
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.kind == 'star':
            col = QColor(255, 220, 60, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = max(2.0, self.size * ratio)
            p = QPainterPath()
            p.moveTo(self.x, self.y - sz * 1.4)
            p.quadTo(self.x, self.y, self.x + sz * 1.4, self.y)
            p.quadTo(self.x, self.y, self.x, self.y + sz * 1.4)
            p.quadTo(self.x, self.y, self.x - sz * 1.4, self.y)
            p.quadTo(self.x, self.y, self.x, self.y - sz * 1.4)
            painter.drawPath(p)

        elif self.kind == 'sparkle':
            col = QColor(255, 235, 120, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = max(1.5, self.size * ratio)
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))

        elif self.kind in ['steam', 'smoke_ribbon']:
            col = QColor(255, 255, 255, int(alpha * 0.5)) if self.color is None else QColor(self.color)
            col.setAlpha(int(alpha * 0.5))
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = self.size * (0.8 + 0.6 * (1.0 - ratio))
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))

        elif self.kind == 'sleepy_dot':
            col = QColor(165, 180, 220, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = max(1.5, self.size * (0.65 + 0.35 * ratio))
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))

        painter.restore()


class SpriteAnimator:
    def __init__(self, state_machine, image_path="assets/luffy.png"):
        self.state_machine = state_machine
        self.image_path = image_path
        self.pixmap = QPixmap(image_path)
        if not self.pixmap.isNull():
            self.pixmap = self.pixmap.scaledToHeight(150, Qt.SmoothTransformation)

        # Reusable laptop and fire breath renderer for compatibility
        self.dummy_dragon = DragonAnimator(state_machine)

        # Canonical Luffy Color Palette
        self.c_outline = QColor(44, 28, 22)
        self.c_skin = QColor(254, 218, 186)
        self.c_skin_shadow = QColor(240, 196, 162)
        self.c_hair = QColor(24, 23, 28)
        self.c_hat = QColor(234, 188, 102)
        self.c_hat_dark = QColor(212, 162, 75)
        self.c_hat_band = QColor(204, 38, 38)
        self.c_vest = QColor(226, 44, 44)
        self.c_shorts = QColor(46, 108, 180)
        self.c_cuff = QColor(235, 240, 248)
        self.c_sandals = QColor(140, 92, 58)
        self.c_blush = QColor(255, 175, 180, 140)
        self.c_meat = QColor(180, 75, 45)
        self.c_bone = QColor(248, 245, 235)

        # Facing & Orientation
        self.facing = 1  # 1 = facing right, -1 = facing left

        # Special Action State
        self.special_action = None
        self.special_timer = 0.0
        self.elapsed = 0.0

        # Animation states & particles
        self.particles = []
        self._spawn_timer = 0.0
        self._blink_seed = random.uniform(1.0, 3.0)
        self._last_blink_time = 0.0
        self._blink_interval = random.uniform(2.5, 4.5)

    def reset_animation(self):
        self.elapsed = 0.0
        self.special_action = None
        self.special_timer = 0.0
        self.particles.clear()
        self._spawn_timer = 0.0
        self._last_blink_time = 0.0
        self._blink_interval = random.uniform(2.8, 4.8)

    def set_facing(self, direction):
        self.facing = 1 if direction >= 0 else -1

    def trigger_special(self, action):
        self.special_action = action
        self.special_timer = 0.0

    def clear_special(self):
        self.special_action = None
        self.special_timer = 0.0
        self.particles.clear()

    def draw_contact_shadow(self, painter, y_offset=0.0, width=54.0, alpha=45):
        painter.save()
        painter.setPen(Qt.NoPen)
        shadow_width = max(22.0, width * (1.0 - min(abs(y_offset) / 60.0, 0.35)))
        painter.setBrush(QColor(0, 0, 0, alpha))
        painter.drawEllipse(QRectF(-shadow_width / 2.0, -4.0, shadow_width, 8.0))
        painter.restore()

    def _draw_gear5_cloud_ring(self, painter, front=False, t=0.0):
        """Draw the white, cloud-like ribbon encircling Luffy's upper body in Gear 5."""
        painter.save()
        wobble = math.sin(t * 5.5) * 3.0
        painter.translate(0.0, wobble)

        path = QPainterPath()
        path.moveTo(-56.0, -74.0)
        path.cubicTo(-70.0, -88.0, -68.0, -106.0, -51.0, -110.0)
        path.cubicTo(-35.0, -114.0, -26.0, -101.0, -18.0, -92.0)
        path.cubicTo(-8.0, -106.0, 8.0, -106.0, 18.0, -92.0)
        path.cubicTo(26.0, -101.0, 35.0, -114.0, 51.0, -110.0)
        path.cubicTo(68.0, -106.0, 70.0, -88.0, 56.0, -74.0)
        path.cubicTo(47.0, -63.0, 31.0, -59.0, 19.0, -63.0)
        path.cubicTo(8.0, -67.0, -8.0, -67.0, -19.0, -63.0)
        path.cubicTo(-31.0, -59.0, -47.0, -63.0, -56.0, -74.0)
        path.closeSubpath()

        # Offset/trim by overlaying the torso later. The cloud itself is white, with a dark outline.
        painter.setPen(QPen(self.c_outline, 3.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawPath(path)

        # Individual soft lobes make the ring read as smoke/cloud rather than a solid belt.
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        lobes = [
            (-52, -98, 18), (-34, -103, 16), (-17, -94, 15),
            (17, -94, 15), (34, -103, 16), (52, -98, 18),
        ]
        for x, y, r in lobes:
            painter.drawEllipse(QRectF(x - r * 0.55, y - r * 0.42, r * 1.1, r * 0.84))

        # In front view, draw a small front-center cloud segment after the torso.
        if front:
            painter.setPen(QPen(self.c_outline, 3.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            front_path = QPainterPath()
            front_path.moveTo(-18, -80)
            front_path.cubicTo(-10, -70, -7, -63, 0, -60)
            front_path.cubicTo(7, -63, 10, -70, 18, -80)
            front_path.cubicTo(12, -75, 7, -75, 0, -70)
            front_path.cubicTo(-7, -75, -12, -75, -18, -80)
            front_path.closeSubpath()
            painter.drawPath(front_path)

        painter.restore()

    def update(self):
        dt = 0.025
        self.elapsed += dt
        self._spawn_timer += dt

        if self.special_action is not None:
            self.special_timer += dt
            # Auto-clear after duration
            durations = {
                "gum_stretch": 2.2,
                "gear2": 3.0,
                "gear3": 2.5,
                "gear5": 3.5
            }
            max_d = durations.get(self.special_action, 2.5)
            if self.special_timer >= max_d:
                self.clear_special()

        # Update and cull active particles
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

        # Spawn state-specific particles (capped at 12)
        if len(self.particles) < 12 and self._spawn_timer >= 0.2:
            state = self.state_machine.get_state()
            active_act = self.special_action or state

            if active_act in ['celebrate']:
                self._spawn_timer = 0.0
                kind = 'star' if random.random() < 0.6 else 'sparkle'
                self.particles.append(
                    VisualParticle(
                        x=random.uniform(-25, 25),
                        y=random.uniform(-110, -70),
                        kind=kind,
                        life=0.55,
                        vx=random.uniform(-16, 16),
                        vy=random.uniform(-20, -8),
                        size=random.uniform(4.5, 7.5)
                    )
                )
            elif active_act == 'gear2':
                # Steam puff ONLY during gear2
                self._spawn_timer = 0.0
                self.particles.append(
                    VisualParticle(
                        x=random.uniform(-16, 16),
                        y=random.uniform(-65, -15),
                        kind='steam',
                        life=0.6,
                        vx=random.uniform(-6, 6),
                        vy=random.uniform(-18, -8),
                        size=random.uniform(5.0, 8.5),
                        color=QColor(255, 220, 225, 180)
                    )
                )
            elif active_act == 'gear5':
                # Mythical smoke ribbon
                self._spawn_timer = 0.0
                self.particles.append(
                    VisualParticle(
                        x=random.uniform(-25, 25),
                        y=random.uniform(-115, -45),
                        kind='smoke_ribbon',
                        life=0.7,
                        vx=random.uniform(-10, 10),
                        vy=random.uniform(-14, -6),
                        size=random.uniform(7.0, 12.0),
                        color=QColor(255, 255, 255, 220)
                    )
                )
            elif active_act in ['sleep', 'exhausted'] and random.random() < 0.4:
                self._spawn_timer = 0.0
                self.particles.append(
                    VisualParticle(
                        x=26 + random.uniform(-4, 6),
                        y=-85 + random.uniform(-6, 2),
                        kind='sleepy_dot',
                        life=0.75,
                        vx=random.uniform(2, 6),
                        vy=random.uniform(-12, -5),
                        size=random.uniform(3.0, 5.0)
                    )
                )

    def draw(self, painter: QPainter, rect):
        state = self.state_machine.get_state()
        t = self.elapsed
        effective_action = self.special_action or state

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Origin at bottom center
        painter.translate(rect.center().x(), rect.bottom())

        # Facing scale
        painter.scale(self.facing, 1.0)

        # Easing & Kinematics
        scale_y = 1.0
        scale_x = 1.0
        y_offset = 0.0
        torso_tilt = 0.0
        head_lag = 0.0
        hat_lag = 0.0
        hat_tilt = 0.0

        # Gait/Limb parameters
        foot_x_l = -10.0
        foot_y_l = 0.0
        foot_x_r = 10.0
        foot_y_r = 0.0
        arm_mode = 'hips'
        rubber_stretch_ratio = 0.0

        # Facial Expression Defaults
        expression = 'normal'
        mouth_expression = 'smile'

        # Natural Randomized Blinking
        if t - self._last_blink_time > self._blink_interval:
            self._last_blink_time = t
            self._blink_interval = random.uniform(2.5, 4.5)
        is_blinking = (t - self._last_blink_time) < 0.18

        # Palettes for Gear modes
        skin_color = self.c_skin
        skin_shadow_color = self.c_skin_shadow
        hair_color = self.c_hair
        outline_color = self.c_outline
        vest_color = self.c_vest
        shorts_color = self.c_shorts
        cuff_color = self.c_cuff
        sandals_color = self.c_sandals
        is_gear5 = (effective_action == 'gear5')

        # ====================================================
        # SPECIAL ACTIONS
        # ====================================================
        if effective_action == 'gum_stretch':
            # Gum-Gum Pistol animation sequence
            st = self.special_timer
            arm_mode = 'gum_stretch'
            if st < 0.4:
                # Preparation: pull back
                prog = st / 0.4
                rubber_stretch_ratio = -0.35 * smoothstep(prog)
                scale_x = 1.06
                scale_y = 0.94
                y_offset = 2
                expression = 'determined'
                mouth_expression = 'determined'
                hat_tilt = -5 * prog
            elif st < 0.9:
                # Rapid extension with overshoot
                prog = (st - 0.4) / 0.5
                eased = ease_out_back(min(1.0, prog * 1.25))
                rubber_stretch_ratio = eased * 1.6
                scale_x = 0.95
                scale_y = 1.05
                y_offset = -3
                expression = 'determined'
                mouth_expression = 'wide_grin'
                hat_tilt = 8 * prog
            elif st < 1.4:
                # Hold at extension
                rubber_stretch_ratio = 1.6
                expression = 'determined'
                mouth_expression = 'wide_grin'
                hat_tilt = 6
            else:
                # Rubber recoil & return to idle
                prog = min(1.0, (st - 1.4) / 0.8)
                rubber_stretch_ratio = 1.6 * (1.0 - smoothstep(prog))
                bounce = math.sin(prog * math.pi * 3) * (1.0 - prog) * 0.12
                scale_x = 1.0 + bounce
                scale_y = 1.0 - bounce
                expression = 'happy'
                mouth_expression = 'smile'

        elif effective_action == 'gear2':
            # Gear 2: Second Gear (Pumped up red hue, steam, crouching ready stance)
            st = self.special_timer
            skin_color = QColor(255, 195, 185)  # Flushed pinkish
            scale_y = 0.88 + 0.04 * math.sin(st * 16.0)
            scale_x = 1.10 - 0.02 * math.sin(st * 16.0)
            y_offset = 5.0
            torso_tilt = 4.0
            hat_tilt = -6.0
            arm_mode = 'gear2_ready'
            expression = 'determined'
            mouth_expression = 'determined'

        elif effective_action == 'gear3':
            # Gear 3: Third Gear (Gigant Pistol balloon fist)
            st = self.special_timer
            arm_mode = 'gear3_giant'
            scale_y = 0.94 + 0.03 * math.sin(st * 8.0)
            scale_x = 1.06
            y_offset = 2.0
            expression = 'determined'
            mouth_expression = 'wide_grin'
            hat_tilt = -8.0

        elif effective_action == 'gear5':
            # Gear 5: complete white Nika silhouette, open laughing face, cloud ring.
            st = self.special_timer
            white = QColor(255, 255, 255)
            skin_color = white
            skin_shadow_color = QColor(238, 238, 238)
            hair_color = white
            vest_color = white
            shorts_color = white
            cuff_color = white
            sandals_color = white
            bounce = abs(math.sin(st * 7.5)) * 14.0
            y_offset = -bounce
            scale_y = 1.08 if bounce > 4.0 else 0.92
            scale_x = 0.94 if bounce > 4.0 else 1.08
            torso_tilt = math.sin(st * 5.0) * 5.0
            hat_tilt = 0.0
            arm_mode = 'gear5_dance'
            expression = 'gear5_laugh'
            mouth_expression = 'laughing'

        # ====================================================
        # NORMAL STATES
        # ====================================================
        elif state == 'wander':
            # 4-Phase Chibi Walk Cycle
            walk_speed = 7.5
            walk_phase = (t * walk_speed) % (math.pi * 2.0)

            stride = math.sin(walk_phase)
            stride_opp = math.sin(walk_phase + math.pi)

            lift_l = max(0.0, stride)
            lift_r = max(0.0, stride_opp)

            body_bob = -abs(math.sin(walk_phase)) * 2.8
            y_offset = body_bob

            foot_y_l = -lift_l * 5.5
            foot_y_r = -lift_r * 5.5
            foot_x_l = -10.0 + stride * 4.0
            foot_x_r = 10.0 + stride_opp * 4.0

            torso_tilt = stride * 2.0
            head_lag = -stride * 1.4
            hat_lag = -stride * 2.8
            hat_tilt = hat_lag

            arm_mode = 'walk_cycle'
            expression = 'blink' if is_blinking else 'normal'
            mouth_expression = 'smile'

        elif state == 'idle':
            # Idle breathing & subtle weight shift
            breath = math.sin(t * 3.0)
            scale_y = 1.0 + 0.024 * breath
            scale_x = 1.0 - 0.012 * breath
            hat_tilt = breath * 2.2
            arm_mode = 'hips'
            expression = 'blink' if is_blinking else 'normal'
            mouth_expression = 'smile'

        elif state == 'celebrate':
            # Joyful celebration jump
            jump_cycle = (t * 2.2) % 1.5
            if jump_cycle < 0.25:
                scale_y = 0.88
                scale_x = 1.12
                y_offset = 3.0
                hat_tilt = -3.0
            elif jump_cycle < 0.95:
                jump_t = (jump_cycle - 0.25) / 0.70
                y_offset = -28.0 * math.sin(jump_t * math.pi)
                scale_y = 1.10
                scale_x = 0.92
                hat_tilt = -10.0 * (1.0 - jump_t)
            else:
                scale_y = 0.94
                scale_x = 1.06
                y_offset = 2.0
            arm_mode = 'celebrate'
            expression = 'happy'
            mouth_expression = 'wide_grin'

        elif state in ['eat', 'hungry']:
            scale_y = 0.96 + 0.03 * math.sin(t * 10.0)
            scale_x = 1.04
            y_offset = -4.0 * abs(math.sin(t * 10.0))
            arm_mode = 'meat'
            expression = 'excited'
            mouth_expression = 'meat'

        elif state in ['sleep', 'exhausted']:
            scale_y = 0.90 + 0.015 * math.sin(t * 2.0)
            scale_x = 1.06
            y_offset = 8.0
            hat_tilt = 12.0
            arm_mode = 'hips'
            expression = 'sleep'
            mouth_expression = 'closed'

        elif state == 'wake':
            wake_phase = min(1.0, t / 1.5)
            if wake_phase < 0.4:
                scale_y = 0.92
                expression = 'sleep'
                mouth_expression = 'o_mouth'
            elif wake_phase < 0.7:
                scale_y = 1.08
                scale_x = 0.94
                y_offset = -8.0
                hat_tilt = -6.0
                expression = 'surprised'
                mouth_expression = 'wide_grin'
            else:
                scale_y = 1.0
                expression = 'happy'
                mouth_expression = 'smile'

        elif state == 'focus':
            scale_y = 0.97
            scale_x = 1.03
            y_offset = 3.0
            arm_mode = 'type'
            expression = 'focused'
            mouth_expression = 'determined'

        elif state in ['think', 'curious']:
            scale_y = 0.98
            scale_x = 1.02
            torso_tilt = 4.0
            head_lag = 4.0
            hat_tilt = 6.0
            arm_mode = 'think'
            expression = 'curious'
            mouth_expression = 'smile'

        elif state in ['annoyed']:
            scale_y = 0.96
            scale_x = 1.04
            torso_tilt = -3.0
            arm_mode = 'hips'
            expression = 'annoyed'
            mouth_expression = 'annoyed'

        elif state in ['drag', 'react_drag']:
            scale_y = 1.15
            scale_x = 0.88
            y_offset = -12.0
            hat_tilt = -8.0
            arm_mode = 'drag'
            expression = 'surprised'
            mouth_expression = 'o_mouth'

        elif state in ['react_click']:
            y_offset = -14.0 * math.sin(t * 15.0) if t < 0.25 else 0.0
            hat_tilt = -8.0 * math.sin(t * 15.0) if t < 0.25 else 0.0
            expression = 'happy'
            mouth_expression = 'wide_grin'

        # ----------------------------------------------------
        # 1. Contact Shadow / Gear 5 Cloud Ring
        # ----------------------------------------------------
        self.draw_contact_shadow(painter, y_offset=y_offset, width=54.0, alpha=45)
        if is_gear5:
            self._draw_gear5_cloud_ring(painter, front=False, t=t)

        # Apply root kinematic transformations
        painter.translate(0, y_offset)
        painter.scale(scale_x, scale_y)

        # ----------------------------------------------------
        # 2. LEGS & FEET (Layered under torso)
        # ----------------------------------------------------
        painter.setPen(QPen(outline_color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        # Blue Shorts Base
        painter.setBrush(shorts_color)
        shorts_path = QPainterPath()
        shorts_path.moveTo(-18, -48)
        shorts_path.lineTo(18, -48)
        shorts_path.lineTo(20, -28)
        shorts_path.lineTo(4, -28)
        shorts_path.lineTo(0, -36)
        shorts_path.lineTo(-4, -28)
        shorts_path.lineTo(-20, -28)
        shorts_path.closeSubpath()
        painter.drawPath(shorts_path)

        # White Fuzzy Cuffs
        painter.setBrush(cuff_color)
        painter.drawRoundedRect(QRectF(-22, -30, 18, 7), 3, 3)
        painter.drawRoundedRect(QRectF(4, -30, 18, 7), 3, 3)

        # Left Leg & Foot
        painter.setBrush(skin_color)
        painter.drawRoundedRect(QRectF(foot_x_l - 4, -24 + foot_y_l, 9, 18), 4, 4)
        # Sandal
        painter.setBrush(sandals_color)
        painter.drawRoundedRect(QRectF(foot_x_l - 7, -7 + foot_y_l, 14, 5), 2.5, 2.5)
        # Sandal strap
        painter.setPen(QPen(vest_color, 1.4))
        painter.drawLine(QPointF(foot_x_l - 3, -7 + foot_y_l), QPointF(foot_x_l, -10 + foot_y_l))
        painter.drawLine(QPointF(foot_x_l + 3, -7 + foot_y_l), QPointF(foot_x_l, -10 + foot_y_l))
        painter.setPen(QPen(outline_color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        # Right Leg & Foot
        painter.setBrush(skin_color)
        painter.drawRoundedRect(QRectF(foot_x_r - 5, -24 + foot_y_r, 9, 18), 4, 4)
        # Sandal
        painter.setBrush(sandals_color)
        painter.drawRoundedRect(QRectF(foot_x_r - 7, -7 + foot_y_r, 14, 5), 2.5, 2.5)
        # Sandal strap
        painter.setPen(QPen(vest_color, 1.4))
        painter.drawLine(QPointF(foot_x_r - 3, -7 + foot_y_r), QPointF(foot_x_r, -10 + foot_y_r))
        painter.drawLine(QPointF(foot_x_r + 3, -7 + foot_y_r), QPointF(foot_x_r, -10 + foot_y_r))
        painter.setPen(QPen(outline_color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        # ----------------------------------------------------
        # 3. TORSO & RED OPEN VEST
        # ----------------------------------------------------
        painter.save()
        painter.rotate(torso_tilt)

        # Bare chest/torso
        painter.setBrush(skin_color)
        painter.drawRoundedRect(QRectF(-17, -84, 34, 40), 10, 10)

        # Red sleeveless open vest
        painter.setBrush(vest_color)
        vest_l = QPainterPath()
        vest_l.moveTo(-18, -84)
        vest_l.lineTo(-8, -84)
        vest_l.lineTo(-14, -48)
        vest_l.lineTo(-19, -48)
        vest_l.closeSubpath()
        painter.drawPath(vest_l)

        vest_r = QPainterPath()
        vest_r.moveTo(18, -84)
        vest_r.lineTo(8, -84)
        vest_r.lineTo(14, -48)
        vest_r.lineTo(19, -48)
        vest_r.closeSubpath()
        painter.drawPath(vest_r)

        # Yellow button accents
        painter.setBrush(white if is_gear5 else QColor(245, 215, 60))
        painter.drawEllipse(QRectF(-15, -74, 3.5, 3.5))
        painter.drawEllipse(QRectF(-16, -60, 3.5, 3.5))

        # ----------------------------------------------------
        # 4. ARMS & RUBBER DEFORMATIONS
        # ----------------------------------------------------
        shoulder_l = (-17.0, -80.0)
        shoulder_r = (17.0, -80.0)

        if arm_mode == 'walk_cycle':
            # Opposite phase arm swings
            walk_phase = (t * 7.5) % (math.pi * 2.0)
            stride = math.sin(walk_phase)
            arm_swing_l = -stride * 12.0
            arm_swing_r = stride * 12.0

            target_l = (-24.0 + stride * 4.0, -60.0 + arm_swing_l)
            target_r = (24.0 - stride * 4.0, -60.0 + arm_swing_r)
            draw_rubber_arm(painter, shoulder_l, target_l, width=7.5, bend_override=stride * 4.0,
                            outline_col=outline_color, skin_col=skin_color)
            draw_rubber_arm(painter, shoulder_r, target_r, width=7.5, bend_override=-stride * 4.0,
                            outline_col=outline_color, skin_col=skin_color)
            # Fists
            painter.setBrush(skin_color)
            painter.drawEllipse(QRectF(target_l[0] - 5, target_l[1] - 5, 10, 10))
            painter.drawEllipse(QRectF(target_r[0] - 5, target_r[1] - 5, 10, 10))

        elif arm_mode == 'gum_stretch':
            # Left arm on hip
            target_l = (-26.0, -68.0)
            draw_rubber_arm(painter, shoulder_l, target_l, width=7.5, bend_override=-5.0,
                            outline_col=outline_color, skin_col=skin_color)
            painter.setBrush(skin_color)
            painter.drawEllipse(QRectF(-31, -73, 10, 10))

            # Right arm: rubber stretch trajectory
            target_x = 24.0 + rubber_stretch_ratio * 75.0
            target_y = -75.0 - rubber_stretch_ratio * 6.0
            draw_rubber_arm(painter, shoulder_r, (target_x, target_y), width=8.5, bend_override=8.0,
                            outline_col=outline_color, skin_col=skin_color)
            painter.setBrush(skin_color)
            fist_sz = 14.0 + min(6.0, abs(rubber_stretch_ratio) * 4.0)
            painter.drawEllipse(QRectF(target_x - fist_sz / 2.0, target_y - fist_sz / 2.0, fist_sz, fist_sz))

        elif arm_mode == 'gear2_ready':
            # Crouching three-point stance
            target_l = (-24.0, -42.0)
            target_r = (24.0, -42.0)
            draw_rubber_arm(painter, shoulder_l, target_l, width=8.0, bend_override=-6.0,
                            outline_col=outline_color, skin_col=skin_color)
            draw_rubber_arm(painter, shoulder_r, target_r, width=8.0, bend_override=6.0,
                            outline_col=outline_color, skin_col=skin_color)
            painter.setBrush(skin_color)
            painter.drawEllipse(QRectF(target_l[0] - 6, target_l[1] - 6, 12, 12))
            painter.drawEllipse(QRectF(target_r[0] - 6, target_r[1] - 6, 12, 12))

        elif arm_mode == 'gear3_giant':
            # Left arm back
            target_l = (-26.0, -70.0)
            draw_rubber_arm(painter, shoulder_l, target_l, width=7.5, bend_override=-4.0,
                            outline_col=outline_color, skin_col=skin_color)
            painter.drawEllipse(QRectF(-31, -75, 10, 10))

            # Right arm: GIGANT FIST!
            target_r = (48.0, -68.0)
            draw_rubber_arm(painter, shoulder_r, target_r, width=15.0, bend_override=10.0,
                            outline_col=outline_color, skin_col=skin_color)
            # Giant fist
            painter.setBrush(skin_color)
            painter.drawEllipse(QRectF(target_r[0] - 12, target_r[1] - 20, 36, 38))
            # Giant knuckles
            painter.setPen(QPen(outline_color, 2.0))
            painter.drawLine(QPointF(target_r[0] + 4, target_r[1] - 12), QPointF(target_r[0] + 16, target_r[1] - 12))
            painter.drawLine(QPointF(target_r[0] + 4, target_r[1] - 2), QPointF(target_r[0] + 18, target_r[1] - 2))
            painter.drawLine(QPointF(target_r[0] + 4, target_r[1] + 8), QPointF(target_r[0] + 16, target_r[1] + 8))
            painter.setPen(QPen(outline_color, 1.8))

        elif arm_mode == 'gear5_dance':
            # Joyful floating arms
            wave_l = math.sin(t * 8.0) * 14.0
            wave_r = math.cos(t * 8.0) * 14.0
            target_l = (-32.0, -90.0 + wave_l)
            target_r = (32.0, -90.0 + wave_r)
            draw_rubber_arm(painter, shoulder_l, target_l, width=8.5, bend_override=wave_l * 0.5,
                            outline_col=outline_color, skin_col=skin_color)
            draw_rubber_arm(painter, shoulder_r, target_r, width=8.5, bend_override=wave_r * 0.5,
                            outline_col=outline_color, skin_col=skin_color)
            painter.setBrush(skin_color)
            painter.drawEllipse(QRectF(target_l[0] - 6, target_l[1] - 6, 12, 12))
            painter.drawEllipse(QRectF(target_r[0] - 6, target_r[1] - 6, 12, 12))

        elif arm_mode == 'celebrate':
            # Double raised victory arms
            target_l = (-32.0, -118.0)
            target_r = (32.0, -118.0)
            draw_rubber_arm(painter, shoulder_l, target_l, width=7.5, bend_override=-10.0,
                            outline_col=outline_color, skin_col=skin_color)
            draw_rubber_arm(painter, shoulder_r, target_r, width=7.5, bend_override=10.0,
                            outline_col=outline_color, skin_col=skin_color)
            painter.setBrush(skin_color)
            painter.drawEllipse(QRectF(-38, -125, 12, 12))
            painter.drawEllipse(QRectF(26, -125, 12, 12))

        elif arm_mode == 'meat':
            # Holding bone meat up to mouth
            target_l = (-20.0, -78.0)
            target_r = (18.0, -78.0)
            draw_rubber_arm(painter, shoulder_l, target_l, width=7.5, bend_override=-4.0,
                            outline_col=outline_color, skin_col=skin_color)
            draw_rubber_arm(painter, shoulder_r, target_r, width=7.5, bend_override=4.0,
                            outline_col=outline_color, skin_col=skin_color)
            painter.setBrush(skin_color)
            painter.drawEllipse(QRectF(-25, -83, 10, 10))
            painter.drawEllipse(QRectF(13, -83, 10, 10))

            # Meat Prop
            mx, my = 20.0, -88.0
            painter.setBrush(self.c_bone)
            painter.drawRoundedRect(QRectF(mx - 14, my - 2, 28, 5), 2.5, 2.5)
            painter.drawEllipse(QRectF(mx - 18, my - 5, 7, 5))
            painter.drawEllipse(QRectF(mx - 18, my, 7, 5))
            painter.drawEllipse(QRectF(mx + 11, my - 5, 7, 5))
            painter.drawEllipse(QRectF(mx + 11, my, 7, 5))
            painter.setBrush(self.c_meat)
            painter.drawRoundedRect(QRectF(mx - 10, my - 11, 20, 22), 7, 7)

        elif arm_mode == 'drag':
            # Dragging: arms stretching upward toward cursor
            target_l = (-22.0, -112.0)
            target_r = (22.0, -112.0)
            draw_rubber_arm(painter, shoulder_l, target_l, width=7.0, bend_override=-4.0,
                            outline_col=outline_color, skin_col=skin_color)
            draw_rubber_arm(painter, shoulder_r, target_r, width=7.0, bend_override=4.0,
                            outline_col=outline_color, skin_col=skin_color)
            painter.setBrush(skin_color)
            painter.drawEllipse(QRectF(-27, -117, 10, 10))
            painter.drawEllipse(QRectF(17, -117, 10, 10))

        elif arm_mode == 'type':
            # Typing posture: hands hopping forward
            tbob = math.sin(t * 16.0) * 4.0
            target_l = (-14.0, -68.0 + tbob)
            target_r = (14.0, -68.0 - tbob)
            draw_rubber_arm(painter, shoulder_l, target_l, width=7.5, bend_override=-3.0,
                            outline_col=outline_color, skin_col=skin_color)
            draw_rubber_arm(painter, shoulder_r, target_r, width=7.5, bend_override=3.0,
                            outline_col=outline_color, skin_col=skin_color)
            painter.setBrush(skin_color)
            painter.drawEllipse(QRectF(target_l[0] - 5, target_l[1] - 5, 10, 10))
            painter.drawEllipse(QRectF(target_r[0] - 5, target_r[1] - 5, 10, 10))

        else:  # 'hips'
            target_l = (-28.0, -66.0)
            target_r = (28.0, -66.0)
            draw_rubber_arm(painter, shoulder_l, target_l, width=7.5, bend_override=-8.0,
                            outline_col=outline_color, skin_col=skin_color)
            draw_rubber_arm(painter, shoulder_r, target_r, width=7.5, bend_override=8.0,
                            outline_col=outline_color, skin_col=skin_color)
            painter.setBrush(skin_color)
            painter.drawEllipse(QRectF(-33, -71, 10, 10))
            painter.drawEllipse(QRectF(23, -71, 10, 10))

        painter.restore()  # End Torso tilt

        # ----------------------------------------------------
        # 5. HEAD & HAIR
        # ----------------------------------------------------
        head_y = -115.0

        painter.save()
        painter.translate(0, head_lag)

        # Back hair. Gear 5 uses a larger all-white cloud silhouette rather than black hair.
        painter.setBrush(hair_color)
        hair_back = QPainterPath()
        if is_gear5:
            hair_back.moveTo(-32, head_y + 18)
            hair_back.cubicTo(-48, head_y + 18, -52, head_y + 4, -43, head_y - 4)
            hair_back.cubicTo(-54, head_y - 14, -46, head_y - 27, -33, head_y - 25)
            hair_back.cubicTo(-35, head_y - 42, -21, head_y - 48, -10, head_y - 35)
            hair_back.cubicTo(0, head_y - 52, 14, head_y - 48, 18, head_y - 33)
            hair_back.cubicTo(35, head_y - 45, 46, head_y - 34, 43, head_y - 21)
            hair_back.cubicTo(56, head_y - 18, 56, head_y - 3, 44, head_y + 4)
            hair_back.cubicTo(53, head_y + 18, 40, head_y + 25, 28, head_y + 18)
            hair_back.cubicTo(10, head_y + 26, -12, head_y + 27, -32, head_y + 18)
            hair_back.closeSubpath()
        else:
            hair_back.moveTo(-34, head_y - 12)
            hair_back.lineTo(-44, head_y + 2)
            hair_back.lineTo(-34, head_y + 12)
            hair_back.lineTo(-42, head_y + 22)
            hair_back.lineTo(-28, head_y + 20)
            hair_back.lineTo(28, head_y + 20)
            hair_back.lineTo(42, head_y + 22)
            hair_back.lineTo(34, head_y + 12)
            hair_back.lineTo(44, head_y + 2)
            hair_back.lineTo(34, head_y - 12)
            hair_back.closeSubpath()
        painter.drawPath(hair_back)

        # Chibi Head Base
        painter.setBrush(skin_color)
        painter.drawRoundedRect(QRectF(-36, head_y - 25, 72, 54), 24, 24)

        # Ears
        painter.drawEllipse(QRectF(-40, head_y - 6, 10, 14))
        painter.drawEllipse(QRectF(30, head_y - 6, 10, 14))

        # Front bangs. Gear 5 has rounded cloud-like locks framing the face.
        painter.setBrush(hair_color)
        hair_front = QPainterPath()
        if is_gear5:
            hair_front.moveTo(-37, head_y - 17)
            hair_front.cubicTo(-28, head_y - 30, -17, head_y - 27, -11, head_y - 17)
            hair_front.cubicTo(-5, head_y - 29, 5, head_y - 31, 11, head_y - 17)
            hair_front.cubicTo(18, head_y - 28, 30, head_y - 27, 37, head_y - 17)
            hair_front.cubicTo(27, head_y - 6, 18, head_y - 4, 10, head_y - 12)
            hair_front.cubicTo(5, head_y - 2, -5, head_y - 2, -10, head_y - 12)
            hair_front.cubicTo(-18, head_y - 4, -28, head_y - 6, -37, head_y - 17)
            hair_front.closeSubpath()
        else:
            hair_front.moveTo(-36, head_y - 12)
            hair_front.lineTo(-28, head_y - 2)
            hair_front.lineTo(-20, head_y - 10)
            hair_front.lineTo(-10, head_y + 2)
            hair_front.lineTo(0, head_y - 8)
            hair_front.lineTo(10, head_y + 2)
            hair_front.lineTo(20, head_y - 10)
            hair_front.lineTo(28, head_y - 2)
            hair_front.lineTo(36, head_y - 12)
            hair_front.lineTo(30, head_y - 24)
            hair_front.lineTo(-30, head_y - 24)
            hair_front.closeSubpath()
        painter.drawPath(hair_front)

        # ----------------------------------------------------
        # 6. FACIAL EXPRESSIONS & SIGNATURE SCAR
        # ----------------------------------------------------
        eye_y = head_y + 2.0

        # Blush is omitted in Gear 5 so the transformed silhouette stays completely white.
        if not is_gear5:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.c_blush)
            painter.drawEllipse(QRectF(-26, eye_y + 5, 11, 6))
            painter.drawEllipse(QRectF(15, eye_y + 5, 11, 6))
        painter.setPen(QPen(outline_color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        # Signature Scar under left eye
        painter.save()
        painter.setPen(QPen(QColor(154, 59, 59), 1.6, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(-20, eye_y + 9), QPointF(-10, eye_y + 9))
        painter.drawLine(QPointF(-17, eye_y + 7), QPointF(-17, eye_y + 11))
        painter.drawLine(QPointF(-13, eye_y + 7), QPointF(-13, eye_y + 11))
        painter.restore()

        # Eyes
        if expression in ['sleep']:
            # (^ ^) curved eyes
            p_l = QPainterPath()
            p_l.moveTo(-24, eye_y + 2)
            p_l.quadTo(-16, eye_y - 5, -8, eye_y + 2)
            painter.drawPath(p_l)

            p_r = QPainterPath()
            p_r.moveTo(8, eye_y + 2)
            p_r.quadTo(16, eye_y - 5, 24, eye_y + 2)
            painter.drawPath(p_r)

        elif is_blinking or expression == 'blink':
            # Blinking line eyes
            painter.drawLine(QPointF(-24, eye_y), QPointF(-8, eye_y))
            painter.drawLine(QPointF(8, eye_y), QPointF(24, eye_y))

        else:
            # Large expressive round anime eyes
            eye_w = 14.0
            eye_h = 17.0
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(-23, eye_y - 8, eye_w, eye_h))
            painter.drawEllipse(QRectF(9, eye_y - 8, eye_w, eye_h))

            if is_gear5:
                # Gear 5 eyes: always OPEN, oversized, bright, with concentric ringed pupils.
                painter.setPen(QPen(QColor(170, 32, 32), 2.0))
                painter.setBrush(QColor(255, 92, 92))
                painter.drawEllipse(QRectF(-22, eye_y - 9, 18, 20))
                painter.drawEllipse(QRectF(8, eye_y - 9, 18, 20))
                painter.setPen(QPen(outline_color, 1.4))
                painter.setBrush(QColor(32, 24, 24))
                painter.drawEllipse(QRectF(-18, eye_y - 5, 9, 12))
                painter.drawEllipse(QRectF(9, eye_y - 5, 9, 12))
            else:
                painter.setBrush(self.c_hair)
                painter.drawEllipse(QRectF(-19, eye_y - 5, 8.5, 11.5))
                painter.drawEllipse(QRectF(11, eye_y - 5, 8.5, 11.5))

            # White highlights keep the eyes lively and unmistakably open.
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(-17, eye_y - 4, 3.5, 3.5))
            painter.drawEllipse(QRectF(13, eye_y - 4, 3.5, 3.5))
            painter.drawEllipse(QRectF(-15, eye_y + 1, 2.0, 2.0))
            painter.drawEllipse(QRectF(15, eye_y + 1, 2.0, 2.0))
            painter.setPen(QPen(outline_color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        # Eyebrows
        if expression == 'determined':
            painter.drawLine(QPointF(-24, eye_y - 10), QPointF(-10, eye_y - 6))
            painter.drawLine(QPointF(24, eye_y - 10), QPointF(10, eye_y - 6))
        elif expression == 'annoyed':
            painter.drawLine(QPointF(-24, eye_y - 11), QPointF(-9, eye_y - 7))
            painter.drawLine(QPointF(24, eye_y - 7), QPointF(9, eye_y - 11))
        elif expression == 'gear5_laugh':
            painter.drawLine(QPointF(-23, eye_y - 14), QPointF(-9, eye_y - 11))
            painter.drawLine(QPointF(9, eye_y - 11), QPointF(23, eye_y - 14))
        else:
            painter.drawLine(QPointF(-23, eye_y - 11), QPointF(-9, eye_y - 12))
            painter.drawLine(QPointF(9, eye_y - 12), QPointF(23, eye_y - 11))

        # Mouth
        mouth_y = head_y + 16.0
        if mouth_expression == 'laughing':
            # Gear 5: unmistakable huge laughing mouth with dark interior, teeth, and tongue.
            m_path = QPainterPath()
            m_path.moveTo(-18, mouth_y - 3)
            m_path.cubicTo(-9, mouth_y + 13, 9, mouth_y + 13, 18, mouth_y - 3)
            m_path.cubicTo(10, mouth_y + 1, -10, mouth_y + 1, -18, mouth_y - 3)
            m_path.closeSubpath()
            painter.setPen(QPen(outline_color, 1.8))
            painter.setBrush(QColor(38, 24, 25))
            painter.drawPath(m_path)
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            painter.drawRoundedRect(QRectF(-14, mouth_y - 1, 28, 6), 3, 3)
            painter.setBrush(QColor(245, 105, 125))
            painter.drawEllipse(QRectF(-9, mouth_y + 5, 18, 7))
            painter.setPen(QPen(outline_color, 1.6))
        elif mouth_expression == 'wide_grin':
            m_path = QPainterPath()
            m_path.moveTo(-16, mouth_y - 2)
            m_path.quadTo(0, mouth_y + 12, 16, mouth_y - 2)
            m_path.closeSubpath()
            painter.setBrush(Qt.white)
            painter.drawPath(m_path)
            painter.drawLine(QPointF(-14, mouth_y + 2), QPointF(14, mouth_y + 2))
        elif mouth_expression == 'o_mouth':
            painter.setBrush(QColor(180, 50, 50))
            painter.drawEllipse(QRectF(-5, mouth_y - 2, 10, 11))
        elif mouth_expression == 'determined':
            painter.drawLine(QPointF(-10, mouth_y + 2), QPointF(10, mouth_y + 1))
        elif mouth_expression == 'closed':
            painter.drawLine(QPointF(-6, mouth_y + 2), QPointF(6, mouth_y + 2))
        else:
            # Classic cheerful Luffy smile
            m_path = QPainterPath()
            m_path.moveTo(-11, mouth_y)
            m_path.quadTo(0, mouth_y + 6, 11, mouth_y)
            painter.drawPath(m_path)

        # ----------------------------------------------------
        # 7. STRAW HAT WITH SECONDARY MOTION
        # ----------------------------------------------------
        if not is_gear5:
            painter.save()
            # Secondary tilt & lag
            painter.translate(0, head_y - 24)
            painter.rotate(hat_tilt)

            # Hat Brim
            painter.setBrush(self.c_hat)
            painter.drawEllipse(QRectF(-48, -7, 96, 20))

            # Red Ribbon Band
            painter.setBrush(self.c_hat_band)
            painter.drawRoundedRect(QRectF(-26, -15, 52, 11), 3, 3)

            # Hat Crown (Dome)
            painter.setBrush(self.c_hat)
            crown_path = QPainterPath()
            crown_path.moveTo(-25, -12)
            crown_path.quadTo(0, -38, 25, -12)
            crown_path.closeSubpath()
            painter.drawPath(crown_path)

            # Straw Hat texture line
            painter.setPen(QPen(self.c_hat_dark, 1.2))
            painter.drawArc(QRectF(-20, -30, 40, 24), 30 * 16, 120 * 16)
            painter.restore()  # End Hat
        else:
            # No yellow/red hat in Gear 5. The cloud hair and white ring define the transformed silhouette.
            pass

        painter.restore()  # End Head

        if is_gear5:
            # Small foreground piece of the cloud ribbon so the ring visibly wraps around the torso.
            self._draw_gear5_cloud_ring(painter, front=True, t=t)

        # ----------------------------------------------------
        # 8. ACTIVE PARTICLES
        # ----------------------------------------------------
        for p in self.particles:
            p.draw(painter)

        painter.restore()  # End Root
