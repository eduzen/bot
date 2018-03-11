import random

# Sentences we'll respond with if the user greeted us; only matches on single words
GREETING_KEYWORDS = (
    "hello", "hi", "greetings", "sup", "what's up",
    "hola", "holas", "holis", 'buenas'
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
    'todo piola?', 'que haces?', 'como estas?', 'como esta?', 'que se cuenta?',
    'qué hacias', 'que hacias?', 'que hacia', 'que hacias', 'que hacia?'
)

INTRO_RESPONSES = (
    "todo piola, que se cuenta?", "Podría estar mejor, pero bueno ya fue ja",
    "todo viento en popa.", "Han habido días mejores", 'super',
    "Trabajar no es lo mio", "Trabajar no es lo mio, sabelo",
    "Podria estar viajando pero aquí estoy, que onda", 'bien bien',
    "super", "bien digamos", "todo bien", "bien se podría decir",
)

BYE_KEYWORDS = (
    'bye', 'chau', 'chauuu', 'adios', 'saludos'
)

BYE_RESPONSES = (
    'bye bye', 'chauchas', 'chauuu', 'nos vimos', 'hasta luego',
    'cuidate', 'abrazo', 'saludos', 'chau'
)
# Sentences we'll respond with if we have no idea what the user just said
NONE_RESPONSES = (
    'macri gato'
    "si seguro",
    'claro',
    'onda, fijate XD',
    'labura vago',
    'no, manzana',
    'piola',
    'toda la onda',
    'te parece? dejame que lo medito',
    "meet me at the foosball table, bro?",
    "code hard bro",
    "I'd like to add you to my professional network on LinkedIn",
    "Me agregas a instagram",
    'tweeteas vos?',
    'posta',
    'y bue',
)

# If the user tries to tell us something about ourselves, use one of these responses
COMMENTS_ABOUT_SELF = [
    "You're just jealous",
    "I worked really hard on that",
    "My Klout score is {}".format(random.randint(100, 500)),
]

# Template for responses that include a direct noun which is indefinite/uncountable
SELF_VERBS_WITH_NOUN_CAPS_PLURAL = [
    "My last startup totally crushed the {noun} vertical",
    "Were you aware I was a serial entrepreneur in the {noun} sector?",
    "My startup is Uber for {noun}",
    "I really consider myself an expert on {noun}",
]

SELF_VERBS_WITH_NOUN_LOWER = [
    "Yeah but I know a lot about {noun}",
    "My bros always ask me about {noun}",
]

SELF_VERBS_WITH_ADJECTIVE = [
    "I'm personally building the {adjective} Economy",
    "I consider myself to be a {adjective}preneur",
]
