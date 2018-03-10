# Sentences we'll respond with if the user greeted us; only matches on single words
GREETING_KEYWORDS = (
    "hello", "hi", "greetings", "sup", "what's up",
    "hola", "holas", "holis",
    "hello", "hi", "greetings", "sup",
)
GREETING_RESPONSES = [
    "'sup bro", "hey", "*nods*", "hey you get my snap?"]

# Intro questions: multiword matches
# Note: Apostrophes must be encoded here with a separating space; Textblob swallows other punctuation
INTRO_QUESTIONS = ("how 's it going", "how are you", "long time no see", "what 's up")

INTRO_RESPONSES = [
    "I'm good, how about you?", "Could be better, but oh well.",
    "Let me tell you about my last workout.", "I've had better days.",
    "Work is giving me a headache"
]

FILTER_WORDS = set([
    "skank",
    "wetback",
    "bitch",
    "cunt",
    "dick",
    "douchebag",
    "dyke",
    "fag",
    "nigger",
    "tranny",
    "trannies",
    "paki",
    "pussy",
    "retard",
    "slut",
    "titt",
    "tits",
    "wop",
    "whore",
    "chink",
    "fatass",
    "shemale",
    "nigga",
    "daygo",
    "dego",
    "dago",
    "gook",
    "kike",
    "kraut",
    "spic",
    "twat",
    "lesbo",
    "homo",
    "fatso",
    "lardass",
    "jap",
    "biatch",
    "tard",
    "gimp",
    "gyp",
    "chinaman",
    "chinamen",
    "golliwog",
    "crip",
    "raghead",
    "negro",
    "hooker"
])
