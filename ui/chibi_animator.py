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
        if self.kind == "heart":
            self.vy -= 2.0 * dt
        elif self.kind == "star":
            self.vy += 2.0 * dt
        else:
            self.vy += 6.0 * dt

    def alive(self):
        return self.life > 0.0

    def draw(self, painter):
        if not self.alive():
            return
        ratio = max(0.0, min(1.0, self.life / self.max_life))
        alpha = int(225 * ratio)
        painter.save()
        painter.setPen(Qt.NoPen)
        if self.kind == "heart":
            col = QColor(255, 120, 150, alpha)
            painter.setBrush(col)
            s = max(2.0, self.size * ratio)
            p = QPainterPath()
            p.moveTo(self.x, self.y + s)
            p.cubicTo(self.x - s * 1.7, self.y - s * 0.2, self.x - s * 0.9, self.y - s * 1.7, self.x, self.y - s * 0.6)
            p.cubicTo(self.x + s * 0.9, self.y - s * 1.7, self.x + s * 1.7, self.y - s * 0.2, self.x, self.y + s)
            painter.drawPath(p)
        else:
            col = QColor(255, 225, 110, alpha)
            painter.setBrush(col)
            s = max(1.5, self.size * ratio)
            painter.drawEllipse(QRectF(self.x - s / 2, self.y - s / 2, s, s))
        painter.restore()


