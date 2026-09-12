import math
import random
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont
from PyQt5.QtCore import Qt, QPointF, QRectF


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
        elif self.kind in ['heart', 'sleepy_dot']:
            self.vy += -2.5 * dt

    def alive(self):
        return self.life > 0

    def draw(self, painter: QPainter):
        if not self.alive():
            return
        ratio = max(0.0, min(1.0, self.life / self.max_life))
        alpha = int(240 * ratio)
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.kind == 'heart':
            painter.setPen(Qt.NoPen)
            col = QColor(255, 110, 140, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setBrush(col)
            sz = self.size * (0.8 + 0.3 * (1.0 - ratio))
            p = QPainterPath()
            p.moveTo(self.x, self.y)
            p.cubicTo(self.x - sz, self.y - sz, self.x - sz * 1.4, self.y + sz * 0.4, self.x, self.y + sz * 1.3)
            p.cubicTo(self.x + sz * 1.4, self.y + sz * 0.4, self.x + sz, self.y - sz, self.x, self.y)
            painter.drawPath(p)

        elif self.kind in ['sparkle', 'star']:
            col = QColor(255, 215, 75, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = max(1.5, self.size * ratio)
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))
            painter.setPen(QPen(col, 1.2))
            painter.drawLine(QPointF(self.x - sz * 1.3, self.y), QPointF(self.x + sz * 1.3, self.y))
            painter.drawLine(QPointF(self.x, self.y - sz * 1.3), QPointF(self.x, self.y + sz * 1.3))

        elif self.kind in ['dust', 'landing_puff']:
            col = QColor(200, 195, 190, int(alpha * 0.55)) if self.color is None else QColor(self.color)
            col.setAlpha(int(alpha * 0.55))
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = self.size * (1.0 + (1.0 - ratio) * 0.9)
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))

        elif self.kind == 'sleepy_dot':
            col = QColor(160, 175, 215, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = max(1.5, self.size * (0.65 + 0.35 * ratio))
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))

        painter.restore()


