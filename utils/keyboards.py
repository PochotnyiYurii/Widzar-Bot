from aiogram import types

def contact_btn():
    buttons = [
        [
            types.KeyboardButton(text="ПОДІЛИТИСЬ", request_contact=True),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True
)
    return keyboard