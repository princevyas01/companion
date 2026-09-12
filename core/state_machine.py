class StateMachine:
    """Central animation state machine with priority-based transitions."""
    
    PRIORITIES = {
        'react_drag': 1,
        'wake': 2,
        'speak': 3,
        'type': 4,
        'react_click': 5,
        'celebrate': 6,
        'fire_breathe': 7,
        'jump': 7,
        'bark': 7,
        'eat': 7,
        'fetch': 7,
        'happy': 7,
        'pounce': 7,
        'meow': 7,
        'clean': 7,
        'stretch': 7,
        'purr': 7,
        'exhausted': 8,
        'sleep': 9,
        'focus': 10,
        'break_time': 11,
        'think': 12,
        'listen': 13,
        'annoyed': 14,
        'curious': 15,
        'wander': 16,
        'perch': 17,
        'sit': 18,
        'idle': 19
    }

    def __init__(self):
        self.current_state = 'idle'
        self.previous_state = 'idle'
        self.time_in_state = 0.0

    def request_state(self, new_state):
        """Request a transition — only succeeds if new_state has equal or higher priority (lower number)."""
        curr_prio = self.PRIORITIES.get(self.current_state, 99)
        new_prio = self.PRIORITIES.get(new_state, 99)
        
        if new_prio <= curr_prio or new_state == 'idle':
            self.previous_state = self.current_state
            self.current_state = new_state
            self.time_in_state = 0.0
            return True
        return False
        
    def force_state(self, new_state):
        """Force a state change regardless of priority."""
        self.previous_state = self.current_state
        self.current_state = new_state
        self.time_in_state = 0.0

    def get_state(self):
        return self.current_state
        
    def tick(self, dt):
        self.time_in_state += dt
