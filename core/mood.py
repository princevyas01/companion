import time
from datetime import datetime
from core.dialogue import get_line

class MoodSystem:
    """Tracks energy, affection, hunger, irritation, focus, and time-of-day awareness."""
    
    def __init__(self):
        self.energy = 100.0
        self.affection = 80.0
        self.hunger = 0.0
        self.irritation = 0.0
        self.focus_level = 0.0
        self.excitement = 50.0
        self.last_interaction_time = time.time()
        self.continuous_typing_secs = 0.0
        self.sleep_on_video = True

    def wake_up_refresh(self):
        """Restores energy fully when woken up by user interaction so pet doesn't instantly re-sleep."""
        self.energy = 100.0
        self.register_interaction()

    def tick(self):
        """Called every ~8 seconds by the idle timer."""
        hour = datetime.now().hour
        
        # Energy drains faster late at night
        if hour >= 23 or hour < 5:
            self.energy = max(0, self.energy - 0.3)
        else:
            self.energy = max(0, self.energy - 0.05)
        
        self.affection = max(0, self.affection - 0.02)
        self.hunger = min(100, self.hunger + 0.1)
        self.irritation = max(0, self.irritation - 0.5)
        self.excitement = max(30, self.excitement - 0.1)
        
        # If ignored for a long time, get hungry/bored
        idle_secs = time.time() - self.last_interaction_time
        if idle_secs > 300:  # 5 minutes
            self.hunger = min(100, self.hunger + 0.5)
            self.affection = max(0, self.affection - 0.1)

    def register_interaction(self):
        self.last_interaction_time = time.time()
        self.excitement = min(100, self.excitement + 5)

    def register_typing(self, dt):
        """Called when user is actively typing."""
        self.continuous_typing_secs += dt
        self.register_interaction()

    def stop_typing(self):
        self.continuous_typing_secs = 0.0

    def is_exhausted_from_typing(self):
        return self.continuous_typing_secs >= 300.0  # Require 5 minutes of continuous typing to get exhausted

    def boost(self, amount):
        self.energy = min(100, self.energy + amount)
        self.affection = min(100, self.affection + amount)
        self.hunger = max(0, self.hunger - amount)
        self.irritation = 0
        self.register_interaction()

    def annoy(self):
        self.irritation = min(100, self.irritation + 25)
        self.affection = max(0, self.affection - 5)

    def is_sleepy(self):
        hour = datetime.now().hour
        if hour >= 0 and hour < 6:
            return self.energy < 50
        return self.energy < 15

    def is_annoyed(self):
        return self.irritation > 50

    def is_hungry(self):
        return self.hunger > 60

    def get_time_greeting(self):
        """Returns a time-appropriate greeting."""
        hour = datetime.now().hour
        if 5 <= hour < 9:
            return get_line("morning")
        elif 9 <= hour < 12:
            return get_line("idle")
        elif 12 <= hour < 14:
            return get_line("hungry")
        elif 14 <= hour < 21:
            return get_line("idle")
        else:
            return get_line("lateNight")

    def is_late_night(self):
        hour = datetime.now().hour
        return hour >= 23 or hour < 5

    def is_morning(self):
        hour = datetime.now().hour
        return 5 <= hour < 9

    def get_idle_seconds(self):
        return time.time() - self.last_interaction_time
