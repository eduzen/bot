# Sentences we'll respond with if the user greeted us; only matches on single words
GREETING_KEYWORDS = (
    "hello", "hi", "greetings", "sup", "what's up",
    "hola", "holas", "holis", ''
)
GREETING_RESPONSES = (
    "'sup bro", "hey", "puto el que lee", "hey you get my snap?",
    "hola", 'como va?', 'Hola, todo bien?', 'buenas',
    'holas', 'hola, que tul?', 'era hora de saludar',
    'que hacés che', 'todo tranca humanoide?', 'hi!',
    'bienvenido', 'hola, che, todo piola?', 'que se cuenta',
    'que dice humanoide', 'buenas buenas', 'buenas y santas',
    'era hora che!',
)
# Intro questions: multiword matches
# Note: Apostrophes must be encoded here with a separating space;
# Textblob swallows other punctuation
INTRO_QUESTIONS = (
    "how 's it going", "how are you", "long time no see", "what 's up",
    'qué haces', 'que hacés', 'que hace', 'todo bien?', 'como va',
    'cómo va', 'todo piola?', 'todo bien=', 'todo bien', 'como va?',
    'todo piola?', 'que haces?', 'como estas?', 'como esta?'
)

INTRO_RESPONSES = (
    "todo piola, que se cuenta?", "Podría estar mejor, pero bueno ya fue ja",
    "todo viento en popa.", "Han habido días mejores",
    "Trabajar no es lo mio", "Trabajar no es lo mio, sabelo",
    "Podria estar viajando pero aquí estoy, que onda", 'bien bien',
    "super", "bien digamos", "todo bien", "bien se podría decir",
)

BYE_KEYWORDS = (
    'bye', 'chau', 'chauuu',
)

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
