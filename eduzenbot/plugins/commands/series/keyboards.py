from telegram import InlineKeyboardButton as Button
from telegram import InlineKeyboardMarkup


def serie():
    buttons = [
        [
            Button("Latest episodes (torrents)", callback_data="latest_episodes"),
            Button("Load all episodes (torrents)", callback_data="all_episodes"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def _go_back_button():
    return [Button("« Back to Main", callback_data="go_back_serie")]


def serie_go_back_keyboard():
    return InlineKeyboardMarkup([_go_back_button()])


def serie_season(seasons):
    COLUMNS = 2
    buttons = [
        Button(f"Season {season}", callback_data=f"get_season_{season}") for season, _ in sorted(seasons.items())
    ]
    columned_keyboard = [buttons[i : i + COLUMNS] for i in range(0, len(buttons), COLUMNS)]
    columned_keyboard.append(_go_back_button())

    return InlineKeyboardMarkup(columned_keyboard)


def serie_episodes(episodes_dict):
    COLUMNS = 5
    buttons = [
        Button(f"Ep {ep_number}", callback_data=f"get_episode_{ep_number}")
        for ep_number, episode in sorted(episodes_dict.items())
    ]
    columned_keyboard = [buttons[i : i + COLUMNS] for i in range(0, len(buttons), COLUMNS)]
    columned_keyboard.append(_go_back_button())

    return InlineKeyboardMarkup(columned_keyboard)
