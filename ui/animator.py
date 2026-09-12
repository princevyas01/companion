import math
import random
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QPointF, QRectF

class DragonAnimator:
    def __init__(self, state_machine):
        self.state_machine = state_machine
        self.base_color = QColor(220, 70, 60)
        self.belly_color = QColor(255, 230, 160)
        self.horn_color = QColor(240, 180, 50)
        self.outline_color = QColor(50, 30, 30)
        self.wing_color = QColor(190, 50, 40)
        self.flame_color = QColor(255, 150, 20)
        self.flame_inner = QColor(255, 255, 100)

    def update(self):
        pass

    def draw(self, painter: QPainter, rect):
        state = self.state_machine.get_state()
        t = self.state_machine.time_in_state
        
        painter.save()
        painter.translate(rect.center().x(), rect.bottom())
        
        # Transforms
        scale_y = 1.0
        scale_x = 1.0
        y_offset = 0.0
        rotation = 0.0
        
        if state == 'idle':
            scale_y = 1.0 + 0.02 * math.sin(t * 3)
        elif state == 'sleep':
            scale_y = 0.95 + 0.01 * math.sin(t * 2)
            y_offset = 5
        elif state == 'exhausted':
            scale_y = 0.90
            scale_x = 1.05
            y_offset = 10
        elif state == 'wake':
            scale_y = 1.0 + 0.1 * math.sin(t * 5) * max(0, 1 - t)
        elif state == 'react_click':
            y_offset = -15 * math.sin(t * 15) if t < 0.2 else 0
        elif state == 'celebrate':
            y_offset = -20 * abs(math.sin(t * 10))
        elif state == 'drag' or state == 'react_drag':
            scale_y = 1.1
            scale_x = 0.9
        elif state == 'focus':
            scale_y = 1.0 + 0.01 * math.sin(t * 2)
        elif state == 'annoyed':
            rotation = 5 * math.sin(t * 20) if t < 0.5 else 0
        elif state == 'wander':
            y_offset = -10 * abs(math.sin(t * 12))
            rotation = 5 * math.sin(t * 6)
        elif state == 'sit':
            scale_y = 0.98
            y_offset = 2
            
        painter.translate(0, y_offset)
        painter.scale(scale_x, scale_y)
        painter.rotate(rotation)
        
        self.draw_tail(painter, state, t)
        self.draw_wings(painter, state, t)
        self.draw_legs(painter, state, t)
        self.draw_body(painter, state, t)
        
        if state in ['type', 'focus', 'exhausted']:
            self.draw_laptop(painter, state, t)
            
        self.draw_arms(painter, state, t)
        self.draw_head(painter, state, t)
        
        if state == 'fire_breathe':
            self.draw_fire_breath(painter, t)
            
        painter.restore()

    def draw_laptop(self, painter, state, t):
        painter.save()
        painter.translate(0, -25) 
        
        # Frame
        painter.setPen(QPen(self.outline_color, 2))
        painter.setBrush(QColor(220, 220, 225))
        painter.drawRect(QRectF(-25, -30, 50, 35))
        
        # Screen
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(30, 40, 50))
        painter.drawRect(QRectF(-22, -27, 44, 29))
        
        if state == 'type':
            painter.setBrush(QColor(100, 255, 100))
            for i in range(5):
                w = 10 + (int(t * 15 + i * 7) % 25)
                painter.drawRect(QRectF(-18, -24 + i*5, w, 2))
        elif state == 'exhausted':
            # Zzz on screen
            painter.setPen(QColor(100, 255, 100))
            painter.setFont(painter.font())
            painter.drawText(QRectF(-22, -27, 44, 29), Qt.AlignCenter, "...")
            
        # Keyboard base
        painter.setPen(QPen(self.outline_color, 2))
        painter.setBrush(QColor(200, 200, 205))
        path = QPainterPath()
        path.moveTo(-25, 5)
        path.lineTo(25, 5)
        path.lineTo(35, 15)
        path.lineTo(-35, 15)
        path.closeSubpath()
        painter.drawPath(path)
        painter.restore()

    def draw_tail(self, painter, state, t):
        painter.save()
        painter.setPen(QPen(self.outline_color, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(self.base_color)
        
        sway = math.sin(t * 2) * 10 if state in ['idle', 'sit'] else 0
        if state in ['curious', 'wander']: sway = math.sin(t * 6) * 15
        if state == 'exhausted': sway = 0
            
        path = QPainterPath()
        path.moveTo(0, -30)
        path.quadTo(30, -10 + sway, 50, -30 + sway)
        path.quadTo(30, -30, 0, -40)
        painter.drawPath(path)
        
        # Flame tip
        painter.setPen(Qt.NoPen)
        flame_scale = 1.0 + 0.2 * math.sin(t * 8)
        if state == 'sleep' or state == 'exhausted': flame_scale = 0.5
        elif state == 'fire_breathe': flame_scale = 2.0 + 0.5 * math.sin(t * 20)
        
        painter.translate(50, -30 + sway)
        painter.scale(flame_scale, flame_scale)
        painter.setBrush(self.flame_color)
        painter.drawEllipse(QPointF(0, 0), 10, 10)
        painter.setBrush(self.flame_inner)
        painter.drawEllipse(QPointF(0, 2), 5, 5)
        painter.restore()

    def draw_wings(self, painter, state, t):
        flap = 0
        if state == 'celebrate' or state == 'fire_breathe': flap = math.sin(t * 15) * 30
        elif state == 'react_click': flap = math.sin(t * 20) * 20 if t < 0.3 else 0
        elif state == 'wander': flap = math.sin(t * 12) * 15
        elif state == 'exhausted': flap = -20 # droop
            
        painter.setPen(QPen(self.outline_color, 3))
        painter.setBrush(self.wing_color)
        for side in [-1, 1]:
            painter.save()
            painter.translate(side * 20, -50)
            painter.rotate(side * (20 + flap))
            path = QPainterPath()
            path.moveTo(0, 0)
            path.quadTo(side * 30, -30, side * 50, -10)
            path.quadTo(side * 25, 0, 0, 10)
            painter.drawPath(path)
            painter.restore()

    def draw_body(self, painter, state, t):
        painter.setPen(QPen(self.outline_color, 3))
        painter.setBrush(self.base_color)
        painter.drawEllipse(QPointF(0, -40), 35, 40)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.belly_color)
        painter.drawEllipse(QPointF(0, -35), 22, 32)

    def draw_legs(self, painter, state, t):
        painter.setPen(QPen(self.outline_color, 3))
        painter.setBrush(self.base_color)
        dangle = math.sin(t * 10) * 15 if state in ['drag', 'react_drag'] else 0
        walk = 0
        if state == 'wander': walk = math.sin(t * 12) * 20
        
        for side in [-1, 1]:
            painter.save()
            painter.translate(side * 20, -10)
            if state == 'wander':
                painter.translate(0, -abs(math.sin(t * 12 + (0 if side==1 else 3.14))) * 5)
            painter.rotate(side * dangle + (walk if side == 1 else -walk))
            painter.drawEllipse(QPointF(0, 0), 12, 10)
            painter.restore()

    def draw_arms(self, painter, state, t):
        painter.setPen(QPen(self.outline_color, 3))
        painter.setBrush(self.base_color)
        
        tap = 0
        if state == 'type':
            tap = math.sin(t * 15) * 5
            
        for side in [-1, 1]:
            painter.save()
            arm_tap = tap if side == 1 else -tap
            if state in ['type', 'focus']:
                painter.translate(side * 15, -30 + arm_tap)
                painter.rotate(side * -30)
            elif state == 'exhausted':
                painter.translate(side * 20, -25)
                painter.rotate(side * -60) # draped over laptop
            else:
                painter.translate(side * 25, -45 + arm_tap)
                if state in ['celebrate', 'fire_breathe']:
                    painter.rotate(side * -130)
                    painter.translate(0, -10)
            painter.drawEllipse(QPointF(0, 0), 8, 14)
            painter.restore()

    def draw_head(self, painter, state, t):
        painter.save()
        
        head_tilt = 0
        if state == 'think': head_tilt = -10
        elif state == 'curious': head_tilt = 15
        elif state == 'listen': head_tilt = -5
        elif state == 'sleep': head_tilt = 5
        elif state == 'exhausted': head_tilt = 25 # drooping head
        
        bob = math.sin(t * 3) * 2 if state in ['idle', 'sit'] else 0
        if state in ['type', 'speak']: bob = math.sin(t * 10) * 2
        elif state == 'exhausted': bob = 15 # head rests low
            
        painter.translate(0, -80 + bob)
        painter.rotate(head_tilt)
        
        # Horns
        painter.setPen(QPen(self.outline_color, 3))
        painter.setBrush(self.horn_color)
        for side in [-1, 1]:
            path = QPainterPath()
            path.moveTo(side * 15, -35)
            path.lineTo(side * 30, -55)
            path.lineTo(side * 40, -25)
            painter.drawPath(path)
            
        # Face
        painter.setBrush(self.base_color)
        painter.drawEllipse(QPointF(0, 0), 45, 38)
        
        # Eyes
        eye_closed = 0.0
        if state in ['sleep', 'listen', 'exhausted']: eye_closed = 1.0
        elif state == 'focus': eye_closed = 0.4
        elif state == 'annoyed': eye_closed = 0.5
        elif state in ['idle', 'sit', 'wander']:
            if (t % 4.0) > 3.8: eye_closed = 1.0
            
        painter.setPen(Qt.NoPen)
        for side in [-1, 1]:
            painter.save()
            painter.translate(side * 18, -5)
            if state == 'exhausted':
                painter.setBrush(self.outline_color)
                painter.drawRect(QRectF(-12, 1, 24, 2)) # Flat sleepy line
            else:
                painter.setBrush(QColor(255, 255, 255))
                painter.drawEllipse(QPointF(0, 0), 12, 16)
                painter.setBrush(self.outline_color)
                painter.drawEllipse(QPointF(side * 2, 0), 8, 12)
                painter.setBrush(QColor(255, 255, 255))
                painter.drawEllipse(QPointF(side * 4, -4), 3, 4)
                painter.setBrush(self.base_color)
                painter.drawRect(QRectF(-15, -20, 30, 40 * eye_closed))
            painter.restore()
            
        # Snout / Mouth
        painter.setPen(QPen(self.outline_color, 2))
        painter.setBrush(Qt.NoBrush)
        
        mouth_open = False
        if state in ['speak', 'celebrate', 'react_click', 'fire_breathe']:
            mouth_open = math.sin(t * 15) > 0 if state == 'speak' else True
            
        if mouth_open:
            painter.setBrush(self.outline_color)
            path = QPainterPath()
            path.moveTo(-5, 12)
            if state == 'fire_breathe':
                path.quadTo(0, 25, 5, 12) # wider mouth
            else:
                path.quadTo(0, 20, 5, 12)
            painter.drawPath(path)
        else:
            path = QPainterPath()
            path.moveTo(-5, 12)
            path.quadTo(0, 16, 5, 12)
            painter.drawPath(path)
            
        if state in ['sleep', 'exhausted']:
            painter.setPen(self.horn_color)
            painter.drawText(QPointF(40, -40 - (t * 20 % 20)), "Z")
            
        painter.restore()

    def draw_fire_breath(self, painter, t):
        painter.save()
        painter.translate(0, -70) # from mouth
        painter.setPen(Qt.NoPen)
        for i in range(5):
            life = (t * 5 - i * 0.2) % 1.0
            if life > 0:
                y = life * 60
                w = 10 + life * 30
                painter.setBrush(self.flame_color if i % 2 == 0 else self.flame_inner)
                painter.drawEllipse(QPointF(math.sin(t*10 + i) * 10, y), w, w)
        painter.restore()
