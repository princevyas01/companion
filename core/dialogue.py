import random

LINES = {
    "idle": [
        "Hoot!", "Just watching the clouds...", "Nice weather for coding.", "*ruffles feathers*",
        "Did you hear that?", "I could use a nap.", "What are we building today?",
        "Ten more minutes and I get a treat, right?", "*stares out the window*",
        "This is a good spot to sit."
    ],
    "pomodoroStart": [
        "Focus time! I'll keep watch.", "Let's get this done together.", "Quiet mode: activated.",
        "No distractions — I'll guard the door.", "25 minutes. Let's go.",
        "I believe in you. Also I'm not moving for 25 minutes."
    ],
    "pomodoroEnd": [
        "Break time! Stretch those wings.", "You earned this break.", "Nice work that round!",
        "That's one down. Water break?", "Look at you go. Proud of you.",
        "Get up, walk around, blink at something far away."
    ],
    "lateNight": [
        "It's pretty late... you okay?", "*yawn* Almost bedtime for owls too.", "Night owl mode, huh?",
        "The rest of the house is asleep. Just saying.", "One more task, then bed?",
        "I'll still be here in the morning either way."
    ],
    "morning": [
        "Good morning!", "Ready for a good day?", "*stretches wings* Morning!",
        "Coffee first, then world domination?", "Let's make today a good one."
    ],
    "ignored": [
        "Hoo-hoo? Still there?", "I'm still here if you need me.", "*taps beak impatiently*",
        "No rush. Just checking in.", "I'll just be over here."
    ],
    "hungry": [
        "My tummy's rumbling...", "Got any snacks?", "*stares at you meaningfully*",
        "Feeding time soon?", "I smell food. Where's my food."
    ],
    "clicked": [
        "Hey!", "Hoot hoot!", "*happy wiggle*", "That tickles!",
        "Again! Again!", "You know just where to click."
    ],
    "annoyed": [
        "Okay, okay, put me down!", "*ruffled feathers* A little gentler please.", "Hoot! Too much!",
        "I have limits, you know.", "Message received. Gently, please."
    ],
    "weekend": [
        "It's the weekend. We could just... not work.",
        "Saturday brain only accepts snacks and naps."
    ],
    "rainyDay": [
        "It's raining out there. Cozy in here though.",
        "Good day to stay in and get things done."
    ],
    "lowBattery": [
        "Your laptop's getting low — might want to plug in.",
        "20% battery. Living dangerously."
    ],
    "posture": [
        "Posture check! Sit up straight.",
        "Look at something 20 feet away for 20 seconds. It helps!",
        "Have you blinked recently? Drink some water."
    ]
}

def get_line(category):
    lines = LINES.get(category, LINES["idle"])
    return random.choice(lines)
