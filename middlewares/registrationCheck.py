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
            user, msg = self._extract_user_and_message(event)
            if not user:
                return await handler(event, data)

            if await self._is_registration_command(msg):
                return await handler(event, data)

            if await self._handle_contact(msg, user):
                return

            if not await self._is_user_registered(msg, user.id):
                return

            if not await self._has_phone_number(msg, user.id):
                return

        except Exception as e:
            print(f"Ошибка в RegistrationCheckMiddleware: {e}")

        return await handler(event, data)

    def _extract_user_and_message(self, event: Update):
        if event.message:
            return event.message.from_user, event.message
        if event.callback_query:
            return event.callback_query.from_user, None
        return None, None

    async def _is_registration_command(self, msg: Message | None) -> bool:
        if not msg or not msg.text:
            return False
        return msg.text.lower() in ("/start", "/register")

    async def _handle_contact(self, msg: Message | None, user) -> bool:
        if not msg or msg.content_type != ContentType.CONTACT:
            return False
        if msg.contact.user_id != user.id:
            await msg.answer(
                "❌ Наданий контакт не належить вам. "
                "Надішліть свій контакт за допомогою кнопки «Поділитись»."
            )
            return True
        return False

    async def _is_user_registered(self, msg: Message | None, user_id: int) -> bool:
        if is_user_in_db(user_id):
            return True
        if msg:
            await msg.answer(
                "❌ Ви не зареєстровані в боті. "
                "Спочатку зареєструйтеся за допомогою команди /register. ❌"
            )
        return False

    async def _has_phone_number(self, msg: Message | None, user_id: int) -> bool:
        phone_number = get_number(user_id)[0][0]
        if phone_number and phone_number.strip():
            return True
        if msg:
            await msg.answer(
                "❌ Ви не надали номер телефону. "
                "Використайте команду /register, щоб завершити реєстрацію. ❌"
            )
        return False
