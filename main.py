import asyncio
import logging

from aiogram import Bot, Dispatcher, types, html, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from datetime import datetime

from config_reader import config

from utils.keyboards import *
from utils.db import *

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

bot = Bot(token=config.bot_token.get_secret_value(), 
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
            )
        )

class Contact(StatesGroup):
    wait_for_contact = State()

@dp.message(F.text, Command('start'))
async def start(message: types.Message, state: FSMContext):
    global username
    username = message.from_user.username

    current_time = datetime.now().time()

    if (current_time >= datetime.strptime('5:00', '%H:%M').time()) and (current_time < datetime.strptime('12:00', '%H:%M').time()):
        greeting = f'Доброго ранку'
    elif (current_time >= datetime.strptime('12:00', '%H:%M').time()) and (current_time < datetime.strptime('18:00', '%H:%M').time()):
        greeting = f'Добридень'
    elif (current_time >= datetime.strptime('18:00', '%H:%M').time()) and (current_time <= datetime.strptime('23:59', '%H:%M').time()):
        greeting = f'Добрий вечір'
    elif (current_time >= datetime.strptime('00:00', '%H:%M').time()) and (current_time < datetime.strptime('05:00', '%H:%M').time()):
        greeting = f'Доброї ночі'
    else:
        greeting = f'Привіт'

    msg=f'{greeting}! Для подальшої роботи з ботом вам треба зареєструватися.\nДля реєстрації натисніть кнопку "ПОДІЛИТИСЬ"'

    await message.answer(msg, reply_markup=contact_btn())
    await state.set_state(Contact.wait_for_contact)

@dp.message(Contact.wait_for_contact)
async def contact(message: types.Message, state: FSMContext): 
    
    phone_number = message.contact.phone_number
    first_name = message.contact.first_name
    user_id = message.contact.user_id

    if first_name == None or "ᅠ":
        first_name = "Користувач"

    starts_with_plus = phone_number.startswith('+')

    if not starts_with_plus:
        phone_number = '+' + phone_number

    add_user(user_id, first_name, username, phone_number)

    msg = f"Дякуємо за реєстрацію <b>{first_name}</b>!" 
    await message.answer(msg, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

@dp.message(F.text, Command("order"))
async def order(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    add_user(user_id, username)
    username = get_name(user_id)[0][0]
    add_user(user_id, username)
    activity = is_user_active(user_id)[0][0]
    if activity == 0:
        if username:
            username = get_name(user_id)[0][0]
        else:
            username = message.from_user.first_name
        current_time = datetime.now().time()
        if (current_time >= datetime.strptime('5:00', '%H:%M').time()) and (current_time < datetime.strptime('12:00', '%H:%M').time()):
            greeting = f'Доброго ранку'
        elif (current_time >= datetime.strptime('12:00', '%H:%M').time()) and (current_time < datetime.strptime('18:00', '%H:%M').time()):
            greeting = f'Добридень'
        elif (current_time >= datetime.strptime('18:00', '%H:%M').time()) and (current_time < datetime.strptime('00:00', '%H:%M').time()):
            greeting = f'Добрий вечір'
        elif (current_time >= datetime.strptime('00:00', '%H:%M').time()) and (current_time < datetime.strptime('05:00', '%H:%M').time()):
            greeting = f'Доброї ночі'
        else:
            greeting = f'Привіт'
            
        global ask_ord
        ask_ord = f'{greeting}, <a href="tg://user?id={user_id}">{username}</a>! ☀️\nЧи бажаєте ви здійснити замовлення?'
        await message.answer(ask_ord, reply_markup=get_button())
    else:
        msg = "🛑Ви вже здійснюєте замовлення. Будь ласка, завершіть його, або використайте команду /stop, щоб скасувати поточне замовлення 🛑"
        await message.answer(msg)
        return

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())