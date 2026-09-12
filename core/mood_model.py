from PyQt5.QtCore import QObject, QTimer

class MoodModel(QObject):
    def __init__(self, decay_ms=300000):
        super().__init__()
        self.energy = 100
        self.affection = 100
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.decay)
        self.timer.start(decay_ms)
        
    def decay(self):
        self.energy = max(0, self.energy - 2)
        self.affection = max(0, self.affection - 1)
        
    def boost_affection(self, amount):
        self.affection = min(100, self.affection + amount)
        
    def expend_energy(self, amount):
        self.energy = max(0, self.energy - amount)
