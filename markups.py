from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


create_petition_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                        text='Оставить обращение',
                        callback_data='petition'
            )
        ]
    ]
)

check_petition_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='✅',
                    callback_data='accept'
                ),
                InlineKeyboardButton(
                    text='❌',
                    callback_data='discard'
                )
            ]
        ]
    )
