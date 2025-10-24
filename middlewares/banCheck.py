from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from utils.db import is_user_banned


class BanCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            user = None

            if event.message:
                msg: Message = event.message
                user = msg.from_user

            elif event.callback_query:
                cb: CallbackQuery = event.callback_query
                user = cb.from_user

            if user:
                user_id = user.id
                banned = is_user_banned(user_id)
                if banned and banned[0][0]:
                    return

        except Exception as e:
            print(f"Ошибка в BanCheckMiddleware: {e}")

        return await handler(event, data)
