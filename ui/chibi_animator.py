import math
import random
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
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
        elif self.kind in ['sleepy_dot', 'heart']:
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
            
        elif self.kind == 'heart':
            col = QColor(255, 105, 140, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = max(2.5, self.size * ratio)
            p = QPainterPath()
            p.moveTo(self.x, self.y)
            p.cubicTo(self.x - sz, self.y - sz * 1.2, self.x - sz * 1.6, self.y + sz * 0.4, self.x, self.y + sz * 1.4)
            p.cubicTo(self.x + sz * 1.6, self.y + sz * 0.4, self.x + sz, self.y - sz * 1.2, self.x, self.y)
            painter.drawPath(p)
            
        elif self.kind in ['dust', 'sparkle']:
            col = QColor(255, 235, 140, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = max(1.5, self.size * ratio)
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))
            
        elif self.kind == 'sleepy_dot':
            col = QColor(160, 185, 230, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = max(1.5, self.size * (0.6 + 0.4 * ratio))
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))
            
        painter.restore()

class ChibiAnimalAnimator:
    """
    Unified procedural chibi animal animation engine.
    Supports Fox, Rabbit, Penguin, Hamster, Owl, and Panda.
    """
    def __init__(self, state_machine, species="fox"):
        self.state_machine = state_machine
        self.species = species.lower()
        
        # Shared Kinematics & Orientation
        self.facing = 1  # 1 = right, -1 = left
        self.particles = []
        self._spawn_timer = 0.0
        self._last_blink = 0.0
        self._blink_interval = random.uniform(2.8, 4.8)
        self.elapsed = 0.0

        # Standard Chibi Outlines & Blush
        self.c_outline = QColor(42, 32, 28)
        self.c_blush = QColor(255, 160, 175, 140)

    def reset_animation(self):
        self.elapsed = 0.0
        self._spawn_timer = 0.0
        self._last_blink = 0.0
        self._blink_interval = random.uniform(2.8, 4.8)
        self.particles.clear()

    def set_facing(self, direction):
        self.facing = 1 if direction >= 0 else -1

    def clear_special(self):
        self.particles.clear()

    def clear_particles(self):
        self.particles.clear()

    def draw_contact_shadow(self, painter, y_offset=0.0, width=50.0, alpha=45):
        painter.save()
        painter.setPen(Qt.NoPen)
        shadow_w = max(18.0, width * (1.0 - min(abs(y_offset) / 60.0, 0.40)))
        painter.setBrush(QColor(0, 0, 0, alpha))
        painter.drawEllipse(QRectF(-shadow_w / 2.0, -4.0, shadow_w, 8.0))
        painter.restore()

    def update(self):
        dt = 0.025
        self.elapsed += dt
        self._spawn_timer += dt
        
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]
        
        # Spawn bounded particles
        if len(self.particles) < 12 and self._spawn_timer >= 0.22:
            state = self.state_machine.get_state()
            if state in ['celebrate']:
                self._spawn_timer = 0.0
                kind = 'heart' if random.random() < 0.5 else 'star'
                self.particles.append(
                    VisualParticle(
                        x=random.uniform(-20, 20),
                        y=random.uniform(-90, -60),
                        kind=kind,
                        life=0.6,
                        vx=random.uniform(-14, 14),
                        vy=random.uniform(-18, -8),
                        size=random.uniform(4.5, 7.0)
                    )
                )
            elif state in ['sleep', 'exhausted'] and random.random() < 0.4:
                self._spawn_timer = 0.0
                self.particles.append(
                    VisualParticle(
                        x=22 + random.uniform(-3, 5),
                        y=-75 + random.uniform(-5, 2),
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
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(rect.center().x(), rect.bottom())
        painter.scale(self.facing, 1.0)
        
        # Natural blink check
        if t - self._last_blink > self._blink_interval:
            self._last_blink = t
            self._blink_interval = random.uniform(2.5, 4.5)
        is_blinking = (t - self._last_blink) < 0.16 or (state in ['sleep'])
        
        # Ground Contact Shadow
        self.draw_contact_shadow(painter, y_offset=0.0, width=54.0)
        
        # Species-specific procedural rendering
        if self.species == 'fox':
            self.draw_fox(painter, state, t, is_blinking)
        elif self.species == 'rabbit':
            self.draw_rabbit(painter, state, t, is_blinking)
        elif self.species == 'penguin':
            self.draw_penguin(painter, state, t, is_blinking)
        elif self.species == 'hamster':
            self.draw_hamster(painter, state, t, is_blinking)
        elif self.species == 'owl':
            self.draw_owl(painter, state, t, is_blinking)
        elif self.species == 'panda':
            self.draw_panda(painter, state, t, is_blinking)
        else:
            self.draw_fox(painter, state, t, is_blinking)
            
        # Particles
        for p in self.particles:
            p.draw(painter)
            
        painter.restore()

    # ========================================================
    # 1. KITSUNE FOX
    # ========================================================
    def draw_fox(self, painter: QPainter, state: str, t: float, is_blinking: bool):
        c_fur = QColor(234, 112, 38)
        c_bib = QColor(255, 245, 235)
        c_dark = QColor(58, 38, 32)
        
        # Gait / Stride
        y_offset = 0.0
        scale_x, scale_y = 1.0, 1.0
        walk_stride = 0.0
        tail_sway = math.sin(t * 3.5) * 8.0
        
        if state in ['wander', 'curious']:
            w_phase = (t * 7.0) % (math.pi * 2.0)
            walk_stride = math.sin(w_phase)
            y_offset = -abs(math.sin(w_phase)) * 2.5
            tail_sway = math.sin(w_phase) * 16.0
        elif state == 'celebrate':
            y_offset = -20.0 * abs(math.sin(t * 5.0))
            tail_sway = math.sin(t * 12.0) * 22.0
            scale_y = 1.08 if y_offset < -5 else 0.92
        elif state in ['sleep']:
            scale_y = 0.92
            y_offset = 4.0
            tail_sway = 2.0
            
        painter.save()
        painter.translate(0, y_offset)
        painter.scale(scale_x, scale_y)
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Fluffy Brush Tail
        painter.save()
        painter.translate(-14, -40)
        painter.rotate(-20 + tail_sway)
        p_tail = QPainterPath()
        p_tail.moveTo(0, 0)
        p_tail.quadTo(-38, -12, -44, -36)
        p_tail.quadTo(-32, -54, -14, -42)
        p_tail.quadTo(4, -24, 0, 0)
        p_tail.closeSubpath()
        painter.setBrush(c_fur)
        painter.drawPath(p_tail)
        # Tail white tip
        p_tip = QPainterPath()
        p_tip.moveTo(-34, -44)
        p_tip.lineTo(-44, -36)
        p_tip.lineTo(-30, -50)
        p_tip.closeSubpath()
        painter.setBrush(c_bib)
        painter.drawPath(p_tip)
        painter.restore()
        
        # Fox Body & Legs
        painter.setBrush(c_dark)
        # Back paws
        painter.drawRoundedRect(QRectF(-16 + walk_stride * 4, -12, 10, 14), 4, 4)
        painter.drawRoundedRect(QRectF(8 - walk_stride * 4, -12, 10, 14), 4, 4)
        
        # Chubby Torso
        painter.setBrush(c_fur)
        painter.drawRoundedRect(QRectF(-18, -60, 36, 46), 16, 16)
        
        # Cream chest bib
        painter.setBrush(c_bib)
        p_bib = QPainterPath()
        p_bib.moveTo(-9, -60)
        p_bib.lineTo(9, -60)
        p_bib.lineTo(13, -40)
        p_bib.lineTo(0, -28)
        p_bib.lineTo(-13, -40)
        p_bib.closeSubpath()
        painter.drawPath(p_bib)
        
        # Front paws
        painter.setBrush(c_dark)
        painter.drawRoundedRect(QRectF(-14 - walk_stride * 3, -16, 9, 18), 4, 4)
        painter.drawRoundedRect(QRectF(5 + walk_stride * 3, -16, 9, 18), 4, 4)
        
        # Fox Head
        head_y = -86.0
        head_tilt = math.sin(t * 3.0) * 3.0 if state in ['curious', 'idle'] else 0.0
        painter.save()
        painter.translate(0, head_y)
        painter.rotate(head_tilt)
        
        # Large Triangular Alert Ears
        painter.setBrush(c_dark)
        p_ear_l = QPainterPath()
        p_ear_l.moveTo(-24, -10)
        p_ear_l.lineTo(-32, -36)
        p_ear_l.lineTo(-10, -22)
        p_ear_l.closeSubpath()
        painter.drawPath(p_ear_l)
        
        p_ear_r = QPainterPath()
        p_ear_r.moveTo(24, -10)
        p_ear_r.lineTo(32, -36)
        p_ear_r.lineTo(10, -22)
        p_ear_r.closeSubpath()
        painter.drawPath(p_ear_r)
        
        # Inner ear cream
        painter.setBrush(c_bib)
        p_iear_l = QPainterPath()
        p_iear_l.moveTo(-22, -12)
        p_iear_l.lineTo(-28, -30)
        p_iear_l.lineTo(-12, -20)
        p_iear_l.closeSubpath()
        painter.drawPath(p_iear_l)
        
        p_iear_r = QPainterPath()
        p_iear_r.moveTo(22, -12)
        p_iear_r.lineTo(28, -30)
        p_iear_r.lineTo(12, -20)
        p_iear_r.closeSubpath()
        painter.drawPath(p_iear_r)
        
        # Head base
        painter.setBrush(c_fur)
        painter.drawRoundedRect(QRectF(-30, -24, 60, 44), 18, 18)
        
        # Cute cheek fluffs
        p_cheek = QPainterPath()
        p_cheek.moveTo(-30, 4)
        p_cheek.lineTo(-38, 10)
        p_cheek.lineTo(-28, 16)
        p_cheek.closeSubpath()
        painter.drawPath(p_cheek)
        
        p_cheek_r = QPainterPath()
        p_cheek_r.moveTo(30, 4)
        p_cheek_r.lineTo(38, 10)
        p_cheek_r.lineTo(28, 16)
        p_cheek_r.closeSubpath()
        painter.drawPath(p_cheek_r)
        
        # Cream Muzzle
        painter.setBrush(c_bib)
        painter.drawRoundedRect(QRectF(-16, -2, 32, 22), 11, 11)
        
        # Little Nose & Mouth
        painter.setBrush(c_dark)
        painter.drawEllipse(QRectF(-3.5, 0, 7, 5))
        painter.drawLine(QPointF(0, 5), QPointF(0, 8))
        painter.drawLine(QPointF(-4, 10), QPointF(0, 8))
        painter.drawLine(QPointF(4, 10), QPointF(0, 8))
        
        # Blush
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.c_blush)
        painter.drawEllipse(QRectF(-22, 2, 9, 5))
        painter.drawEllipse(QRectF(13, 2, 9, 5))
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Eyes
        if is_blinking:
            painter.drawLine(QPointF(-19, -4), QPointF(-7, -4))
            painter.drawLine(QPointF(7, -4), QPointF(19, -4))
        else:
            painter.setBrush(c_dark)
            painter.drawEllipse(QRectF(-18, -10, 10, 13))
            painter.drawEllipse(QRectF(8, -10, 10, 13))
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(-16, -8, 3.5, 3.5))
            painter.drawEllipse(QRectF(10, -8, 3.5, 3.5))
            painter.drawEllipse(QRectF(-13, -3, 2, 2))
            painter.drawEllipse(QRectF(13, -3, 2, 2))
            painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
        painter.restore()
        painter.restore()

    # ========================================================
    # 2. CHIBI BUNNY (RABBIT)
    # ========================================================
    def draw_rabbit(self, painter: QPainter, state: str, t: float, is_blinking: bool):
        c_fur = QColor(252, 250, 246)
        c_inner = QColor(248, 195, 208)
        c_dark = QColor(48, 36, 32)
        
        # Hop kinematics
        y_offset = 0.0
        scale_x, scale_y = 1.0, 1.0
        ear_lag = 0.0
        
        if state in ['wander', 'hop']:
            hop_phase = (t * 6.5) % 1.0
            if hop_phase < 0.65:
                jump_prog = hop_phase / 0.65
                y_offset = -22.0 * math.sin(jump_prog * math.pi)
                scale_y = 1.10
                scale_x = 0.92
                ear_lag = -12.0 * math.sin(jump_prog * math.pi)
            else:
                land_prog = (hop_phase - 0.65) / 0.35
                y_offset = 2.5 * math.sin(land_prog * math.pi)
                scale_y = 0.90
                scale_x = 1.10
                ear_lag = 6.0
        elif state == 'celebrate':
            y_offset = -24.0 * abs(math.sin(t * 6.0))
            ear_lag = -16.0 * math.sin(t * 6.0)
        elif state in ['sleep']:
            scale_y = 0.92
            y_offset = 4.0
            ear_lag = 12.0
            
        painter.save()
        painter.translate(0, y_offset)
        painter.scale(scale_x, scale_y)
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Fluffy Bunny Tail
        painter.setBrush(c_fur)
        painter.drawEllipse(QRectF(-26, -34, 14, 14))
        
        # Round Body & Paws
        painter.drawRoundedRect(QRectF(-18, -54, 36, 44), 18, 18)
        # Big feet
        painter.drawRoundedRect(QRectF(-18, -14, 14, 16), 6, 6)
        painter.drawRoundedRect(QRectF(4, -14, 14, 16), 6, 6)
        # Front paws
        painter.drawRoundedRect(QRectF(-12, -32, 9, 14), 4, 4)
        painter.drawRoundedRect(QRectF(3, -32, 9, 14), 4, 4)
        
        # Bunny Head & Ears
        head_y = -78.0
        painter.save()
        painter.translate(0, head_y)
        
        # Long Floppy/Upright Ears with spring lag
        painter.save()
        painter.translate(-12, -18)
        painter.rotate(-8 + ear_lag)
        p_ear_l = QPainterPath()
        p_ear_l.moveTo(-6, 0)
        p_ear_l.quadTo(-12, -38, 0, -48)
        p_ear_l.quadTo(12, -38, 6, 0)
        p_ear_l.closeSubpath()
        painter.setBrush(c_fur)
        painter.drawPath(p_ear_l)
        painter.setBrush(c_inner)
        painter.drawRoundedRect(QRectF(-3.5, -42, 7, 34), 3.5, 3.5)
        painter.restore()
        
        painter.save()
        painter.translate(12, -18)
        painter.rotate(8 - ear_lag)
        p_ear_r = QPainterPath()
        p_ear_r.moveTo(-6, 0)
        p_ear_r.quadTo(-12, -38, 0, -48)
        p_ear_r.quadTo(12, -38, 6, 0)
        p_ear_r.closeSubpath()
        painter.setBrush(c_fur)
        painter.drawPath(p_ear_r)
        painter.setBrush(c_inner)
        painter.drawRoundedRect(QRectF(-3.5, -42, 7, 34), 3.5, 3.5)
        painter.restore()
        
        # Chubby Face
        painter.setBrush(c_fur)
        painter.drawRoundedRect(QRectF(-28, -22, 56, 42), 20, 20)
        
        # Pink Nose & Twitch
        nose_twitch = math.sin(t * 12.0) * 1.5 if state in ['idle', 'nose_twitch'] else 0.0
        painter.setBrush(c_inner)
        painter.drawEllipse(QRectF(-3.5, -2 + nose_twitch, 7, 5))
        painter.drawLine(QPointF(0, 3 + nose_twitch), QPointF(0, 6 + nose_twitch))
        painter.drawLine(QPointF(-4, 7 + nose_twitch), QPointF(0, 6 + nose_twitch))
        painter.drawLine(QPointF(4, 7 + nose_twitch), QPointF(0, 6 + nose_twitch))
        
        # Blush
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.c_blush)
        painter.drawEllipse(QRectF(-20, 2, 8, 5))
        painter.drawEllipse(QRectF(12, 2, 8, 5))
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Big Shiny Eyes
        if is_blinking:
            painter.drawLine(QPointF(-18, -6), QPointF(-8, -6))
            painter.drawLine(QPointF(8, -6), QPointF(18, -6))
        else:
            painter.setBrush(c_dark)
            painter.drawEllipse(QRectF(-17, -12, 10, 13))
            painter.drawEllipse(QRectF(7, -12, 10, 13))
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(-15, -10, 3.5, 3.5))
            painter.drawEllipse(QRectF(9, -10, 3.5, 3.5))
            painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
        painter.restore()
        painter.restore()

    # ========================================================
    # 3. WADDLING PENGUIN
    # ========================================================
    def draw_penguin(self, painter: QPainter, state: str, t: float, is_blinking: bool):
        c_body = QColor(28, 34, 48)
        c_belly = QColor(255, 255, 255)
        c_beak = QColor(255, 140, 0)
        
        # Waddle cycle
        y_offset = 0.0
        waddle_tilt = 0.0
        wing_flap = 0.0
        if state in ['wander', 'waddle']:
            w_phase = (t * 6.5) % (math.pi * 2.0)
            waddle_tilt = math.sin(w_phase) * 11.0
            y_offset = -abs(math.sin(w_phase)) * 3.0
            wing_flap = math.cos(w_phase) * 14.0
        elif state == 'celebrate':
            y_offset = -16.0 * abs(math.sin(t * 6.0))
            wing_flap = math.sin(t * 18.0) * 28.0
        elif state in ['sleep']:
            y_offset = 3.0
            waddle_tilt = 4.0
            
        painter.save()
        painter.translate(0, y_offset)
        painter.rotate(waddle_tilt)
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Orange Flipper Feet
        painter.setBrush(c_beak)
        painter.drawRoundedRect(QRectF(-20, -12, 16, 12), 5, 5)
        painter.drawRoundedRect(QRectF(4, -12, 16, 12), 5, 5)
        
        # Flipper Wings (behind body)
        painter.setBrush(c_body)
        painter.save()
        painter.translate(-24, -50)
        painter.rotate(-15 + wing_flap)
        painter.drawRoundedRect(QRectF(-6, 0, 12, 28), 6, 6)
        painter.restore()
        
        painter.save()
        painter.translate(24, -50)
        painter.rotate(15 - wing_flap)
        painter.drawRoundedRect(QRectF(-6, 0, 12, 28), 6, 6)
        painter.restore()
        
        # Rounded Body & Head
        painter.setBrush(c_body)
        painter.drawRoundedRect(QRectF(-25, -84, 50, 76), 25, 25)
        
        # White Belly Oval
        painter.setBrush(c_belly)
        painter.drawEllipse(QRectF(-18, -66, 36, 54))
        
        # Cute Beak
        painter.setBrush(c_beak)
        p_beak = QPainterPath()
        p_beak.moveTo(-7, -56)
        p_beak.lineTo(7, -56)
        p_beak.lineTo(0, -46)
        p_beak.closeSubpath()
        painter.drawPath(p_beak)
        
        # Blush
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.c_blush)
        painter.drawEllipse(QRectF(-20, -56, 7, 5))
        painter.drawEllipse(QRectF(13, -56, 7, 5))
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Round Eyes
        if is_blinking:
            painter.drawLine(QPointF(-16, -64), QPointF(-8, -64))
            painter.drawLine(QPointF(8, -64), QPointF(16, -64))
        else:
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(-16, -70, 9, 12))
            painter.drawEllipse(QRectF(7, -70, 9, 12))
            painter.setBrush(c_body)
            painter.drawEllipse(QRectF(-14, -68, 6, 8))
            painter.drawEllipse(QRectF(8, -68, 6, 8))
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(-13, -67, 2.5, 2.5))
            painter.drawEllipse(QRectF(9, -67, 2.5, 2.5))
            painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
        painter.restore()

    # ========================================================
    # 4. CHEEKY HAMSTER
    # ========================================================
    def draw_hamster(self, painter: QPainter, state: str, t: float, is_blinking: bool):
        c_fur = QColor(228, 168, 98)
        c_belly = QColor(255, 248, 240)
        c_pink = QColor(248, 192, 202)
        c_dark = QColor(48, 36, 32)
        
        # Fast scurrying gait
        y_offset = 0.0
        scurry_step = 0.0
        cheek_bounce = 0.0
        if state in ['wander', 'scurry']:
            s_phase = (t * 14.0) % (math.pi * 2.0)
            scurry_step = math.sin(s_phase) * 5.0
            y_offset = -abs(math.sin(s_phase)) * 2.0
            cheek_bounce = math.sin(s_phase) * 1.5
        elif state == 'celebrate':
            y_offset = -18.0 * abs(math.sin(t * 6.0))
            cheek_bounce = math.sin(t * 12.0) * 3.0
        elif state in ['sleep']:
            y_offset = 5.0
            
        painter.save()
        painter.translate(0, y_offset)
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Tiny Paws
        painter.setBrush(c_pink)
        painter.drawRoundedRect(QRectF(-16 + scurry_step, -10, 8, 11), 3, 3)
        painter.drawRoundedRect(QRectF(8 - scurry_step, -10, 8, 11), 3, 3)
        
        # Extremely Round Body
        painter.setBrush(c_fur)
        painter.drawEllipse(QRectF(-28, -62, 56, 56))
        
        # White tummy
        painter.setBrush(c_belly)
        painter.drawEllipse(QRectF(-18, -48, 36, 40))
        
        # Tiny front hands holding sunflower seed
        painter.setBrush(c_pink)
        painter.drawEllipse(QRectF(-10, -32, 7, 7))
        painter.drawEllipse(QRectF(3, -32, 7, 7))
        
        # Sunflower seed
        painter.setBrush(QColor(60, 50, 45))
        p_seed = QPainterPath()
        p_seed.moveTo(0, -35)
        p_seed.lineTo(-4, -27)
        p_seed.lineTo(4, -27)
        p_seed.closeSubpath()
        painter.drawPath(p_seed)
        
        # Tiny Ears
        painter.setBrush(c_fur)
        painter.drawEllipse(QRectF(-26, -72, 14, 14))
        painter.drawEllipse(QRectF(12, -72, 14, 14))
        painter.setBrush(c_pink)
        painter.drawEllipse(QRectF(-23, -69, 8, 8))
        painter.drawEllipse(QRectF(15, -69, 8, 8))
        
        # Puffed Cheeks
        painter.setBrush(c_belly)
        painter.drawEllipse(QRectF(-31, -44 + cheek_bounce, 20, 18))
        painter.drawEllipse(QRectF(11, -44 + cheek_bounce, 20, 18))
        
        # Nose & Whiskers
        painter.setBrush(c_pink)
        painter.drawEllipse(QRectF(-3, -38, 6, 5))
        painter.drawLine(QPointF(-10, -36), QPointF(-24, -38))
        painter.drawLine(QPointF(-10, -34), QPointF(-24, -32))
        painter.drawLine(QPointF(10, -36), QPointF(24, -38))
        painter.drawLine(QPointF(10, -34), QPointF(24, -32))
        
        # Blush
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.c_blush)
        painter.drawEllipse(QRectF(-26, -38, 10, 6))
        painter.drawEllipse(QRectF(16, -38, 10, 6))
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Beady Black Eyes
        if is_blinking:
            painter.drawLine(QPointF(-16, -46), QPointF(-8, -46))
            painter.drawLine(QPointF(8, -46), QPointF(16, -46))
        else:
            painter.setBrush(c_dark)
            painter.drawEllipse(QRectF(-16, -52, 9, 11))
            painter.drawEllipse(QRectF(7, -52, 9, 11))
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(-14, -50, 3, 3))
            painter.drawEllipse(QRectF(9, -50, 3, 3))
            painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
        painter.restore()

    # ========================================================
    # 5. WISE CHIBI OWL
    # ========================================================
    def draw_owl(self, painter: QPainter, state: str, t: float, is_blinking: bool):
        c_feather = QColor(110, 78, 54)
        c_chest = QColor(252, 245, 235)
        c_beak = QColor(235, 155, 35)
        c_eyes = QColor(255, 184, 0)
        c_dark = QColor(42, 32, 28)
        
        # Head turning rotation
        head_rotate = 0.0
        wing_flap = 0.0
        y_offset = 0.0
        if state in ['wander', 'head_turn']:
            w_phase = (t * 5.0) % (math.pi * 2.0)
            y_offset = -abs(math.sin(w_phase)) * 2.0
            head_rotate = math.sin(w_phase) * 18.0
        elif state == 'celebrate':
            y_offset = -20.0 * abs(math.sin(t * 6.0))
            wing_flap = math.sin(t * 16.0) * 26.0
        elif state in ['sleep', 'perch']:
            y_offset = 3.0
            
        painter.save()
        painter.translate(0, y_offset)
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Talon Feet
        painter.setBrush(c_beak)
        painter.drawRoundedRect(QRectF(-16, -10, 12, 11), 3, 3)
        painter.drawRoundedRect(QRectF(4, -10, 12, 11), 3, 3)
        
        # Wing fluffs
        painter.setBrush(c_feather)
        painter.save()
        painter.translate(-24, -46)
        painter.rotate(-12 + wing_flap)
        painter.drawRoundedRect(QRectF(-6, 0, 12, 28), 6, 6)
        painter.restore()
        
        painter.save()
        painter.translate(24, -46)
        painter.rotate(12 - wing_flap)
        painter.drawRoundedRect(QRectF(-6, 0, 12, 28), 6, 6)
        painter.restore()
        
        # Chubby Oval Body
        painter.setBrush(c_feather)
        painter.drawRoundedRect(QRectF(-25, -74, 50, 68), 24, 24)
        
        # Speckled Chest
        painter.setBrush(c_chest)
        painter.drawEllipse(QRectF(-16, -50, 32, 42))
        painter.setPen(QPen(c_feather, 1.5))
        for sx, sy in [(-8, -40), (8, -40), (0, -32), (-6, -24), (6, -24)]:
            painter.drawArc(QRectF(sx - 3, sy - 2, 6, 4), 0, 180 * 16)
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Owl Head with Head Swivel
        head_y = -72.0
        painter.save()
        painter.translate(0, head_y)
        painter.rotate(head_rotate)
        
        # Feather tufts / horns
        p_tuft_l = QPainterPath()
        p_tuft_l.moveTo(-20, -10)
        p_tuft_l.lineTo(-28, -26)
        p_tuft_l.lineTo(-12, -18)
        p_tuft_l.closeSubpath()
        painter.drawPath(p_tuft_l)
        
        p_tuft_r = QPainterPath()
        p_tuft_r.moveTo(20, -10)
        p_tuft_r.lineTo(28, -26)
        p_tuft_r.lineTo(12, -18)
        p_tuft_r.closeSubpath()
        painter.drawPath(p_tuft_r)
        
        # Head Base
        painter.drawRoundedRect(QRectF(-28, -18, 56, 36), 16, 16)
        
        # Huge Golden Amber Eyes
        painter.setBrush(c_eyes)
        painter.drawEllipse(QRectF(-24, -14, 22, 22))
        painter.drawEllipse(QRectF(2, -14, 22, 22))
        
        if is_blinking:
            painter.drawLine(QPointF(-20, -3), QPointF(-6, -3))
            painter.drawLine(QPointF(6, -3), QPointF(20, -3))
        else:
            painter.setBrush(c_dark)
            painter.drawEllipse(QRectF(-18, -9, 11, 13))
            painter.drawEllipse(QRectF(7, -9, 11, 13))
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(-16, -7, 4, 4))
            painter.drawEllipse(QRectF(9, -7, 4, 4))
            painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
        # Curved Beak
        painter.setBrush(c_beak)
        p_beak = QPainterPath()
        p_beak.moveTo(-4, -4)
        p_beak.lineTo(4, -4)
        p_beak.lineTo(0, 6)
        p_beak.closeSubpath()
        painter.drawPath(p_beak)
        
        painter.restore()
        painter.restore()

    # ========================================================
    # 6. SLEEPY PANDA
    # ========================================================
    def draw_panda(self, painter: QPainter, state: str, t: float, is_blinking: bool):
        c_white = QColor(250, 247, 242)
        c_black = QColor(32, 34, 38)
        
        # Heavy cute waddle
        y_offset = 0.0
        waddle = 0.0
        arm_sway = 0.0
        if state in ['wander', 'slow_walk']:
            w_phase = (t * 4.5) % (math.pi * 2.0)
            waddle = math.sin(w_phase) * 6.0
            y_offset = -abs(math.sin(w_phase)) * 2.2
            arm_sway = math.sin(w_phase) * 8.0
        elif state == 'celebrate':
            y_offset = -18.0 * abs(math.sin(t * 5.0))
            arm_sway = math.sin(t * 12.0) * 16.0
        elif state in ['sleep', 'roll']:
            y_offset = 6.0
            
        painter.save()
        painter.translate(0, y_offset)
        painter.rotate(waddle)
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # Black Leg Paws
        painter.setBrush(c_black)
        painter.drawRoundedRect(QRectF(-18, -14, 14, 15), 5, 5)
        painter.drawRoundedRect(QRectF(4, -14, 14, 15), 5, 5)
        
        # Round White Body
        painter.setBrush(c_white)
        painter.drawRoundedRect(QRectF(-24, -62, 48, 52), 22, 22)
        
        # Black arms
        painter.setBrush(c_black)
        painter.save()
        painter.translate(-22, -52)
        painter.rotate(-8 + arm_sway)
        painter.drawRoundedRect(QRectF(-6, 0, 12, 23), 5, 5)
        painter.restore()
        
        painter.save()
        painter.translate(22, -52)
        painter.rotate(8 - arm_sway)
        painter.drawRoundedRect(QRectF(-6, 0, 12, 23), 5, 5)
        painter.restore()
        
        # Panda Head & Ears
        head_y = -82.0
        painter.save()
        painter.translate(0, head_y)
        
        # Black Round Ears
        painter.setBrush(c_black)
        painter.drawEllipse(QRectF(-28, -26, 16, 16))
        painter.drawEllipse(QRectF(12, -26, 16, 16))
        
        # Chubby White Head
        painter.setBrush(c_white)
        painter.drawRoundedRect(QRectF(-28, -18, 56, 42), 20, 20)
        
        # Black Teardrop Eye Patches
        painter.setBrush(c_black)
        painter.save()
        painter.translate(-13, -2)
        painter.rotate(-18)
        painter.drawEllipse(QRectF(-7, -9, 14, 18))
        painter.restore()
        
        painter.save()
        painter.translate(13, -2)
        painter.rotate(18)
        painter.drawEllipse(QRectF(-7, -9, 14, 18))
        painter.restore()
        
        # Eyes inside patches
        if is_blinking:
            painter.setPen(QPen(Qt.white, 1.8))
            painter.drawLine(QPointF(-16, -2), QPointF(-9, -2))
            painter.drawLine(QPointF(9, -2), QPointF(16, -2))
            painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            painter.drawEllipse(QRectF(-15, -4, 4, 4))
            painter.drawEllipse(QRectF(11, -4, 4, 4))
            painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
        # Cute Black Nose & Smile
        painter.setBrush(c_black)
        painter.drawEllipse(QRectF(-4, 6, 8, 5))
        painter.drawLine(QPointF(0, 11), QPointF(0, 13))
        painter.drawLine(QPointF(-4, 15), QPointF(0, 13))
        painter.drawLine(QPointF(4, 15), QPointF(0, 13))
        
        # Soft Blush
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.c_blush)
        painter.drawEllipse(QRectF(-22, 10, 8, 5))
        painter.drawEllipse(QRectF(14, 10, 8, 5))
        painter.setPen(QPen(self.c_outline, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        painter.restore()
        painter.restore()
