from aiogram import BaseMiddleware, html
from aiogram.types import Update, Message, CallbackQuery
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramMigrateToChat
from typing import Callable, Dict, Any, Awaitable
from utils.logger_config import logger

LOG_CHAT_ID = -4960605494

class LoggerMiddleware(BaseMiddleware):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        content_type = "unknown"
        content_info = ""
        action = "совершил действие"

        try:
            if event.message:
                msg: Message = event.message
                
                if msg.content_type == ContentType.PINNED_MESSAGE:
                    return await handler(event, data)

                user = msg.from_user
                content_type = msg.content_type
                action = "отправил сообщение"

                match content_type:
                    case ContentType.TEXT:
                        content_info = f"Сообщение: {html.quote(msg.text)}"
                    case ContentType.PHOTO:
                        content_info = f"Фото (ID: {msg.photo[-1].file_id})"
                    case ContentType.VIDEO:
                        content_info = f"Видео (ID: {msg.video.file_id})"
                    case ContentType.DOCUMENT:
                        content_info = f"Документ: {msg.document.file_name} (ID: {msg.document.file_id})"
                    case ContentType.AUDIO:
                        content_info = f"Аудио (ID: {msg.audio.file_id})"
                    case ContentType.VOICE:
                        content_info = f"Голосовое сообщение (ID: {msg.voice.file_id})"
                    case ContentType.STICKER:
                        content_info = f"Стикер (ID: {msg.sticker.file_id})"
                    case ContentType.LOCATION:
                        loc = msg.location
                        content_info = f"Локация: {loc.latitude},{loc.longitude}"
                    case ContentType.CONTACT:
                        content_info = f"Контакт: {msg.contact.phone_number}"
                    case _:
                        content_info = "Неизвестный тип контента"

            elif event.callback_query:
                cb: CallbackQuery = event.callback_query
                user = cb.from_user
                content_type = "callback"
                content_info = f"Данные callback: {html.quote(cb.data)}"
                action = "нажал на кнопку"

            if user:
                username = f"@{user.username}" if user.username else "нет юзернейма"
                log_message = (
                    f"👤 Пользователь: <a href='tg://user?id={user.id}'>{user.full_name}</a>\n"
                    f"🆔 ID: <code>{user.id}</code>\n"
                    f"📛 Юзернейм: {username}\n"
                    f"📝 Тип контента: {content_type}\n"
                    f"📄 Действие: {action}\n"
                    f"ℹ️ Детали: {content_info}"
                )

                global LOG_CHAT_ID
                try:
                    await self.bot.send_message(LOG_CHAT_ID, log_message)

                    if event.message:
                        await self.bot.forward_message(
                            chat_id=LOG_CHAT_ID,
                            from_chat_id=event.message.chat.id,
                            message_id=event.message.message_id
                        )
                except TelegramMigrateToChat as e:
                    LOG_CHAT_ID = e.migrate_to_chat_id
                    await self.bot.send_message(LOG_CHAT_ID, log_message)
                except Exception as e:
                    logger.error(f"Ошибка логирования: {e}")

        except Exception as e:
            logger.exception(f"Ошибка в LoggerMiddleware: {e}")

        return await handler(event, data)