class DogAnimator:
    def __init__(self, state_machine):
        self.state_machine = state_machine
        
        # Puppy Colors matching the cute puppy image
        self.body_color = QColor(255, 255, 255)
        self.ear_color = QColor(218, 172, 128)  # Warm tan / brown
        self.ear_dark = QColor(190, 145, 105)
        self.outline_color = QColor(45, 30, 25)  # Dark brown outline
        self.blush_color = QColor(255, 182, 193)  # Pink cheeks
        self.tongue_color = QColor(255, 110, 130)  # Pink tongue
        self.eye_color = QColor(30, 20, 20)
        self.laptop_color = QColor(200, 205, 215)
        self.laptop_screen = QColor(40, 45, 60)

        # Lightweight transient effect particles (bounded to <= 12)
        self.particles = []
        self._spawn_timer = 0.0

    def draw_contact_shadow(self, painter, y_offset=0.0, width=54.0, alpha=45):
        """Draws subtle soft contact shadow on the ground."""
        painter.save()
        painter.setPen(Qt.NoPen)
        shadow_width = max(22.0, width * (1.0 - min(abs(y_offset) / 60.0, 0.35)))
        painter.setBrush(QColor(0, 0, 0, alpha))
        painter.drawEllipse(
            QRectF(
                -shadow_width / 2.0,
                -4.0,
                shadow_width,
                8.0
            )
        )
        painter.restore()

    def update(self):
        dt = 0.025
        self._spawn_timer += dt

        # Update and cull particles
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

        # Controlled particle spawn based on active state (never exceed 12)
        if len(self.particles) < 12 and self._spawn_timer >= 0.22:
            state = self.state_machine.get_state()
            t = self.state_machine.time_in_state

            if state in ['celebrate', 'happy']:
                self._spawn_timer = 0.0
                kind = 'heart' if random.random() < 0.35 else 'sparkle'
                self.particles.append(
                    VisualParticle(
                        x=random.uniform(-22, 22),
                        y=random.uniform(-95, -60),
                        kind=kind,
                        life=0.55,
                        vx=random.uniform(-12, 12),
                        vy=random.uniform(-18, -8),
                        size=random.uniform(4.0, 6.5)
                    )
                )
            elif state == 'sleep' and random.random() < 0.4:
                self._spawn_timer = 0.0
                self.particles.append(
                    VisualParticle(
                        x=28 + random.uniform(-4, 6),
                        y=-85 + random.uniform(-6, 2),
                        kind='sleepy_dot',
                        life=0.75,
                        vx=random.uniform(2, 8),
                        vy=random.uniform(-14, -6),
                        size=random.uniform(3.0, 5.0)
                    )
                )

    def draw(self, painter: QPainter, rect):
        state = self.state_machine.get_state()
        t = self.state_machine.time_in_state
        
        painter.save()
        painter.translate(rect.center().x(), rect.bottom())
        
        scale_y = 1.0
        scale_x = 1.0
        y_offset = 0.0
        rotation = 0.0
        tail_angle = math.sin(t * 12) * 20  # Tail wagging
        ear_flop = math.sin(t * 4) * 4
        is_sitting = False
        tongue_out = False
        barking = False
        is_eating = False
        
        if state == 'idle':
            scale_y = 1.0 + 0.02 * math.sin(t * 3)
            scale_x = 1.0 - 0.01 * math.sin(t * 3)
            tail_angle = math.sin(t * 8) * 15
            ear_flop = math.sin(t * 3) * 2.5
        elif state in ['tongue_out', 'happy']:
            scale_y = 1.0 + 0.03 * math.sin(t * 6)
            y_offset = -5 * abs(math.sin(t * 8))
            tongue_out = True
            tail_angle = math.sin(t * 18) * 35  # Super fast happy tail wag
            ear_flop = math.sin(t * 8) * 5
        elif state in ['sit', 'sit_down']:
            is_sitting = True
            scale_y = 0.92
            scale_x = 1.03
            y_offset = 4
            tail_angle = math.sin(t * 6) * 25
            ear_flop = math.sin(t * 2) * 2
        elif state in ['bark', 'celebrate']:
            y_offset = -18 * abs(math.sin(t * 10))
            barking = True
            tongue_out = True
            tail_angle = math.sin(t * 20) * 40
            ear_flop = math.sin(t * 10) * 7
        elif state == 'jump':
            # Smooth, gentle, cute parabolic jump with squash & stretch settling
            jump_t = (t * 2.0) % 1.5
            if jump_t < 1.0:
                y_offset = -24 * math.sin(jump_t * math.pi)
                rotation = -4 * math.cos(jump_t * math.pi)
                scale_y = 1.06 if y_offset < -8 else 0.94
                scale_x = 0.95 if y_offset < -8 else 1.05
            else:
                y_offset = 3 * math.sin((jump_t - 1.0) * math.pi * 2)
                scale_y = 0.93
                scale_x = 1.06
                rotation = 0.0
            ear_flop = math.sin(t * 6) * 8
            tongue_out = True
            tail_angle = math.sin(t * 12) * 30
        elif state == 'eat':
            is_sitting = True
            is_eating = True
            tongue_out = True
            tail_angle = math.sin(t * 15) * 30
            scale_y = 0.93 + 0.02 * math.sin(t * 12)
        elif state == 'fetch':
            y_offset = -10 * abs(math.sin(t * 18))
            scale_x = 1.05
            ear_flop = 12
            tail_angle = math.sin(t * 22) * 35
        elif state == 'sleep':
            scale_y = 0.90 + 0.015 * math.sin(t * 2)
            scale_x = 1.05
            y_offset = 8
            is_sitting = True
            tail_angle = 5 + math.sin(t * 2) * 3
            ear_flop = 3
        elif state == 'exhausted':
            scale_y = 0.88 + 0.01 * math.sin(t * 1.5)
            scale_x = 1.08
            y_offset = 10
            is_sitting = True
        elif state == 'wake':
            scale_y = 1.0 + 0.1 * math.sin(t * 5) * max(0, 1 - t)
            tail_angle = math.sin(t * 15) * 30
            ear_flop = math.sin(t * 6) * 6
        elif state == 'react_click':
            y_offset = -15 * math.sin(t * 15) if t < 0.2 else 0
            tongue_out = True
            ear_flop = 8 * math.sin(t * 15) if t < 0.3 else 0
        elif state in ['drag', 'react_drag']:
            scale_y = 1.15
            scale_x = 0.88
            ear_flop = 14
            tail_angle = 15 * math.sin(t * 8)
        elif state == 'focus':
            scale_y = 1.0 + 0.01 * math.sin(t * 2)
            is_sitting = True
            tail_angle = math.sin(t * 4) * 8
        elif state == 'type':
            # Dog sits happily while text prints
            is_sitting = True
            tail_angle = math.sin(t * 12) * 25
            tongue_out = True
            scale_y = 0.94 + 0.02 * math.sin(t * 6)
        elif state == 'annoyed':
            rotation = 8 * math.sin(t * 20) if t < 0.5 else 0
            ear_flop = 6 * math.sin(t * 16)
        elif state == 'wander':
            y_offset = -12 * abs(math.sin(t * 12))
            rotation = 4 * math.sin(t * 6)
            ear_flop = math.sin(t * 12) * 8
            tail_angle = math.sin(t * 14) * 20

        # Grounded Contact Shadow (drawn on base floor before character translate)
        shadow_base_w = 64.0 if is_sitting else 54.0
        self.draw_contact_shadow(painter, y_offset=y_offset, width=shadow_base_w, alpha=42)

        # Character Transform
        painter.translate(0, y_offset)
        painter.scale(scale_x, scale_y)
        painter.rotate(rotation)
        
        # Setup Pen & Brushes
        pen = QPen(self.outline_color, 3.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # 1. DRAW TAIL
        painter.save()
        painter.translate(25, -25 if not is_sitting else -15)
        painter.rotate(tail_angle)
        tail_path = QPainterPath()
        tail_path.moveTo(0, 0)
        tail_path.cubicTo(15, -10, 20, -25, 10, -35)
        tail_path.cubicTo(0, -25, 5, -10, 0, 0)
        painter.setBrush(QBrush(self.ear_color))
        painter.drawPath(tail_path)
        painter.restore()
        
        # 2. DRAW LEGS / FEET
        painter.setBrush(QBrush(self.body_color))
        if is_sitting:
            # Back feet tucked in
            painter.drawEllipse(QRectF(-35, -18, 22, 18))
            painter.drawEllipse(QRectF(13, -18, 22, 18))
            # Front feet
            painter.drawEllipse(QRectF(-18, -14, 16, 14))
            painter.drawEllipse(QRectF(2, -14, 16, 14))
        else:
            # Standing / Running / Jumping feet
            spd = 18 if state in ['fetch', 'jump'] else 12
            leg_bounce = math.sin(t * spd) * (6 if state in ['fetch', 'jump'] else 4)
            painter.drawRoundedRect(QRectF(-28, -20 + leg_bounce, 18, 20), 8, 8)
            painter.drawRoundedRect(QRectF(10, -20 - leg_bounce, 18, 20), 8, 8)
            
        # 3. DRAW BODY
        body_rect = QRectF(-32, -55, 64, 45) if not is_sitting else QRectF(-30, -50, 60, 42)
        painter.setBrush(QBrush(self.body_color))
        painter.drawRoundedRect(body_rect, 22, 22)
        
        # 4. DRAW HEAD (Big cute puppy head)
        head_y = -75 if not is_sitting else -70
        if is_eating:
            head_y += math.sin(t * 12) * 6  # Eating bob
            
        head_rect = QRectF(-45, head_y - 45, 90, 75)
        painter.drawRoundedRect(head_rect, 35, 35)
        
        # 5. DRAW FLOPPY EARS
        # Left Ear
        painter.save()
        painter.translate(-38, head_y - 30)
        painter.rotate(-10 + ear_flop)
        ear_left = QPainterPath()
        ear_left.moveTo(0, 0)
        ear_left.cubicTo(-25, 5, -30, 45, -10, 55)
        ear_left.cubicTo(5, 45, 10, 20, 0, 0)
        painter.setBrush(QBrush(self.ear_color))
        painter.drawPath(ear_left)
        painter.restore()
        
        # Right Ear
        painter.save()
        painter.translate(38, head_y - 30)
        painter.rotate(10 - ear_flop)
        ear_right = QPainterPath()
        ear_right.moveTo(0, 0)
        ear_right.cubicTo(25, 5, 30, 45, 10, 55)
        ear_right.cubicTo(-5, 45, -10, 20, 0, 0)
        painter.setBrush(QBrush(self.ear_color))
        painter.drawPath(ear_right)
        painter.restore()
        
        # 6. EYES & BLUSH CHEEKS
        eye_y = head_y - 12
        if state == 'sleep':
            # Sleeping curved eyes ( ^ ^ )
            painter.setPen(QPen(self.outline_color, 3, Qt.SolidLine, Qt.RoundCap))
            left_eye_path = QPainterPath()
            left_eye_path.moveTo(-24, eye_y)
            left_eye_path.quadTo(-17, eye_y - 8, -10, eye_y)
            painter.drawPath(left_eye_path)
            
            right_eye_path = QPainterPath()
            right_eye_path.moveTo(10, eye_y)
            right_eye_path.quadTo(17, eye_y - 8, 24, eye_y)
            painter.drawPath(right_eye_path)
            painter.setPen(pen)  # Restore pen
        else:
            # Big Shiny Pupil Eyes
            painter.setBrush(QBrush(self.eye_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(-24, eye_y - 10, 14, 18))
            painter.drawEllipse(QRectF(10, eye_y - 10, 14, 18))
            
            # Eye Shine (white sparkles)
            painter.setBrush(QBrush(Qt.white))
            painter.drawEllipse(QRectF(-22, eye_y - 8, 5, 6))
            painter.drawEllipse(QRectF(-18, eye_y + 2, 3, 3))
            painter.drawEllipse(QRectF(12, eye_y - 8, 5, 6))
            painter.drawEllipse(QRectF(16, eye_y + 2, 3, 3))
            painter.setPen(pen)
            
        # Pink Blush Cheeks
        painter.setBrush(QBrush(self.blush_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(-34, eye_y + 4, 11, 7))
        painter.drawEllipse(QRectF(23, eye_y + 4, 11, 7))
        painter.setPen(pen)
        
        # 7. NOSE & MOUTH
        nose_y = head_y + 2
        painter.setBrush(QBrush(self.outline_color))
        painter.drawRoundedRect(QRectF(-5, nose_y - 4, 10, 7), 3, 3)
        
        # Mouth
        mouth_path = QPainterPath()
        mouth_path.moveTo(-8, nose_y + 6)
        mouth_path.quadTo(-4, nose_y + 10, 0, nose_y + 6)
        mouth_path.quadTo(4, nose_y + 10, 8, nose_y + 6)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(mouth_path)
        
        # 8. TONGUE OUT (If panting / happy / barking / eating / jumping)
        if tongue_out or state in ['happy', 'tongue_out', 'celebrate', 'react_click', 'jump', 'eat']:
            painter.setBrush(QBrush(self.tongue_color))
            painter.setPen(QPen(self.outline_color, 2))
            tongue_rect = QRectF(-5, nose_y + 7, 10, 12 + math.sin(t * 10) * 2)
            painter.drawRoundedRect(tongue_rect, 5, 5)
            
        # 9. BARK WAVES ("WOOF!")
        if barking or state == 'bark':
            painter.setPen(QPen(self.outline_color, 3))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            painter.drawText(QPointF(35, head_y - 30), "WOOF!")
            
        # 10. EATING TREAT / BONE FX
        if is_eating:
            painter.setBrush(QBrush(QColor(220, 200, 160)))
            painter.setPen(QPen(self.outline_color, 2))
            painter.drawRoundedRect(QRectF(-12, nose_y + 12, 24, 8), 4, 4)

        # 11. SLEEP Zzz
        if state in ['sleep', 'exhausted']:
            painter.setPen(QPen(self.ear_dark, 3))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            painter.drawText(QPointF(30, head_y - 45 - (t * 20 % 20)), "Zzz")

        # Draw active transient particles
        for p in self.particles:
            p.draw(painter)
            
        painter.restore()
