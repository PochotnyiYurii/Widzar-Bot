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


def get_button():
    buttons = [
        [
            types.InlineKeyboardButton(text="Так ✅", callback_data="YesBtn"),
            types.InlineKeyboardButton(text="Ні ❌", callback_data="NoBtn")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_button_admin():
    buttons = [
        [
            types.InlineKeyboardButton(text="Прийняти ✅", callback_data="Accept"),
            types.InlineKeyboardButton(text="Відмовити ❌", callback_data="Cancel"),
        ],
        [
            types.InlineKeyboardButton(text="БАН 🚫", callback_data="Ban")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