class ChibiAnimalAnimator:
    """Original QPainter chibi renderer with strongly species-specific silhouettes."""

    def __init__(self, state_machine, species="fox"):
        self.state_machine = state_machine
        self.species = species.lower()
        self.facing = 1
        self.elapsed = 0.0
        self.particles = []
        self._spawn_timer = 0.0
        self._blink_open_until = 0.0
        self._next_blink = random.uniform(2.6, 4.4)
        self.c_outline = QColor(42, 32, 28)
        self.c_blush = QColor(255, 138, 164, 150)

    def reset_animation(self):
        self.elapsed = 0.0
        self.particles.clear()
        self._spawn_timer = 0.0
        self._blink_open_until = 0.0
        self._next_blink = random.uniform(2.6, 4.4)

    def set_facing(self, direction):
        self.facing = 1 if direction >= 0 else -1

    def clear_particles(self):
        self.particles.clear()

    def clear_special(self):
        self.clear_particles()

    def update(self):
        dt = 0.025
        self.elapsed += dt
        self._spawn_timer += dt
        state = self.state_machine.get_state()

        if self.elapsed >= self._next_blink:
            self._blink_open_until = self.elapsed + 0.12
            self._next_blink = self.elapsed + random.uniform(2.6, 4.4)

        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

        if self._spawn_timer >= 0.28 and len(self.particles) < 10:
            self._spawn_timer = 0.0
            if state == "celebrate":
                self.particles.append(VisualParticle(random.uniform(-20, 20), random.uniform(-90, -55), "star", 0.65, random.uniform(-12, 12), -15, random.uniform(4, 7)))
                if random.random() < 0.5:
                    self.particles.append(VisualParticle(random.uniform(-18, 18), random.uniform(-85, -55), "heart", 0.7, random.uniform(-10, 10), -10, random.uniform(4, 6)))

    def _eyes_closed(self, state):
        return state == "sleep" or self.elapsed < self._blink_open_until

    def _outline(self):
        return QPen(self.c_outline, 1.9, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

    def _ellipse(self, painter, rect, fill):
        painter.setBrush(fill)
        painter.drawEllipse(QRectF(*rect))

    def _roundrect(self, painter, rect, radius, fill):
        painter.setBrush(fill)
        painter.drawRoundedRect(QRectF(*rect), radius, radius)

    def draw_contact_shadow(self, painter, width=58, alpha=45):
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, alpha))
        painter.drawEllipse(QRectF(-width / 2, -5, width, 10))
        painter.restore()

    def draw(self, painter: QPainter, rect):
        state = self.state_machine.get_state()
        t = self.elapsed
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(rect.center().x(), rect.bottom())
        painter.scale(self.facing, 1.0)
        self.draw_contact_shadow(painter)

        if self.species == "fox":
            self.draw_fox(painter, state, t, self._eyes_closed(state))
        elif self.species == "rabbit":
            self.draw_rabbit(painter, state, t, self._eyes_closed(state))
        elif self.species == "penguin":
            self.draw_penguin(painter, state, t, self._eyes_closed(state))
        elif self.species == "hamster":
            self.draw_hamster(painter, state, t, self._eyes_closed(state))
        elif self.species == "owl":
            self.draw_owl(painter, state, t, self._eyes_closed(state))
        elif self.species == "panda":
            self.draw_panda(painter, state, t, self._eyes_closed(state))
        else:
            self.draw_fox(painter, state, t, self._eyes_closed(state))

        for particle in self.particles:
            particle.draw(painter)
        painter.restore()

    def _draw_big_eyes(self, painter, left, right, y, rx, ry, closed):
        if closed:
            painter.setPen(self._outline())
            painter.drawArc(QRectF(left - rx, y - 1, rx * 2, 8), 200, 140)
            painter.drawArc(QRectF(right - rx, y - 1, rx * 2, 8), 200, 140)
            return
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(48, 38, 42))
        painter.drawEllipse(QRectF(left - rx, y - ry, rx * 2, ry * 2))
        painter.drawEllipse(QRectF(right - rx, y - ry, rx * 2, ry * 2))
        painter.setBrush(Qt.white)
        painter.drawEllipse(QRectF(left - rx * 0.55, y - ry * 0.65, rx * 0.42, ry * 0.42))
        painter.drawEllipse(QRectF(right - rx * 0.55, y - ry * 0.65, rx * 0.42, ry * 0.42))
        painter.drawEllipse(QRectF(left + rx * 0.1, y + ry * 0.15, rx * 0.20, ry * 0.20))
        painter.drawEllipse(QRectF(right + rx * 0.1, y + ry * 0.15, rx * 0.20, ry * 0.20))
        painter.setPen(self._outline())

    # ------------------------------------------------------------
    # FOX
    # ------------------------------------------------------------
    def draw_fox(self, painter, state, t, closed):
        orange = QColor(236, 118, 40)
        orange_dark = QColor(181, 72, 29)
        cream = QColor(255, 246, 231)
        nose = QColor(71, 44, 40)
        bounce = -abs(math.sin(t * 6.6)) * 3.0 if state in ("wander", "curious") else 0.0
        tail_wave = math.sin(t * 2.8) * 12.0
        if state == "celebrate":
            bounce = -abs(math.sin(t * 7.0)) * 18.0
            tail_wave = math.sin(t * 10) * 20

        painter.save()
        painter.translate(0, bounce)
        painter.setPen(self._outline())

        # Large bushy tail first
        painter.save()
        painter.translate(-14, -30)
        painter.rotate(-16 + tail_wave)
        path = QPainterPath()
        path.moveTo(3, 2)
        path.cubicTo(-22, -4, -48, -25, -47, -53)
        path.cubicTo(-40, -70, -19, -69, -7, -53)
        path.cubicTo(5, -36, 10, -12, 3, 2)
        path.closeSubpath()
        painter.setBrush(orange)
        painter.drawPath(path)
        painter.setBrush(cream)
        tip = QPainterPath()
        tip.moveTo(-28, -57)
        tip.cubicTo(-42, -54, -47, -45, -42, -35)
        tip.cubicTo(-31, -40, -22, -46, -17, -54)
        tip.closeSubpath()
        painter.drawPath(tip)
        painter.restore()

        # Rear legs and compact body
        self._roundrect(painter, (-18, -18, 15, 18), 6, orange_dark)
        self._roundrect(painter, (4, -18, 15, 18), 6, orange_dark)
        self._roundrect(painter, (-23, -69, 46, 54), 20, orange)
        self._roundrect(painter, (-13, -57, 26, 35), 13, cream)

        # Front legs
        self._roundrect(painter, (-15, -24, 10, 18), 5, orange)
        self._roundrect(painter, (5, -24, 10, 18), 5, orange)

        # Head with unmistakable triangular ears and cream muzzle
        painter.save()
        painter.translate(0, -82)
        left_ear = QPainterPath()
        left_ear.moveTo(-25, -10)
        left_ear.lineTo(-30, -43)
        left_ear.lineTo(-5, -22)
        left_ear.closeSubpath()
        right_ear = QPainterPath()
        right_ear.moveTo(25, -10)
        right_ear.lineTo(30, -43)
        right_ear.lineTo(5, -22)
        right_ear.closeSubpath()
        painter.setBrush(orange_dark)
        painter.drawPath(left_ear)
        painter.drawPath(right_ear)
        painter.setBrush(cream)
        painter.drawPath(QPainterPath(left_ear))
        # Inner ears are smaller cream triangles
        p = QPainterPath(); p.moveTo(-22, -15); p.lineTo(-26, -34); p.lineTo(-10, -22); p.closeSubpath(); painter.drawPath(p)
        p = QPainterPath(); p.moveTo(22, -15); p.lineTo(26, -34); p.lineTo(10, -22); p.closeSubpath(); painter.drawPath(p)
        self._roundrect(painter, (-31, -24, 62, 46), 22, orange)
        self._roundrect(painter, (-18, -2, 36, 20), 12, cream)
        self._ellipse(painter, (-4, 1, 8, 6), nose)
        self._draw_big_eyes(painter, -14, 14, -5, 8, 11, closed)
        painter.setBrush(self.c_blush); painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(-25, 1, 9, 5)); painter.drawEllipse(QRectF(16, 1, 9, 5))
        painter.restore()
        painter.restore()

    # ------------------------------------------------------------
    # RABBIT
    # ------------------------------------------------------------
    def draw_rabbit(self, painter, state, t, closed):
        fur = QColor(252, 250, 246)
        pink = QColor(247, 170, 190)
        foot_pink = QColor(243, 183, 195)
        hop = -abs(math.sin(t * 6.0)) * 18.0 if state in ("wander", "hop") else 0.0
        ear_sway = math.sin(t * 4.0) * 7.0
        if state == "celebrate": hop = -abs(math.sin(t * 7.0)) * 23.0

        painter.save(); painter.translate(0, hop); painter.setPen(self._outline())
        self._ellipse(painter, (-27, -28, 15, 15), fur)
        self._roundrect(painter, (-22, -66, 44, 54), 21, fur)
        self._roundrect(painter, (-18, -22, 15, 18), 7, foot_pink)
        self._roundrect(painter, (3, -22, 15, 18), 7, foot_pink)
        self._roundrect(painter, (-13, -38, 9, 14), 4, fur)
        self._roundrect(painter, (4, -38, 9, 14), 4, fur)

        painter.save(); painter.translate(-12, -82); painter.rotate(-10 + ear_sway)
        p = QPainterPath(); p.moveTo(-7, 3); p.quadTo(-15, -45, 0, -59); p.quadTo(15, -45, 7, 3); p.closeSubpath(); painter.setBrush(fur); painter.drawPath(p)
        painter.setBrush(pink); painter.drawRoundedRect(QRectF(-4, -48, 8, 40), 4, 4); painter.restore()
        painter.save(); painter.translate(12, -82); painter.rotate(10 - ear_sway)
        p = QPainterPath(); p.moveTo(-7, 3); p.quadTo(-15, -45, 0, -59); p.quadTo(15, -45, 7, 3); p.closeSubpath(); painter.setBrush(fur); painter.drawPath(p)
        painter.setBrush(pink); painter.drawRoundedRect(QRectF(-4, -48, 8, 40), 4, 4); painter.restore()

        painter.translate(0, -73)
        self._roundrect(painter, (-28, -19, 56, 43), 20, fur)
        self._draw_big_eyes(painter, -13, 13, -1, 8, 10, closed)
        painter.setPen(self._outline()); painter.setBrush(pink); painter.drawEllipse(QRectF(-3.5, 5, 7, 5)); painter.drawLine(QPointF(0, 9), QPointF(0, 12)); painter.drawLine(QPointF(-4, 14), QPointF(0, 12)); painter.drawLine(QPointF(4, 14), QPointF(0, 12))
        painter.setPen(Qt.NoPen); painter.setBrush(self.c_blush); painter.drawEllipse(QRectF(-23, 5, 9, 5)); painter.drawEllipse(QRectF(14, 5, 9, 5))
        painter.restore()

    # ------------------------------------------------------------
    # PENGUIN
    # ------------------------------------------------------------
    def draw_penguin(self, painter, state, t, closed):
        body = QColor(33, 39, 52)
        white = QColor(254, 254, 252)
        orange = QColor(244, 147, 33)
        waddle = math.sin(t * 5.8) * 8.0 if state in ("wander", "waddle") else 0.0
        flap = math.sin(t * 7.0) * 16.0 if state in ("flap", "celebrate") else 0.0
        lift = -abs(math.sin(t * 6.0)) * 4.0 if state == "celebrate" else 0.0

        painter.save(); painter.translate(0, lift); painter.rotate(waddle); painter.setPen(self._outline())
        self._roundrect(painter, (-21, -15, 17, 12), 6, orange); self._roundrect(painter, (4, -15, 17, 12), 6, orange)
        painter.save(); painter.translate(-24, -55); painter.rotate(-15 + flap); self._roundrect(painter, (-6, 0, 12, 30), 6, body); painter.restore()
        painter.save(); painter.translate(24, -55); painter.rotate(15 - flap); self._roundrect(painter, (-6, 0, 12, 30), 6, body); painter.restore()
        self._ellipse(painter, (-27, -90, 54, 79), body)
        self._ellipse(painter, (-19, -72, 38, 58), white)
        # White face mask reads as penguin, not generic bird
        self._ellipse(painter, (-22, -78, 44, 37), white)
        self._draw_big_eyes(painter, -11, 11, -60, 7.5, 9, closed)
        painter.setBrush(orange); painter.setPen(self._outline())
        p = QPainterPath(); p.moveTo(-7, -48); p.lineTo(7, -48); p.lineTo(0, -39); p.closeSubpath(); painter.drawPath(p)
        painter.setPen(Qt.NoPen); painter.setBrush(self.c_blush); painter.drawEllipse(QRectF(-21, -53, 8, 5)); painter.drawEllipse(QRectF(13, -53, 8, 5))
        painter.restore()

    # ------------------------------------------------------------
    # HAMSTER - deliberately rebuilt around real hamster proportions
    # ------------------------------------------------------------
    def draw_hamster(self, painter, state, t, closed):
        fur = QColor(234, 166, 91)
        fur_light = QColor(255, 238, 215)
        muzzle = QColor(255, 245, 230)
        pink = QColor(244, 167, 184)
        dark = QColor(57, 42, 38)
        scurry = math.sin(t * 11.0) * 3.5 if state in ("wander", "scurry") else 0.0
        body_bob = -abs(math.sin(t * 10.0)) * 2.0 if state in ("wander", "scurry") else 0.0
        if state == "celebrate": body_bob = -abs(math.sin(t * 7.0)) * 14.0

        painter.save(); painter.translate(0, body_bob); painter.setPen(self._outline())

        # Tiny rear feet + tail
        self._ellipse(painter, (-21, -15, 14, 13), pink); self._ellipse(painter, (7, -15, 14, 13), pink)
        self._ellipse(painter, (23, -49, 9, 9), pink)

        # Very broad pear-shaped hamster body
        self._ellipse(painter, (-31, -66, 62, 63), fur)
        self._ellipse(painter, (-18, -49, 36, 43), fur_light)

        # Round ears, visibly hamster-specific
        self._ellipse(painter, (-29, -79, 20, 20), fur)
        self._ellipse(painter, (9, -79, 20, 20), fur)
        self._ellipse(painter, (-24, -74, 10, 10), pink)
        self._ellipse(painter, (14, -74, 10, 10), pink)

        # Raised tiny paws
        self._ellipse(painter, (-14 + scurry, -35, 11, 10), pink)
        self._ellipse(painter, (3 - scurry, -35, 11, 10), pink)

        # Huge cheek pouches: the defining visual cue
        cheek_y = -50 + math.sin(t * 8.0) * 1.3 if state == "cheek_puff" else -50
        self._ellipse(painter, (-31, cheek_y, 24, 21), muzzle)
        self._ellipse(painter, (7, cheek_y, 24, 21), muzzle)

        # Head/muzzle sits forward over the body
        self._ellipse(painter, (-28, -78, 56, 45), fur)
        self._ellipse(painter, (-21, -55, 42, 25), muzzle)
        self._draw_big_eyes(painter, -14, 14, -61, 8, 10, closed)

        painter.setBrush(pink); painter.setPen(self._outline())
        painter.drawEllipse(QRectF(-3.5, -50, 7, 5))
        painter.drawLine(QPointF(-1, -45), QPointF(0, -40))
        painter.drawLine(QPointF(0, -40), QPointF(5, -37))
        painter.setPen(QPen(dark, 1.1))
        painter.drawLine(QPointF(-12, -47), QPointF(-24, -50)); painter.drawLine(QPointF(-12, -44), QPointF(-24, -44))
        painter.drawLine(QPointF(12, -47), QPointF(24, -50)); painter.drawLine(QPointF(12, -44), QPointF(24, -44))
        painter.setPen(Qt.NoPen); painter.setBrush(self.c_blush); painter.drawEllipse(QRectF(-25, -53, 10, 6)); painter.drawEllipse(QRectF(15, -53, 10, 6))
        painter.restore()

    # ------------------------------------------------------------
    # OWL - true facial disk and huge forward-facing eyes
    # ------------------------------------------------------------
    def draw_owl(self, painter, state, t, closed):
        brown = QColor(111, 79, 57)
        dark = QColor(67, 47, 39)
        cream = QColor(250, 241, 220)
        gold = QColor(202, 149, 41)
        beak = QColor(235, 161, 42)
        flap = math.sin(t * 8.0) * 18.0 if state in ("wing_flap", "celebrate") else 0.0
        turn = math.sin(t * 2.7) * 12.0 if state in ("head_turn", "wander") else 0.0
        lift = -abs(math.sin(t * 6.0)) * 14.0 if state == "celebrate" else 0.0

        painter.save(); painter.translate(0, lift); painter.setPen(self._outline())
        painter.save(); painter.translate(-22, -52); painter.rotate(-14 + flap); self._roundrect(painter, (-6, 0, 12, 29), 6, brown); painter.restore()
        painter.save(); painter.translate(22, -52); painter.rotate(14 - flap); self._roundrect(painter, (-6, 0, 12, 29), 6, brown); painter.restore()
        self._ellipse(painter, (-25, -72, 50, 66), brown)

        # Ear tufts
        p = QPainterPath(); p.moveTo(-18, -64); p.lineTo(-25, -88); p.lineTo(-8, -75); p.closeSubpath(); painter.setBrush(dark); painter.drawPath(p)
        p = QPainterPath(); p.moveTo(18, -64); p.lineTo(25, -88); p.lineTo(8, -75); p.closeSubpath(); painter.drawPath(p)

        painter.save(); painter.translate(0, -59); painter.rotate(turn)
        # Large cream facial disk
        self._ellipse(painter, (-28, -29, 56, 52), cream)
        # Golden eyes with dark pupils
        if closed:
            painter.setPen(self._outline()); painter.drawArc(QRectF(-22, -8, 16, 7), 200, 140); painter.drawArc(QRectF(6, -8, 16, 7), 200, 140)
        else:
            painter.setPen(Qt.NoPen); painter.setBrush(gold); painter.drawEllipse(QRectF(-22, -19, 18, 21)); painter.drawEllipse(QRectF(4, -19, 18, 21))
            painter.setBrush(QColor(44, 34, 26)); painter.drawEllipse(QRectF(-17, -14, 8, 12)); painter.drawEllipse(QRectF(9, -14, 8, 12))
            painter.setBrush(Qt.white); painter.drawEllipse(QRectF(-15, -13, 3.5, 3.5)); painter.drawEllipse(QRectF(11, -13, 3.5, 3.5))
        painter.setPen(self._outline()); painter.setBrush(beak)
        p = QPainterPath(); p.moveTo(-5, -1); p.lineTo(5, -1); p.lineTo(0, 9); p.closeSubpath(); painter.drawPath(p)
        painter.restore(); painter.restore()

    # ------------------------------------------------------------
    # PANDA - clean black/white silhouette, no vest
    # ------------------------------------------------------------
    def draw_panda(self, painter, state, t, closed):
        white = QColor(250, 248, 243)
        black = QColor(32, 32, 36)
        waddle = math.sin(t * 4.8) * 5.0 if state in ("wander", "slow_walk") else 0.0
        lift = -abs(math.sin(t * 6.0)) * 15.0 if state == "celebrate" else 0.0
        roll = state == "roll"

        painter.save(); painter.translate(0, lift); painter.rotate(waddle); painter.setPen(self._outline())
        self._ellipse(painter, (-21, -18, 18, 16), black); self._ellipse(painter, (3, -18, 18, 16), black)
        self._roundrect(painter, (-24, -66, 48, 53), 22, white)
        # Black limbs, not a shoulder vest
        self._roundrect(painter, (-31, -56, 13, 28), 6, black); self._roundrect(painter, (18, -56, 13, 28), 6, black)
        self._roundrect(painter, (-25, -17, 17, 15), 7, black); self._roundrect(painter, (8, -17, 17, 15), 7, black)

        # Head and ears
        self._ellipse(painter, (-28, -91, 56, 46), white)
        self._ellipse(painter, (-27, -93, 18, 18), black); self._ellipse(painter, (9, -93, 18, 18), black)
        painter.save(); painter.translate(0, -70)
        painter.setBrush(black); painter.save(); painter.rotate(-18); painter.drawEllipse(QRectF(-24, -11, 14, 22)); painter.restore(); painter.save(); painter.rotate(18); painter.drawEllipse(QRectF(10, -11, 14, 22)); painter.restore()
        if closed:
            painter.setPen(QPen(Qt.white, 2.0)); painter.drawLine(QPointF(-16, 0), QPointF(-9, 0)); painter.drawLine(QPointF(9, 0), QPointF(16, 0))
        else:
            painter.setPen(Qt.NoPen); painter.setBrush(Qt.white); painter.drawEllipse(QRectF(-15, -3, 5, 5)); painter.drawEllipse(QRectF(10, -3, 5, 5))
        painter.setBrush(black); painter.drawEllipse(QRectF(-4, 8, 8, 5)); painter.drawLine(QPointF(0, 13), QPointF(0, 15)); painter.drawLine(QPointF(-4, 17), QPointF(0, 15)); painter.drawLine(QPointF(4, 17), QPointF(0, 15))
        painter.restore()
        painter.restore()
