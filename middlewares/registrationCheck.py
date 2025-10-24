from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from aiogram.enums import ContentType
from typing import Callable, Dict, Any, Awaitable
from utils.db import is_user_in_db, get_number


class RegistrationCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            user = None
            msg = None

            if event.message:
                msg: Message = event.message
                user = msg.from_user

                # Пропускаем команды регистрации и старт
                if msg.text and msg.text.lower() in ["/start", "/register"]:
                    return await handler(event, data)

                # Если это контакт
                if msg.content_type == ContentType.CONTACT:
                    if msg.contact.user_id != user.id:
                        await msg.answer("❌ Наданий контакт не належить вам. Надішліть свій контакт за допомогою кнопки «Поділитись».")
                        return  # ждем правильный контакт
                    return await handler(event, data)

            elif event.callback_query:
                cb: CallbackQuery = event.callback_query
                user = cb.from_user

            if user:
                user_id = user.id
                if not is_user_in_db(user_id):
                    if msg:
                        await msg.answer("❌ Ви не зареєстровані в боті. Спочатку зареєструйтеся за допомогою команди /register. ❌")
                    return
                phone_number = get_number(user_id)[0][0]
                if not phone_number or phone_number.strip() == "":
                    if msg:
                        await msg.answer("❌ Ви не надали номер телефону. Використайте команду /register, щоб завершити реєстрацію. ❌")
                    return

        except Exception as e:
            print(f"Ошибка в RegistrationCheckMiddleware: {e}")

        return await handler(event, data)
