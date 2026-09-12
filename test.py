import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtCore import QRectF
from ui.dog_animator import DogAnimator
class Dummy:
    def __init__(self, s): self.s = s
    def get_state(self): return self.s
    @property
    def time_in_state(self): return 1.0
app = QApplication(sys.argv)
states = ['idle', 'tongue_out', 'happy', 'sit', 'sit_down', 'bark', 'celebrate', 'sleep', 'exhausted', 'wake', 'react_click', 'drag', 'react_drag', 'focus', 'annoyed', 'wander', 'type']
for s in states:
    print('testing', s)
    anim = DogAnimator(Dummy(s))
    img = QImage(100, 100, QImage.Format_ARGB32)
    p = QPainter(img)
    anim.draw(p, QRectF(0, 0, 100, 100))
    p.end()
print('ok')
