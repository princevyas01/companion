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

        if self.kind in ['sparkle', 'star']:
            col = QColor(255, 225, 90, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = max(1.5, self.size * ratio)
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))
            painter.setPen(QPen(col, 1.1))
            painter.drawLine(QPointF(self.x - sz * 1.2, self.y), QPointF(self.x + sz * 1.2, self.y))
            painter.drawLine(QPointF(self.x, self.y - sz * 1.2), QPointF(self.x, self.y + sz * 1.2))

        elif self.kind in ['dust', 'landing_puff']:
            col = QColor(200, 195, 190, int(alpha * 0.5)) if self.color is None else QColor(self.color)
            col.setAlpha(int(alpha * 0.5))
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = self.size * (1.0 + (1.0 - ratio) * 0.8)
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))

        elif self.kind == 'sleepy_dot':
            col = QColor(165, 180, 220, alpha) if self.color is None else QColor(self.color)
            col.setAlpha(alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(col)
            sz = max(1.5, self.size * (0.65 + 0.35 * ratio))
            painter.drawEllipse(QRectF(self.x - sz / 2.0, self.y - sz / 2.0, sz, sz))

        painter.restore()


class CatAnimator:
    def __init__(self, state_machine, cat_variant='cat_tuxedo'):
        self.state_machine = state_machine
        self.cat_variant = cat_variant  # 'cat_tuxedo', 'cat_orange', or 'cats_duo'
        
        # Colors - Tuxedo Cat (Rich dark charcoal & crisp white)
        self.tux_black = QColor(32, 32, 38)
        self.tux_white = QColor(255, 255, 255)
        
        # Colors - Ginger Tabby Cat (Warm honey orange & cream belly)
        self.ginger_fur = QColor(246, 146, 38)
        self.ginger_dark = QColor(192, 90, 16)
        self.ginger_belly = QColor(255, 242, 218)
        
        # Common Cute Facial Colors (Matching Dog)
        self.eye_color = QColor(30, 20, 20)      # Cute Dark Sparkle Eyes
        self.outline_color = QColor(45, 30, 25)  # Dark Brown Outline
        self.blush_color = QColor(255, 182, 193) # Soft Pink Cheeks
        self.nose_color = QColor(255, 138, 158)  # Soft Pink Nose
        self.tongue_color = QColor(255, 110, 130) # Soft Pink Tongue

        # Lightweight transient effect particles (bounded to <= 12)
        self.particles = []
        self._spawn_timer = 0.0

    def set_variant(self, variant):
        self.cat_variant = variant

    def draw_contact_shadow(self, painter, y_offset=0.0, width=52.0, alpha=40):
        """Draws subtle soft contact shadow on the ground."""
        painter.save()
        painter.setPen(Qt.NoPen)
        shadow_width = max(20.0, width * (1.0 - min(abs(y_offset) / 60.0, 0.35)))
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
        if len(self.particles) < 12 and self._spawn_timer >= 0.25:
            state = self.state_machine.get_state()
            if state in ['happy', 'purr', 'celebrate']:
                self._spawn_timer = 0.0
                self.particles.append(
                    VisualParticle(
                        x=random.uniform(-20, 20),
                        y=random.uniform(-90, -55),
                        kind='sparkle',
                        life=0.55,
                        vx=random.uniform(-10, 10),
                        vy=random.uniform(-16, -6),
                        size=random.uniform(3.5, 6.0)
                    )
                )
            elif state in ['clean', 'eat']:
                self._spawn_timer = 0.0
                self.particles.append(
                    VisualParticle(
                        x=-15 + random.uniform(-4, 4),
                        y=-42 + random.uniform(-4, 4),
                        kind='sparkle',
                        life=0.45,
                        vx=random.uniform(-6, 6),
                        vy=random.uniform(-10, -4),
                        size=random.uniform(3.0, 5.0)
                    )
                )
            elif state == 'sleep' and random.random() < 0.4:
                self._spawn_timer = 0.0
                self.particles.append(
                    VisualParticle(
                        x=26 + random.uniform(-4, 6),
                        y=-85 + random.uniform(-6, 2),
                        kind='sleepy_dot',
                        life=0.75,
                        vx=random.uniform(2, 7),
                        vy=random.uniform(-12, -5),
                        size=random.uniform(3.0, 5.0)
                    )
                )

    def draw(self, painter: QPainter, rect):
        state = self.state_machine.get_state()
        t = self.state_machine.time_in_state
        
        if self.cat_variant == 'cats_duo':
            # Both ultra-cute round cats side-by-side!
            painter.save()
            
            # Left Tuxedo Cat (-36 offset)
            painter.save()
            painter.translate(-36, 0)
            self._draw_single_cat(painter, rect, 'tuxedo', state, t, scale_factor=1.00, role='primary')
            painter.restore()
            
            # Right Ginger Cat (+36 offset, slightly smaller buddy scale 0.88)
            painter.save()
            painter.translate(36, 0)
            self._draw_single_cat(painter, rect, 'orange', state, t, scale_factor=0.88, role='secondary')
            painter.restore()
            
            # Draw shared particles
            for p in self.particles:
                p.draw(painter)

            painter.restore()
        elif self.cat_variant == 'cat_orange':
            self._draw_single_cat(painter, rect, 'orange', state, t, scale_factor=1.00, role='primary')
            for p in self.particles:
                p.draw(painter)
        else:
            self._draw_single_cat(painter, rect, 'tuxedo', state, t, scale_factor=1.00, role='primary')
            for p in self.particles:
                p.draw(painter)

    def _draw_single_cat(self, painter: QPainter, rect, breed, state, t, scale_factor=1.0, role='primary'):
        painter.save()
        painter.translate(rect.center().x(), rect.bottom())
        
        # Apply character scale factor
        painter.scale(scale_factor, scale_factor)
        
        # Determine different motion parameters based on role!
        if role == 'secondary':
            t_eff = t + 0.65
            if state in ['pounce', 'jump', 'celebrate']:
                sub_state = 'curious_peek' if t < 0.3 else 'small_hop'
            elif state in ['happy', 'purr']:
                sub_state = 'lick_paw'  # Licking paw animation!
            elif state in ['clean', 'eat']:
                sub_state = 'lick_paw'
            else:
                sub_state = state
        else:
            t_eff = t
            sub_state = state

        # Compute transform values (Cute natural physics!)
        scale_y = 1.0
        scale_x = 1.0
        y_offset = 0.0
        rotation = 0.0
        tail_angle = math.sin(t_eff * 10) * 20
        ear_flop = math.sin(t_eff * 4) * 3
        is_sitting = False
        is_pouncing = False
        is_sleeping = False
        is_meowing = False
        is_stretching = False
        tongue_out = False
        making_biscuits = False
        licking_paw = False
        
        if sub_state == 'idle':
            # Cheerful breathing & tail sway
            scale_y = 1.0 + 0.022 * math.sin(t_eff * 3)
            scale_x = 1.0 - 0.01 * math.sin(t_eff * 3)
            tail_angle = math.sin(t_eff * 8) * 18
            ear_flop = math.sin(t_eff * 3) * 2
        elif sub_state == 'curious_peek':
            rotation = -8 * math.sin(t_eff * 4)
            tail_angle = math.sin(t_eff * 10) * 22
            ear_flop = -4
        elif sub_state == 'small_hop':
            y_offset = -14 * abs(math.sin((t_eff - 0.3) * 10))
            tail_angle = math.sin(t_eff * 16) * 28
            scale_y = 1.04 if y_offset < -6 else 0.96
        elif sub_state in ['lick_paw', 'clean']:
            licking_paw = True
            is_sitting = True
            tail_angle = math.sin(t_eff * 8) * 15
            scale_y = 0.94
        elif sub_state in ['happy', 'purr']:
            scale_y = 1.0 + 0.03 * math.sin(t_eff * 6)
            scale_x = 1.0 - 0.015 * math.sin(t_eff * 6)
            y_offset = -4 * abs(math.sin(t_eff * 8))
            tail_angle = math.sin(t_eff * 18) * 35
            making_biscuits = True
            tongue_out = True
        elif sub_state in ['sit', 'sit_down', 'type', 'focus']:
            is_sitting = True
            scale_y = 0.94
            scale_x = 1.02
            y_offset = 3
            tail_angle = math.sin(t_eff * 6) * 20
        elif sub_state in ['pounce', 'jump', 'celebrate']:
            # ====================================================
            # CUTE GHIBLI JUMP ANIMATION (Anticipation -> Arc -> Soft Landing)
            # ====================================================
            cycle = (t_eff * 2.5) % 2.0
            if cycle < 0.4:
                # Phase 1: Crouching Wind-Up (Anticipation squish)
                y_offset = 6
                scale_y = 0.88
                scale_x = 1.08
                rotation = 0.0
                tail_angle = math.sin(t_eff * 15) * 15
            elif cycle < 1.4:
                # Phase 2: Smooth Parabolic Leap (Upward Launch)
                jump_t = (cycle - 0.4) / 1.0
                y_offset = -32 * math.sin(jump_t * math.pi)
                rotation = -6 * math.cos(jump_t * math.pi)
                scale_y = 1.06 if y_offset < -12 else 0.94
                scale_x = 0.95 if y_offset < -12 else 1.04
                ear_flop = math.sin(t_eff * 12) * 8
                tail_angle = math.sin(t_eff * 20) * 35
                tongue_out = True
            else:
                # Phase 3: Soft Pillowy Landing & Bounce
                land_t = (cycle - 1.4) / 0.6
                y_offset = 4 * math.sin(land_t * math.pi)
                scale_y = 0.92
                scale_x = 1.06
                rotation = 0.0
                tail_angle = math.sin(t_eff * 10) * 20
            is_pouncing = True
        elif sub_state in ['meow', 'bark', 'react_click']:
            is_meowing = True
            tongue_out = True
            y_offset = -12 * math.sin(t_eff * 14) if t_eff < 0.2 else 0
            tail_angle = math.sin(t_eff * 18) * 30
            ear_flop = 6
        elif sub_state == 'sleep':
            is_sleeping = True
            is_sitting = True
            scale_y = 0.90 + 0.015 * math.sin(t_eff * 2)
            scale_x = 1.05
            y_offset = 8
            tail_angle = 5 + math.sin(t_eff * 2) * 3
            ear_flop = 3
        elif sub_state == 'stretch':
            is_stretching = True
            scale_x = 1.15
            scale_y = 0.88
            y_offset = 5
            tail_angle = 25
        elif sub_state in ['drag', 'react_drag']:
            is_sitting = False
            scale_y = 1.15
            scale_x = 0.88
            ear_flop = 12
            tail_angle = 15 * math.sin(t_eff * 8)
        elif sub_state == 'wander':
            is_sitting = False
            y_offset = -10 * abs(math.sin(t_eff * 10))
            rotation = 3 * math.sin(t_eff * 5)
            ear_flop = math.sin(t_eff * 10) * 6
            tail_angle = math.sin(t_eff * 12) * 20

        # Grounded Contact Shadow (drawn on base floor before character translate)
        shadow_w = 60.0 if is_sitting else 52.0
        self.draw_contact_shadow(painter, y_offset=y_offset, width=shadow_w, alpha=38)

        # Apply character transforms
        painter.translate(0, y_offset)
        painter.scale(scale_x, scale_y)
        painter.rotate(rotation)
        
        # Setup Pen & Brushes (Matching Dog outline thickness)
        pen = QPen(self.outline_color, 3.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        primary_color = self.tux_black if breed == 'tuxedo' else self.ginger_fur
        secondary_color = self.tux_white if breed == 'tuxedo' else self.ginger_belly
        stripe_color = self.ginger_dark
        
        # ==========================================
        # 1. DRAW TAIL
        # ==========================================
        painter.save()
        painter.translate(25, -25 if not is_sitting else -15)
        painter.rotate(tail_angle)
        tail_path = QPainterPath()
        tail_path.moveTo(0, 0)
        tail_path.cubicTo(18, -12, 24, -36, 12, -48)
        tail_path.cubicTo(2, -48, -4, -34, 4, -20)
        tail_path.cubicTo(8, -12, 6, -5, 0, 0)
        painter.setBrush(QBrush(primary_color))
        painter.drawPath(tail_path)
        
        if breed == 'orange':
            painter.setPen(QPen(stripe_color, 2.5, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(QPointF(6, -16), QPointF(14, -20))
            painter.drawLine(QPointF(10, -28), QPointF(18, -32))
            painter.setPen(pen)
        painter.restore()
        
        # ==========================================
        # 2. DRAW LEGS / FEET (Matching Dog geometry!)
        # ==========================================
        painter.setBrush(QBrush(secondary_color if breed == 'tuxedo' else primary_color))
        if is_sitting and not licking_paw:
            # Back feet tucked in
            painter.drawEllipse(QRectF(-35, -18, 22, 18))
            painter.drawEllipse(QRectF(13, -18, 22, 18))
            # Front feet / Biscuit making
            biscuit_off = math.sin(t_eff * 15) * 4 if making_biscuits else 0
            painter.drawEllipse(QRectF(-18, -14 + biscuit_off, 16, 14))
            painter.drawEllipse(QRectF(2, -14 - biscuit_off, 16, 14))
        elif is_sitting and licking_paw:
            # Back feet tucked in
            painter.drawEllipse(QRectF(-35, -18, 22, 18))
            painter.drawEllipse(QRectF(13, -18, 22, 18))
            # Right foot on ground
            painter.drawEllipse(QRectF(2, -14, 16, 14))
            # Left foot raised up to mouth for licking!
            paw_lift = math.sin(t_eff * 12) * 3
            painter.drawEllipse(QRectF(-18, -42 + paw_lift, 16, 16))
        else:
            # Standing feet
            spd = 16 if sub_state in ['pounce', 'jump', 'wander'] else 12
            leg_bounce = math.sin(t_eff * spd) * (5 if sub_state in ['pounce', 'jump'] else 4)
            painter.drawRoundedRect(QRectF(-28, -20 + leg_bounce, 18, 20), 8, 8)
            painter.drawRoundedRect(QRectF(10, -20 - leg_bounce, 18, 20), 8, 8)

        # ==========================================
        # 3. DRAW BODY (Matching Dog body roundness!)
        # ==========================================
        body_rect = QRectF(-32, -55, 64, 45) if not is_sitting else QRectF(-30, -50, 60, 42)
        painter.setBrush(QBrush(primary_color))
        painter.drawRoundedRect(body_rect, 22, 22)
        
        # White Chest Patch
        painter.setBrush(QBrush(secondary_color))
        painter.setPen(Qt.NoPen)
        chest_rect = QRectF(-18, -46, 36, 34)
        painter.drawEllipse(chest_rect)
        painter.setPen(pen)

        # ==========================================
        # 4. DRAW ULTRA-ROUND CHUBBY BEAN HEAD (EXACTLY MATCHING DOG!)
        # ==========================================
        head_y = -75 if not is_sitting else -70
        if licking_paw:
            head_y += math.sin(t_eff * 12) * 4  # Head bobbing while licking paw!
            
        head_rect = QRectF(-45, head_y - 45, 90, 75)
        painter.setBrush(QBrush(primary_color))
        painter.drawRoundedRect(head_rect, 35, 35)  # Perfectly round 35px corners!

        # White Face Blaze / Muzzle for Tuxedo Cat
        if breed == 'tuxedo':
            painter.setBrush(QBrush(self.tux_white))
            painter.setPen(Qt.NoPen)
            # White muzzle circle
            painter.drawEllipse(QRectF(-20, head_y - 14, 40, 28))
            # White forehead blaze V
            blaze_p = QPainterPath()
            blaze_p.moveTo(0, head_y - 40)
            blaze_p.lineTo(-8, head_y - 12)
            blaze_p.lineTo(8, head_y - 12)
            blaze_p.closeSubpath()
            painter.drawPath(blaze_p)
            painter.setPen(pen)
        elif breed == 'orange':
            # Cream Muzzle Patch
            painter.setBrush(QBrush(self.ginger_belly))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(-18, head_y - 14, 36, 26))
            painter.setPen(pen)
            
            # Tabby stripes on round forehead ("M" shape)
            painter.setPen(QPen(stripe_color, 3, Qt.SolidLine, Qt.RoundCap))
            m_path = QPainterPath()
            m_path.moveTo(-10, head_y - 36)
            m_path.lineTo(-5, head_y - 28)
            m_path.lineTo(0, head_y - 34)
            m_path.lineTo(5, head_y - 28)
            m_path.lineTo(10, head_y - 36)
            painter.drawPath(m_path)
            painter.setPen(pen)

        # ==========================================
        # 5. CAT EARS ON ROUND HEAD
        # ==========================================
        # Left Ear
        painter.save()
        painter.translate(-30, head_y - 34)
        painter.rotate(-10 + ear_flop)
        ear_left = QPainterPath()
        ear_left.moveTo(0, 0)
        ear_left.cubicTo(-18, -12, -24, -44, -6, -42)
        ear_left.cubicTo(8, -32, 10, -14, 0, 0)
        painter.setBrush(QBrush(primary_color))
        painter.drawPath(ear_left)
        
        # Pink Inner Ear
        painter.setBrush(QBrush(self.blush_color))
        painter.setPen(Qt.NoPen)
        inner_l = QPainterPath()
        inner_l.moveTo(-2, -5)
        inner_l.cubicTo(-12, -12, -16, -34, -4, -32)
        inner_l.cubicTo(5, -24, 6, -10, -2, -5)
        painter.drawPath(inner_l)
        painter.setPen(pen)
        painter.restore()
        
        # Right Ear
        painter.save()
        painter.translate(30, head_y - 34)
        painter.rotate(10 - ear_flop)
        ear_right = QPainterPath()
        ear_right.moveTo(0, 0)
        ear_right.cubicTo(18, -12, 24, -44, 6, -42)
        ear_right.cubicTo(-8, -32, -10, -14, 0, 0)
        painter.setBrush(QBrush(primary_color))
        painter.drawPath(ear_right)
        
        # Pink Inner Ear
        painter.setBrush(QBrush(self.blush_color))
        painter.setPen(Qt.NoPen)
        inner_r = QPainterPath()
        inner_r.moveTo(2, -5)
        inner_r.cubicTo(12, -12, 16, -34, 4, -32)
        inner_r.cubicTo(-5, -24, -6, -10, 2, -5)
        painter.drawPath(inner_r)
        painter.setPen(pen)
        painter.restore()

        # ==========================================
        # 6. CHEERFUL HAPPY EYES & PINK BLUSH CHEEKS
        # ==========================================
        eye_y = head_y - 12
        if is_sleeping:
            # Sleeping Curved Eyes ( ^ ^ )
            painter.setPen(QPen(self.outline_color, 3, Qt.SolidLine, Qt.RoundCap))
            left_eye_path = QPainterPath()
            left_eye_path.moveTo(-24, eye_y)
            left_eye_path.quadTo(-17, eye_y - 8, -10, eye_y)
            painter.drawPath(left_eye_path)
            
            right_eye_path = QPainterPath()
            right_eye_path.moveTo(10, eye_y)
            right_eye_path.quadTo(17, eye_y - 8, 24, eye_y)
            painter.drawPath(right_eye_path)
            painter.setPen(pen)
        else:
            # Big Shiny Cheerful Pupil Eyes (Matching Dog size & double sparkle!)
            painter.setBrush(QBrush(self.eye_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(-24, eye_y - 10, 14, 18))
            painter.drawEllipse(QRectF(10, eye_y - 10, 14, 18))
            
            # Double White Sparkle Highlights
            painter.setBrush(QBrush(Qt.white))
            painter.drawEllipse(QRectF(-22, eye_y - 8, 5, 6))
            painter.drawEllipse(QRectF(-18, eye_y + 2, 3, 3))
            painter.drawEllipse(QRectF(12, eye_y - 8, 5, 6))
            painter.drawEllipse(QRectF(16, eye_y + 2, 3, 3))
            painter.setPen(pen)

        # Soft Pink Blush Cheeks
        painter.setBrush(QBrush(self.blush_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(-34, eye_y + 4, 11, 7))
        painter.drawEllipse(QRectF(23, eye_y + 4, 11, 7))
        painter.setPen(pen)

        # ==========================================
        # 7. HAPPY NOSE, WHISKERS & SWEET SMILE MOUTH
        # ==========================================
        nose_y = head_y + 2
        
        # Pink Nose (Matching Dog rounded nose)
        painter.setBrush(QBrush(self.nose_color))
        painter.drawRoundedRect(QRectF(-5, nose_y - 4, 10, 7), 3, 3)

        # Delicate Cat Whiskers
        painter.setPen(QPen(self.outline_color, 1.8, Qt.SolidLine, Qt.RoundCap))
        # Left Whiskers
        painter.drawLine(QPointF(-14, nose_y - 1), QPointF(-42, nose_y - 6))
        painter.drawLine(QPointF(-14, nose_y + 3), QPointF(-44, nose_y + 3))
        painter.drawLine(QPointF(-14, nose_y + 7), QPointF(-40, nose_y + 10))
        # Right Whiskers
        painter.drawLine(QPointF(14, nose_y - 1), QPointF(42, nose_y - 6))
        painter.drawLine(QPointF(14, nose_y + 3), QPointF(44, nose_y + 3))
        painter.drawLine(QPointF(14, nose_y + 7), QPointF(40, nose_y + 10))
        painter.setPen(pen)

        # Sweet Smiling :3 Cat Mouth
        mouth_path = QPainterPath()
        mouth_path.moveTo(-8, nose_y + 6)
        mouth_path.quadTo(-4, nose_y + 10, 0, nose_y + 6)
        mouth_path.quadTo(4, nose_y + 10, 8, nose_y + 6)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(mouth_path)

        # ==========================================
        # 8. PAW LICKING & HAPPY TONGUE
        # ==========================================
        if licking_paw:
            # Pink tongue licking raised paw!
            painter.setBrush(QBrush(self.tongue_color))
            painter.setPen(QPen(self.outline_color, 2))
            tongue_rect = QRectF(-7, nose_y + 5, 8, 10)
            painter.drawRoundedRect(tongue_rect, 4, 4)

        elif tongue_out or sub_state in ['happy', 'tongue_out', 'celebrate', 'react_click', 'pounce']:
            painter.setBrush(QBrush(self.tongue_color))
            painter.setPen(QPen(self.outline_color, 2))
            tongue_rect = QRectF(-5, nose_y + 7, 10, 12 + math.sin(t_eff * 10) * 2)
            painter.drawRoundedRect(tongue_rect, 5, 5)

        if is_meowing or sub_state == 'meow':
            painter.setPen(QPen(self.outline_color, 3))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            painter.drawText(QPointF(35, head_y - 30), "MEOW!")

        if is_sleeping or sub_state in ['sleep', 'exhausted']:
            painter.setPen(QPen(self.outline_color, 3))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            painter.drawText(QPointF(30, head_y - 45 - (t_eff * 20 % 20)), "Zzz")

        painter.restore()
