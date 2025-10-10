import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from datetime import datetime

from config_reader import config

from utils.keyboards import contact_btn, get_button, get_button_admin, unban_button
from utils.db import add_user, get_first_name, get_name, get_number, is_user_active, set_user_active, set_user_inactive, save_name, set_user_banned, set_user_unbanned, get_banned_users, get_unbanned_users
from middlewares.logs import *
from middlewares.banCheck import *
from middlewares.registrationCheck import *

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

def check_time():
    current_time = datetime.now().time()

    if (current_time >= datetime.strptime('5:00', '%H:%M').time()) and (current_time < datetime.strptime('12:00', '%H:%M').time()):
        greeting = 'Доброго ранку'
    elif (current_time >= datetime.strptime('12:00', '%H:%M').time()) and (current_time < datetime.strptime('18:00', '%H:%M').time()):
        greeting = 'Добридень'
    elif (current_time >= datetime.strptime('18:00', '%H:%M').time()) and (current_time <= datetime.strptime('23:59', '%H:%M').time()):
        greeting = 'Добрий вечір'
    elif (current_time >= datetime.strptime('00:00', '%H:%M').time()) and (current_time < datetime.strptime('05:00', '%H:%M').time()):
        greeting = 'Доброї ночі'
    else:
        greeting = 'Привіт'
        
    return greeting

@dp.message(F.text, Command('start', 'register'))
async def start(message: Message, state: FSMContext):
    global username
    username = message.from_user.username
    
    greeting = check_time()

    msg=f'{greeting}! Для подальшої роботи з ботом вам треба зареєструватися.\nДля реєстрації натисніть кнопку "ПОДІЛИТИСЬ"'

    await message.answer(msg, reply_markup=contact_btn())
    await state.set_state(Contact.wait_for_contact)

@dp.message(Contact.wait_for_contact)
async def contact(message: Message, state: FSMContext): 
    if not message.contact:
        await message.answer("Будь ласка, надішліть свій контакт натиснув на кнопку «Поділитись».")
        return

    phone_number = message.contact.phone_number
    first_name = message.contact.first_name
    user_id = message.from_user.id

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
async def order(message: Message):
    user_id = message.from_user.id

    username = get_first_name(user_id)[0][0]
    name = get_name(user_id)[0][0]

    activity = is_user_active(user_id)[0][0]

    if activity == 0:

        username = name if name else username

        greeting = check_time()

        global ask_ord
        ask_ord = f'{greeting}, <a href="tg://user?id={user_id}">{username}</a>! ☀️\nЧи бажаєте ви здійснити замовлення?'

        await message.answer(ask_ord, reply_markup=get_button())

    else:
        msg = "🛑Ви вже здійснюєте замовлення. Будь ласка, завершіть його, або використайте команду /stop, щоб скасувати поточне замовлення 🛑"
        await message.answer(msg)

@dp.message(F.text, Command("stop"))
async def stop(message: Message, state: FSMContext):
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
async def yes_btn(call: CallbackQuery, state: FSMContext):
    global user_id
    user_id = call.from_user.id
    
    activity = is_user_active(user_id)[0][0]

    if activity == 0:
        set_user_active(user_id)

        await call.message.edit_text(text=ask_ord, reply_markup=None)

        check_name = get_name(user_id)[0][0]

        if check_name:
            msg = "Введіть ваше замовлення! ✉️"

            await state.set_state(Waits.wait_for_order)
            await call.message.answer(msg)
        else:
            msg = "Чудово! Напишіть, будь ласка, ваше ім'я! 👤"

            await call.message.answer(msg)
            await state.set_state(Waits.wait_for_name)


