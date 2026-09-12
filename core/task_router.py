class TaskRouter:
    def __init__(self, state_machine, window):
        self.sm = state_machine
        self.window = window
        
    def handle_event(self, event_type, data=None):
        current = self.sm.get_state()
        if event_type == "pomodoro_start":
            self.sm.request_state('focus')
            self.window.say("Time to focus!")
        elif event_type == "pomodoro_break":
            self.sm.request_state('break_time')
            self.window.say("Break time! Stretch your wings!")
        elif event_type == "late_night":
            self.sm.request_state('sleep')
            self.window.say("Zzz... so late...")
        elif event_type == "click":
            if current != 'react_drag':
                self.sm.force_state('react_click')
                self.window.say("Rawr!")
        elif event_type == "idle_chat":
            if current == 'idle':
                self.sm.request_state('speak')
                self.window.say("Just hanging around!")
        elif event_type == "drag_start":
            self.sm.force_state('react_drag')
            if hasattr(self.window, 'hide_bubble'):
                self.window.hide_bubble()
            elif hasattr(self.window, 'speech_bubble'):
                self.window.speech_bubble.hide()
        elif event_type == "drag_end":
            self.sm.force_state('idle')
        elif event_type == "type_finished":
            if current in ['type', 'speak']:
                self.sm.request_state('idle')
