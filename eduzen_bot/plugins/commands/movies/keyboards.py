from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button


def pelis():
    buttons = [
        [
            Button('🎟️ IMDB', callback_data="get_movie_imdb"),
            Button('🎬️ Trailer', callback_data="get_movie_youtube"),
            Button('🍿 Torrent', callback_data="get_movie_torrent"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)
