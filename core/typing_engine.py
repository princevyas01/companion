from PyQt5.QtCore import QTimer

class TypingEngine:
    def __init__(self, window):
        self.window = window
        self.full_text = ""
        self.current_idx = 0
        self.timer = QTimer(self.window)
        self.timer.timeout.connect(self.type_next_char)
        self.on_complete = None
        self.caret_visible = False
        self.caret_timer = QTimer(self.window)
        self.caret_timer.timeout.connect(self.toggle_caret)

    def start_typing(self, text, on_complete=None):
        self.full_text = text
        self.current_idx = 0
        self.on_complete = on_complete
        
        self.window.speech_bubble.set_text("")
        self.window.speech_bubble.show()
        
        self.caret_visible = True
        self.window.speech_bubble.set_caret(self.caret_visible)
        
        self.caret_timer.start(400)
        self.type_next_char()

    def type_next_char(self):
        if self.current_idx < len(self.full_text):
            self.current_idx += 1
            current_text = self.full_text[:self.current_idx]
            self.window.speech_bubble.set_text(current_text)
            
            char = self.full_text[self.current_idx - 1]
            delay = 40
            if char in ['.', '!', '?']:
                delay = 300
            elif char in [',']:
                delay = 150
                
            self.timer.start(delay)
            self.window.state_machine.force_state('type')
        else:
            self.timer.stop()
            if self.on_complete:
                self.on_complete()
            else:
                self.window.state_machine.request_state('idle')
                # Keep bubble up for 2 seconds
                QTimer.singleShot(2000, self.stop_typing)

    def toggle_caret(self):
        self.caret_visible = not self.caret_visible
        self.window.speech_bubble.set_caret(self.caret_visible)

    def stop_typing(self):
        self.timer.stop()
        self.caret_timer.stop()
        self.window.speech_bubble.hide()