@dp.message(Waits.wait_for_name)
async def name(message: Message, state: FSMContext): 
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
async def send_order(message: Message, state: FSMContext): 
    global admin_id 
    admin_id = 1071185904
    user_name = get_name(user_id)[0][0]
    phone_number = get_number(user_id)[0][0]
    if name == '/stop':
        await stop(message)
        return
    else:
        order = message.text
        msg = "Ваше замовлення було надіслано. Зараз воно проходить перевірку. Очікуйте, будь ласка! ✅"
        global to_admin
        to_admin = f"❗️Нове замовлення!❗️\n\n👤 Ім'я: <a href='tg://user?id={user_id}'>{user_name}</a> 👤\n🔒 ID: <code>{user_id}</code> 🔒\n📱 Номер телефону: {phone_number} 📱\n\n✉️ Замовлення: {order} ✉️"
        set_user_inactive(user_id)
        await bot.send_message(user_id, msg)
        await bot.send_message(admin_id, to_admin, reply_markup=get_button_admin())
        await state.clear()


@dp.callback_query(F.data == 'NoBtn')
async def no_btn(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    username = get_first_name(user_id)[0][0]
    name = get_name(user_id)[0][0]

    username = name if name else username

    greeting = check_time()

    msg = f'{greeting}, <a href="tg://user?id={user_id}">{username}</a>! ☀️\nЧи бажаєте ви здійснити замовлення?'
    set_user_inactive(user_id)

    await call.message.edit_text(text=msg, reply_markup=None)

    msg = "Добре! Буду на вас чекати, якщо захочете здійснити замовлення! ✅"
    await call.message.answer(msg)


# ===================================================================================================
# ================================ Accept & decline btn handlers ====================================
# ===================================================================================================


@dp.callback_query(F.data == "Accept")
async def accept(call: CallbackQuery):
    set_user_inactive(user_id)
    approved = "\n\n ✅✅✅ Прийнято ✅✅✅"
    await call.message.edit_text(text=to_admin+approved, reply_markup=None)
    msg = "✅ Ваше замовлення було прийнято. Очікувайти поки з вами зв'яжуться. Я завжди тут, якщо ви забажаєте здійснити нове замовлення! ✅"
    await call.bot.send_message(user_id, msg)


@dp.callback_query(F.data == "Decline")
async def accept(call: CallbackQuery, state: FSMContext):
    set_user_inactive(user_id)
    msg = "Вкажіть причину:"
    declined = "\n\n ❌❌❌ Відмовлено ❌❌❌"
    await call.message.edit_text(text=to_admin+declined, reply_markup=None)
    await bot.send_message(admin_id, msg)
    await state.set_state(Waits.wait_for_reason)


@dp.message(Waits.wait_for_reason)
async def order(message: Message, state: FSMContext): 
    reason = message.text
    if reason.lower() == "без":
        msg = "❌❌❌ На жаль, вам було відмовлено. Гарного дня! ❌❌❌"
    else:
        msg = f"❌❌❌ На жаль, вам було відмовлено за насутпною причиною: <b>{reason}.</b> Гарного дня! ❌❌❌"
    await bot.send_message(user_id, msg, reply_markup=None)
    await state.clear()


# ===================================================================================================
# ========================================== Ban handler ============================================
# ===================================================================================================

@dp.callback_query(F.from_user.id == 1071185904, F.data == "Ban")
async def accept(call: CallbackQuery):
    set_user_banned(user_id)
    await call.message.edit_text(f"🚫 Користувач з user_id <code>{user_id}</code> був заблокований 🚫", reply_markup=unban_button())


@dp.callback_query(F.from_user.id == 1071185904, F.data == "Unban")
async def accept(call: CallbackQuery):
    set_user_unbanned(user_id)
    await call.message.edit_text(f"✅<a href='tg://user?id={user_id}'><b> Користувач 👤</b></a> був успішно разблокован! ✅ \nuser_id - <code>{user_id}</code>", reply_markup=None)


@dp.message(F.from_user.id == 1071185904, Command("ban"))
async def ban(message: Message, command: CommandObject):
    if command.args:
        user_id = command.args
        if not user_id.isdigit():
            msg = "❌ Неправильний формат користувача! Введіть коректний user_id ❌"
        else:
            if (len(user_id) < 9 or len(user_id) > 10):
                msg = "❌ Неправильна довжина user_id! Введіть коректний user_id ❌"
            else:
                set_user_banned(user_id)
                msg = f"<a href='tg://user?id={user_id}'><b> Користувач 👤</b></a> був успішно заблокован! ✅"
    else:   
        msg = "Не вказано значення після команди /ban"
    await message.answer(msg)


@dp.message(F.from_user.id == 1071185904, Command("unban"))
async def unban(message: Message, command: CommandObject):
    if command.args:
        user_id = command.args
        if not user_id.isdigit():
            msg = "❌ Неправильний формат користувача! Введіть коректний user_id ❌"
        else:
            if (len(user_id) < 9 or len(user_id) > 10):
                msg = "❌ Неправильна довжина user_id! Введіть коректний user_id ❌"
            else:
                user_id = int(user_id)
                set_user_unbanned(user_id)
                msg = f"<a href='tg://user?id={user_id}'><b>Користувач 👤</b></a> був разблокован! ✅"
        await message.answer(msg)
        return
    else:
        msg = "Не вказано значення після команди /unban"
    await message.answer(msg)

@dp.message(F.from_user.id == 1071185904, F.text.lower() == "банлист")
@dp.message(F.from_user.id == 1071185904,  Command("banlist"))
async def banlist(message: Message):

    banned_users = get_banned_users()
    
    if banned_users:
        msg = "Список забанених користувачів:\n"
        for idx, user in enumerate(banned_users, start=1):
            user_id = user[0]
            username = user[1]
            msg += f"<b>{idx}. 👤 <a href='tg://user?id={user_id}'>{username}</a> 👤</b>\n    🔒 ID: <code>{user_id}</code>🔒\n\n"
    else:
        msg = "На даний момент немає заблокованих користувачів."
    await message.answer(msg)

class BroadcastState(StatesGroup):
    waiting_for_content = State()

@dp.message(F.from_user.id == 1071185904, Command("bc"))
async def cmd_broadcast(message: Message, state: FSMContext):
    await message.answer(
        "📨 Отправьте сообщение для рассылки:\n"
        "⚠️ Можно текст, фото, видео или любой другой медиа-контент"
    )
    await state.set_state(BroadcastState.waiting_for_content)

@dp.message(BroadcastState.waiting_for_content)
async def process_broadcast_content(message: Message, state: FSMContext):
    users = get_unbanned_users()
    total = len(users)
    success = 0
    blocked = 0
    
    await message.answer(f"🚀 Начата рассылка для {total} пользователей...")

    for user_id in users:
        try:
            await message.send_copy(chat_id=user_id)
            success += 1
        except Exception:
            blocked += 1
        
        await asyncio.sleep(0.05)

    report = (
        "📊 Рассылка завершена!\n"
        f"✅ Успешно: {success}\n"
        f"❌ Заблокировали бота: {blocked}\n"
        f"📩 Всего получателей: {total}"
    )
    
    await message.answer(report)
    await state.clear()



class Update(StatesGroup):
    waiting_for_update_content = State()

@dp.message(F.from_user.id == 1071185904, Command("upd"))
async def cmd_update_broadcast(message: Message, state: FSMContext):
    await message.answer(
        "🆕 Введите описание обновления, которое будет разослано пользователям:"
    )
    await state.set_state(Update.waiting_for_update_content)

@dp.message(Update.waiting_for_update_content)
async def process_update_content(message: Message, state: FSMContext):
    users = get_unbanned_users()
    total = len(users)
    success = 0
    blocked = 0
    update_text = (f"🔔 *Новое обновление!* 🔔\n\n {message.text}\n\n🔥 Спасибо, что остаётесь с нами!")

    await message.answer(f"🚀 Начата рассылка для {total} пользователей...")

    for user_id in users:
        try:
            await message.bot.send_message(chat_id=user_id, text=update_text, parse_mode="Markdown")
            success += 1
        except Exception:
            blocked += 1
        await asyncio.sleep(0.05)

    report = (
        "📊 Рассылка завершена!\n"
        f"✅ Успешно: {success}\n"
        f"❌ Заблокировали бота: {blocked}\n"
        f"📩 Всего получателей: {total}"
    )
    
    await message.answer(report)
    await state.clear()

async def main():
    dp.update.outer_middleware.register(LoggerMiddleware(bot))
    dp.update.outer_middleware.register(BanCheckMiddleware())
    dp.update.outer_middleware.register(RegistrationCheckMiddleware())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 