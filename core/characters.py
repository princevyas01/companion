from core.dialogue import LINES

# Default lines for characters that don\'t override them
DEFAULT_LINES = LINES

CHARACTER_PROFILES = {
    "dragon": {
        "name": "Dragon Companion",
        "type": "dragon",  # Uses DragonAnimator
        "supported_actions": [
            "celebrate",
            "fire_breathe",
            "think",
            "wander",
            "sleep",
            "exhausted",
            "focus",
            "type",
            "wake"
        ],
        "lines": DEFAULT_LINES
    },
    "dog": {
        "name": "Puppy Dog",
        "type": "dog", # Uses DogAnimator
        "supported_actions": [
            "tongue_out",
            "sit",
            "bark",
            "celebrate",
            "jump",
            "eat",
            "fetch",
            "happy",
            "wander",
            "sleep",
            "think",
            "focus",
            "type",
            "wake"
        ],
        "lines": {
            "idle": [
                "Woof! Want to play?", "Tail wagging happily!", "*Pant pant*",
                "Boop my nose!", "Who\'s a good pet?"
            ],
            "posture": [
                "Sit up straight! Woof!", "Don\'t slouch, human!"
            ],
            "hungry": [
                "Treat time? Woof!", "Need treats!", "*Stares at treat bowl*"
            ],
            "clicked": [
                "Woof! *Happy tail wag*", "Belly rubs please!", "Arf!"
            ],
            "pomodoroStart": [
                "Time to focus! I\'ll guard your desk!", "Woof! Let\'s get to work!"
            ],
            "pomodoroEnd": [
                "Break time! Let me get a treat!", "Woof! You did great!"
            ],
            "lateNight": [
                "Yawn... Time for bed?", "Sleeping on the rug... Zzz"
            ]
        }
    },
    "luffy": {
        "name": "Luffy",
        "type": "sprite",  # Uses SpriteAnimator
        "image_path": "assets/luffy.png",
        "supported_actions": [
            "celebrate",
            "gum_stretch",
            "gear2",
            "gear3",
            "gear5",
            "think",
            "wander",
            "sleep",
            "focus",
            "wake"
        ],
        "lines": {
            "idle": [
                "I\'m gonna be King of the Pirates!", "Meat...", "Is it time to eat?",
                "I\'m so bored!", "Let\'s go on an adventure!"
            ],
            "pomodoroStart": [
                "Alright! Let\'s get to work!", "Focus time!"
            ],
            "pomodoroEnd": [
                "Time for meat!", "Break time! Let\'s eat!"
            ],
            "morning": [
                "Morning! Where\'s breakfast?"
            ],
            "hungry": [
                "Meat... I need meat...", "Sanji! Food!"
            ],
            "clicked": [
                "Hey! Cut it out!", "Shishishi!"
            ]
        }
    },
    "cat_orange": {
        "name": "Orange Tabby Cat",
        "type": "cat",
        "cat_variant": "cat_orange",
        "supported_actions": [
            "meow", "pounce", "clean", "stretch", "purr", "sleep", "sit", "wander", "happy", "wake"
        ],
        "lines": {
            "idle": ["Meow~", "*Purrrrr*", "Sunbathing time...", "Pet me human!", "*Makes biscuits*"],
            "hungry": ["Meow! Fish please!", "*Stares at empty food bowl*"],
            "clicked": ["Purrrr... *head butt*", "Meow! *tail curl*", "Nyan!"],
            "pomodoroStart": ["I\'ll nap on your keyboard while you work!", "Meow! Good luck!"],
            "pomodoroEnd": ["Break time! Time for cat treats!", "Purrrr... You worked hard!"]
        }
    },
    "cat_tuxedo": {
        "name": "Ghibli Tuxedo Cat",
        "type": "cat",
        "cat_variant": "cat_tuxedo",
        "supported_actions": [
            "meow", "pounce", "clean", "stretch", "purr", "sleep", "sit", "wander", "happy", "wake"
        ],
        "lines": {
            "idle": ["Meow~", "*Gentle purr*", "Watchful guardian...", "*Licks paw*"],
            "hungry": ["Meow! Fish please!"],
            "clicked": ["Meow! *happy chirp*", "Purrrr...", "*Blinks slowly*"],
            "pomodoroStart": ["I\'ll keep watch from your desktop!", "Meow! Focus time!"],
            "pomodoroEnd": ["Time to play! Meow!"]
        }
    },
    "cats_duo": {
        "name": "Forest Cat Duo (Both Cats)",
        "type": "cat",
        "cat_variant": "cats_duo",
        "supported_actions": [
            "meow", "pounce", "clean", "stretch", "purr", "sleep", "sit", "wander", "happy", "wake"
        ],
        "lines": {
            "idle": ["Meow meow! *Double purr*", "Best friends forever!", "Sunbathing together!"],
            "hungry": ["Double treats please! Meow!"],
            "clicked": ["*Double head butts*", "Purrrr... *Happy cats*!"],
            "pomodoroStart": ["We\'ll guard your desktop together!"],
            "pomodoroEnd": ["Break time! Let me & my buddy play!"]
        }
    },
    "fox": {
        "name": "Kitsune Fox",
        "type": "chibi_animal",
        "species": "fox",
        "supported_actions": [
            "tail_sway", "curious", "wander", "celebrate", "sleep", "sit", "wake"
        ],
        "lines": {
            "idle": ["*Ears perk up*", "Yip! Exploring the forest!", "*Fluffy tail swishes*", "What\'s that over there?"],
            "hungry": ["Berries or snacks please! Yip!", "*Sniffs curiously at your desk*"],
            "clicked": ["Yip yip! *Happy bounce*", "*Nuzzles gently*", "Hehe, that tickles!"],
            "pomodoroStart": ["I\'ll keep watch with sharp ears!", "Time to focus! Let\'s go!"],
            "pomodoroEnd": ["Break time! Time for a forest run!", "Yip! Outstanding work!"]
        }
    },
    "rabbit": {
        "name": "Chibi Bunny",
        "type": "chibi_animal",
        "species": "rabbit",
        "supported_actions": [
            "hop", "nose_twitch", "wander", "celebrate", "sleep", "sit", "wake"
        ],
        "lines": {
            "idle": ["*Nose twitches rapidly*", "Hop hop hop!", "*Ears flop happily*", "Munching on clover..."],
            "hungry": ["Got any fresh carrots?", "*Binky hop for treats!*"],
            "clicked": ["*Soft bunny thumping*", "*Happy purr-grind*", "Hop!"],
            "pomodoroStart": ["Quiet bunny focus mode activated!", "I\'ll sit quietly while you work!"],
            "pomodoroEnd": ["*Binky celebration!* Break time!", "Hop hooray! Great job!"]
        }
    },
    "penguin": {
        "name": "Waddling Penguin",
        "type": "chibi_animal",
        "species": "penguin",
        "supported_actions": [
            "waddle", "flap", "wander", "celebrate", "sleep", "sit", "wake"
        ],
        "lines": {
            "idle": ["*Happy waddle*", "Honk! Looking for icebergs!", "*Flaps tiny flippers*", "Slide into adventure!"],
            "hungry": ["Fish please! *Honk honk!*", "*Stares with big round eyes*"],
            "clicked": ["*Excited wing flaps*", "Waddle waddle!", "Brrr! So cozy!"],
            "pomodoroStart": ["Cool heads accomplish great things!", "Penguin focus engaged!"],
            "pomodoroEnd": ["Time to slide into the break pool!", "Honk! Fantastic job!"]
        }
    },
    "hamster": {
        "name": "Cheeky Hamster",
        "type": "chibi_animal",
        "species": "hamster",
        "supported_actions": [
            "scurry", "cheek_puff", "wander", "celebrate", "sleep", "sit", "wake"
        ],
        "lines": {
            "idle": ["*Sniff sniff*", "Cheeks full of sunflower seeds!", "*Tiny rapid paws*", "Scurry scurry!"],
            "hungry": ["Seeds please! My cheek pouches have room!", "*Tiny paws begging*"],
            "clicked": ["Squeak! *Happy nibble*", "*Puffs cheeks happily*", "Hehe!"],
            "pomodoroStart": ["Spinning the wheel of productivity!", "Let\'s scurry through your tasks!"],
            "pomodoroEnd": ["Break time! Snack stash unlocked!", "Squeak! High five!"]
        }
    },
    "owl": {
        "name": "Wise Chibi Owl",
        "type": "chibi_animal",
        "species": "owl",
        "supported_actions": [
            "head_turn", "wing_flap", "wander", "celebrate", "sleep", "perch", "wake"
        ],
        "lines": {
            "idle": ["Hoo hoo!", "*Rotates head 180 degrees*", "Observing wisdom...", "*Fluffs soft feathers*"],
            "hungry": ["Midnight snacks are the best snacks!", "*Hooting politely*"],
            "clicked": ["Hoo! *Wise blink*", "*Feather ruffle*", "Greetings, scholar!"],
            "pomodoroStart": ["Deep wisdom requires deep focus. Proceed.", "Hoo! Stay diligent."],
            "pomodoroEnd": ["Knowledge earned deserves a restful pause.", "Hoo! Excellent progress!"]
        }
    },
    "panda": {
        "name": "Sleepy Panda",
        "type": "chibi_animal",
        "species": "panda",
        "supported_actions": [
            "slow_walk", "roll", "wander", "celebrate", "sleep", "sit", "wake"
        ],
        "lines": {
            "idle": ["*Chomp chomp bamboo*", "Slow and steady...", "*Lazy roll*", "Life is good..."],
            "hungry": ["Bamboo shoots please!", "*Rumbles tummy peacefully*"],
            "clicked": ["*Soft panda hug*", "Yawn... Big cuddles!", "Roly-poly!"],
            "pomodoroStart": ["Let\'s work steadily like a calm panda.", "Focus time, then nap time!"],
            "pomodoroEnd": ["Break time! Time to roll around!", "You did great, now relax!"]
        }
    },

    "white_hamster": {
        "name": "White Meme Hamster",
        "type": "white_hamster",
        "supported_actions": [
            # Six existing expression controls.
            "laugh",
            "smile",
            "neutral",
            "tongue_out",
            "halo",
            "costume",

            # Movement controls.
            "jump",
            "wander",

            # Additional supplied sticker actions.
            "magic",
            "type",
            "focus",
            "eat",
            "sad",
            "happy",
            "paint",
            "cook"
        ],
        "lines": {
            "idle": [
                "*stares at you*",
                "*tiny hamster noises*",
                "hmm.",
                "*wiggles*"
            ],
            "hungry": [
                "*looks for snacks*",
                "I want a tiny snack.",
                "*stares intensely at food*"
            ],
            "clicked": [
                "*big hamster smile*",
                "hehe.",
                "*wiggles happily*"
            ],
            "action_magic": [
                "*waves the magic wand*",
                "*tiny magical hamster*"
            ],
            "action_type": [
                "*opens the book and gets serious*",
                "Focus time."
            ],
            "action_eat": [
                "*munch munch*",
                "Watermelon!"
            ],
            "action_sad": [
                "*tiny hamster tears*",
                "Oh no..."
            ],
            "action_happy": [
                "hehe!",
                "*big happy hamster grin*"
            ],
            "action_paint": [
                "*paints carefully*",
                "Art time."
            ],
            "action_cook": [
                "*chef hamster at work*",
                "Cooking!"
            ],
            "click": [
                "*big hamster smile*",
                "hehe.",
                "*wiggles happily*"
            ],
            "pomodoroStart": [
                "*puts on the serious outfit*",
                "Okay. We work now."
            ],
            "pomodoroEnd": [
                "*throws paws in the air*",
                "Done! Time to celebrate."
            ],
            "lateNight": [
                "*sleepy hamster stare*",
                "I think it is nap time."
            ]
        }
    },

    "yellow_guardian_hamster": {
        "name": "Yellow Guardian Hamster",
        "type": "yellow_guardian_hamster",
        "supported_actions": [
            "jump",
            "wave",
            "happy",
            "laugh",
            "point",
            "react_click",
            "wander",
            "celebrate",
            "sleep",
            "think",
            "focus",
            "type",
            "wake"
        ],
        "lines": {
            "idle": [
                "hehe.",
                "Ready.",
                "Guardian mode.",
                "Standing by..."
            ],
            "clicked": [
                "Hehe!",
                "Boop.",
                "Hey!"
            ],
            "click": [
                "Hehe!",
                "Boop.",
                "Hey!"
            ],
            "pomodoroStart": [
                "Focus mode.",
                "We work now."
            ],
            "pomodoroEnd": [
                "Finished.",
                "Break time."
            ],
            "hungry": [
                "Snack?",
                "Tiny snack please."
            ],
            "lateNight": [
                "Sleep mode soon.",
                "Too late..."
            ]
        }
    },
}

def get_character_config(char_id):
    return CHARACTER_PROFILES.get(char_id, CHARACTER_PROFILES["dragon"])

def get_character_line(char_id, category):
    config = get_character_config(char_id)
    lines_dict = config.get("lines", DEFAULT_LINES)
    # Fallback to default if category is missing in this character\'s lines
    lines = lines_dict.get(category, DEFAULT_LINES.get(category, ["..."]))
    import random
    return random.choice(lines)
