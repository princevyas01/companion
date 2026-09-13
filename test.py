import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtCore import QRect, QRectF
from ui.dog_animator import DogAnimator
from ui.white_hamster_animator import WhiteHamsterAnimator
from ui.yellow_guardian_hamster_animator import YellowGuardianHamsterAnimator

class Dummy:
    def __init__(self, s): self.s = s
    def get_state(self): return self.s
    def force_state(self, s): self.s = s
    @property
    def time_in_state(self): return 1.0

app = QApplication(sys.argv)
states = ['idle', 'tongue_out', 'happy', 'sit', 'sit_down', 'bark', 'celebrate', 'sleep', 'exhausted', 'wake', 'react_click', 'drag', 'react_drag', 'focus', 'annoyed', 'wander', 'type']
for s in states:
    anim = DogAnimator(Dummy(s))
    img = QImage(100, 100, QImage.Format_ARGB32)
    p = QPainter(img)
    anim.draw(p, QRectF(0, 0, 100, 100))
    p.end()

# Smoke test hamster animators
dummy_sm = Dummy('idle')
white_anim = WhiteHamsterAnimator(dummy_sm)
yellow_anim = YellowGuardianHamsterAnimator(dummy_sm)
img = QImage(350, 400, QImage.Format_ARGB32)
p = QPainter(img)
rect = QRect(25, 230, 150, 160)
white_anim.draw(p, rect)
yellow_anim.draw(p, rect)
p.end()

print('All pet smoke tests passed cleanly!')
