from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button


def serie_keyboard():
    buttons = [
        [
            Button('Latest episodes', callback_data='latest_episodes'),
            Button('Load all episodes', callback_data='all_episodes')
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def serie_go_back_keyboard():
    buttons = [
        [Button('« Back to Main', callback_data="go_back_serie")]
    ]
    return InlineKeyboardMarkup(buttons)


def serie_season(seasons):
    COLUMNS = 2
    buttons = [
        Button(f'Season {season}', callback_data=f"get_season_{season}")
        for season, episodes in sorted(seasons.items())
    ]
    columned_keyboard= [
        buttons[i:i+COLUMNS] for i in range(0, len(buttons), COLUMNS)
    ]
    columned_keyboard.append([Button('« Back to Main', callback_data="go_back_serie")])

    return InlineKeyboardMarkup(columned_keyboard)
