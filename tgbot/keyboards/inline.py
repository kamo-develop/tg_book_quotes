from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.misc.messages import Messages

quote_menu_callback = CallbackData('quote_menu', 'action', 'user_quote_id', 'is_like')


def get_quote_menu_keyboard(user_quote_id):
    return InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(
                    text='👍',
                    callback_data=quote_menu_callback.new(action='like', user_quote_id=user_quote_id, is_like=1)
                ),
                InlineKeyboardButton(
                    text='👎',
                    callback_data=quote_menu_callback.new(action='like', user_quote_id=user_quote_id, is_like=0)
                )
            ],
            [
                InlineKeyboardButton(
                    text=Messages.next_quote_text,
                    callback_data=quote_menu_callback.new(action='next', user_quote_id=0, is_like=0)
                )
            ]
        ]
    )


def get_next_quote_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(
                    text=Messages.next_quote_text,
                    callback_data=quote_menu_callback.new(action='next', user_quote_id=0, is_like=0)
                )
            ]
        ]
    )


first_start_menu_callback = CallbackData('first_start')


def get_first_start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=Messages.first_button_forward,
                    callback_data=first_start_menu_callback.new()
                )
            ]
        ]
    )


genres_choice_menu_callback = CallbackData('genres_choice', 'action', 'genre_id', 'is_start')


def get_text_genre_choice(genres_preference: dict):
    return ('✅ ' if genres_preference.get('is_preferences') is True else '') + genres_preference.get('title')


def get_genres_choice_keyboard(genres_preferences: list, is_start: bool):
    m = 1
    n = len(genres_preferences) // m

    buttons = \
    [
        [
            InlineKeyboardButton(
                text=get_text_genre_choice(genres_preferences[i * m + j]),
                callback_data=genres_choice_menu_callback.new(
                    action='genre',
                    genre_id=genres_preferences[i * m + j].get('genre_id'),
                    is_start=int(is_start)
                )
            )
            for j in range(m)
        ]
        for i in range(n)
    ]

    if len(genres_preferences) % m != 0:
        buttons.append([
            InlineKeyboardButton(
                text=get_text_genre_choice(genres_preferences[-1]),
                callback_data=genres_choice_menu_callback.new(
                    action='genre',
                    genre_id=genres_preferences[-1].get('genre_id'),
                    is_start=int(is_start)
                )
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text=Messages.start_quote_text if is_start else Messages.next_quote_text,
            callback_data=genres_choice_menu_callback.new(
                action='next',
                genre_id=0,
                is_start=int(is_start)
            )
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
