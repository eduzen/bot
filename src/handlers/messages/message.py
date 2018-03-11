import os
import logging
import random
import codecs
from datetime import datetime

from db import User
from .vocabulary import (
    GREETING_KEYWORDS, GREETING_RESPONSES,
    INTRO_QUESTIONS,
    SELF_VERBS_WITH_NOUN_LOWER,
    SELF_VERBS_WITH_ADJECTIVE,
    SELF_VERBS_WITH_NOUN_CAPS_PLURAL,
    NONE_RESPONSES, COMMENTS_ABOUT_SELF,
    INTRO_RESPONSES, BYE_KEYWORDS,
    BYE_RESPONSES

)
os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'
from textblob import TextBlob

logger = logging.getLogger(__name__)


def record_msg(msg):
    with codecs.open('history.txt', 'a', "utf-8") as f:
        msg = f'{datetime.now().isoformat()} - {msg}'
        f.write(msg)


def check_for_greeting(sentence):
    for word in sentence.words:
        if word.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)


def check_for_bye(sentence):
    for word in sentence.words:
        if word.lower() in BYE_KEYWORDS:
            return random.choice(BYE_RESPONSES)


def check_for_intro_question(sentence):
    """Sometimes people greet by introducing a question."""
    if sentence in INTRO_QUESTIONS:
        return random.choice(INTRO_RESPONSES)


def get_or_create_user(username, userid):
    User.get_or_create(
        username=username,
        id=userid
    )


def find_pronoun(sent):
    """Given a sentence, find a preferred pronoun to respond with.
    Returns:
        None if no candidate
        pronoun is found in the input
    """
    pronoun = None

    for word, part_of_speech in sent.pos_tags:
        # Disambiguate pronouns
        if part_of_speech == 'PRP' and word.lower() in ('vos', 'tu'):
            pronoun = 'Yo'
        elif part_of_speech == 'PRP' and word.lower() == 'yo':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'vos'
    return pronoun


def find_verb(sent):
    """Pick a candidate verb for the sentence."""
    verb = None
    pos = None
    for word, part_of_speech in sent.pos_tags:
        if part_of_speech.startswith('VB'):  # This is a verb
            verb = word
            pos = part_of_speech
            break
    return verb, pos


def find_noun(sent):
    """Given a sentence, find the best candidate noun."""
    noun = None

    if not noun:
        for w, p in sent.pos_tags:
            if p == 'NN':  # This is a noun
                noun = w
                break
    if noun:
        logger.info("Found noun: %s", noun)

    return noun


def find_adjective(sent):
    """Given a sentence, find the best candidate adjective."""
    adj = None
    for w, p in sent.pos_tags:
        if p == 'JJ':  # This is an adjective
            adj = w
            break
    return adj


def find_candidate_parts_of_speech(parsed):
    """Given a parsed input, find the best pronoun, direct noun,
    adjective, and verb to match their input.
    Returns a tuple of pronoun, noun, adjective, verb any of which may
    be None if there was no good match
    """
    pronoun = None
    noun = None
    adjective = None
    verb = None
    for sent in parsed.sentences:
        pronoun = find_pronoun(sent)
        noun = find_noun(sent)
        adjective = find_adjective(sent)
        verb = find_verb(sent)

    logger.info("Pronoun=%s, noun=%s, adjective=%s, verb=%s", pronoun, noun, adjective, verb)
    return pronoun, noun, adjective, verb


def construct_response(pronoun, noun, verb):
    """No special cases matched, so we're going to try to construct
    a full sentence that uses as much of the user's input as possible
    """
    resp = []

    if pronoun:
        resp.append(pronoun)
    print(pronoun)
    fruta = 'dificil de saber'
    return fruta


def check_for_comment_about_bot(pronoun, noun, adjective):
    """Check if the user's input was about the bot itself,
    in which case try to fashion a response that feels
    right based on their input.
    Returns:
        str the new best sentence, or None.
    """
    resp = None
    if pronoun == 'Yo' and (noun or adjective):
        if noun:
            if random.choice((True, False)):
                resp = random.choice(
                    SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(
                    **{'noun': noun.pluralize().capitalize()}
                )
            else:
                resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
        else:
            resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp


def parse_chat(msg):
    parsed = TextBlob(msg)

    pronoun, noun, adjective, verb = find_candidate_parts_of_speech(parsed)
    resp = check_for_comment_about_bot(pronoun, noun, adjective)

    # If we just greeted the bot, we'll use a return greeting
    logger.info(resp)
    if not resp:
        resp = check_for_greeting(parsed)

    # If we were asked an intro question, we'll return an intro response
    if not resp:
        resp = check_for_intro_question(parsed)

    if not resp:
        # If we didn't override the final sentence, try to construct a new one:
        if not pronoun:
            resp = random.choice(NONE_RESPONSES)
        elif pronoun == 'I' and not verb:
            resp = random.choice(COMMENTS_ABOUT_SELF)
        else:
            resp = construct_response(pronoun, noun, verb)

    # If we got through all that with nothing, use a random response
    if not resp:
        resp = random.choice(NONE_RESPONSES)

    return resp


def parse_regular_chat(msg):
    parsed = TextBlob(msg)
    answer = False
    for sentence in parsed.sentences:
        answer = check_for_greeting(sentence)
        if answer:
            return answer
        bye = check_for_bye(sentence)
        if bye:
            return bye
        question = check_for_intro_question(sentence)
        if question:
            return question

    return answer


def parse_msgs(bot, update):
    logger.info(f"parse_msgs... by {update.message.from_user.name}")
    msg = update.message.text
    msg = f'{update.message.from_user.name}: {msg}\n'
    record_msg(msg)

    get_or_create_user(
        update.message.from_user.name,
        update.message.from_user.id
    )

    raw_msg = update.message.text_html
    if 'jaja' in raw_msg or 'jeje' in raw_msg:
        bot.send_message(chat_id=update.message.chat_id, text='jaja')
        return

    entities = update.message.parse_entities()
    if not entities:
        answer = parse_regular_chat(raw_msg)
        if answer:
            bot.send_message(chat_id=update.message.chat_id, text=answer)
        return

    mentions = [value for key, value in entities.items()]

    if '@eduzen_bot' not in mentions and '@eduzenbot' not in mentions:
        return

    raw_msg = raw_msg.replace('@eduzenbot', 'vos').replace('@eduzen_bot', 'tu')
    answer = parse_chat(raw_msg)

    bot.send_message(
        chat_id=update.message.chat_id,
        text=answer
    )
