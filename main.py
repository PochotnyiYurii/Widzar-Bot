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

    if (first_name == None) or (first_name == "ᅠ"):
        first_name = "Користувач"

    starts_with_plus = phone_number.startswith('+')

    if not starts_with_plus:
        phone_number = '+' + phone_number

    add_user(user_id, first_name, username, phone_number)

    first_name = get_first_name(user_id)[0][0]

    msg = f"Дякуємо за реєстрацію <b>{first_name}</b>!" 
    await message.answer(msg, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

@dp.message(F.text, Command("order"))
async def order(message: types.Message):
    user_id = message.from_user.id
    username = get_first_name(user_id)[0][0]
    name = get_name(user_id)[0][0]

    activity = is_user_active(user_id)[0][0]

    if activity == 0:
        if name:
            username = name
        else:
            username = username

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
            
        global ask_ord
        ask_ord = f'{greeting}, <a href="tg://user?id={user_id}">{username}</a>! ☀️\nЧи бажаєте ви здійснити замовлення?'

        await message.answer(ask_ord, reply_markup=get_button())
    else:
        msg = "🛑Ви вже здійснюєте замовлення. Будь ласка, завершіть його, або використайте команду /stop, щоб скасувати поточне замовлення 🛑"
        await message.answer(msg)
        return

@dp.message(F.text, Command("stop"))
async def stop(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    activity = is_user_active(user_id)[0][0]
    if activity == 1:
        set_user_inactive(user_id)
        msg = "✅ Ваше замовлення було скасовано. Я завжди тут, якщо ви забажаєте здійснити нове замовлення! ✅"
        await state.clear()
    else:
        msg = "❌ У вас немає активного замовлення, щоб його скасувати ❌"
    await message.answer(msg)

# ===================================================================================================
# ====================================== Yes & No btn handlers ======================================
# ===================================================================================================

class Waits(StatesGroup):
    wait_for_name = State()
    wait_for_order = State()
    wait_for_reason = State()

@dp.callback_query(F.data == "YesBtn")
async def YesBtn(call: types.CallbackQuery, state: FSMContext):
    global user_id
    user_id = call.from_user.id
    activity = is_user_active(user_id)[0][0]
    if activity == 0:
        set_user_active(user_id)
        await call.message.edit_text(text=ask_ord, reply_markup=None)
        check_name = get_name(user_id)[0][0]
        if check_name:
            msg = f"Введіть ваше замовлення! ✉️"
            await state.set_state(Waits.wait_for_order)
            await call.message.answer(msg)
        else:
            msg = "Чудово! Напишіть, будь ласка, ваше ім'я! 👤"
            await call.message.answer(msg)
            await state.set_state(Waits.wait_for_name)

@dp.message(Waits.wait_for_name)
async def name(message: types.Message, state: FSMContext): 
    name = message.text
    user_id = message.from_user.id
    if name == '/stop':
        await stop(message)
        return
    else:
        save_name(name, user_id)
        msg = "Добре, тепер введіть ваше замовлення! ✉️"
        await message.answer(msg)
        await state.set_state(Waits.wait_for_order)


@dp.message(Waits.wait_for_order)
async def send_order(message: types.Message, state: FSMContext): 
    global admin_id 
    admin_id = 1071185904
    user_name = get_name(user_id)[0][0]
    if name == '/stop':
        await stop(message)
        return
    else:
        order = message.text
        msg = "Ваше замовлення було надіслано. Зараз воно проходить перевірку. Очікуйте, будь ласка! ✅"
        global to_admin
        to_admin = f"❗️Нове замовлення!❗️\n\n👤 Ім'я: <a href='tg://user?id={user_id}'>{user_name}</a> 👤\n🔒 ID: <code>{user_id}</code> 🔒\n\n✉️ Замовлення: {order} ✉️"
        set_user_inactive(user_id)
        await bot.send_message(user_id, msg)
        await bot.send_message(admin_id, to_admin, reply_markup=get_button_admin())
        await state.clear()

@dp.callback_query(F.data == 'NoBtn')
async def NoBtn(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    username = call.from_user.username
    if username:
        username = get_name(user_id)[0][0]

    else:
        username = call.from_user.first_name

    msg = f'Привіт <a href="tg://user?id={user_id}">{username}</a>! ☀️\nЧи бажаєте ви здійснити замовлення?'
    set_user_inactive(user_id)

    await call.message.edit_text(text=msg, reply_markup=None)

    msg = "Добре! Буду на вас чекати, якщо захочете здійснити замовлення! ✅"
    await call.message.answer(msg)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())