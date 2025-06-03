from datetime import datetime, timedelta, timezone
import re

from telegram import Update, ChatPermissions
from telegram.error import TelegramError
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler, filters, MessageHandler

from services import Log
from services.log import FirebaseAction
from json import dumps


class Admin:
    def __init__(self, logs: Log) -> None:
        self.logs = logs

    def handlers(self) -> list:
        return [
            CommandHandler("ban", self.ban_user, filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("tban", self.temp_ban_user, filters=~filters.ChatType.PRIVATE & filters.COMMAND),
        ]

    # async def unban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     await context.bot.unban_chat_member(chat_id=update.effective_chat.id, user_id=7880380383, only_if_banned=True)
    #     await context.bot.send_message(chat_id=7880380383, text="Unbanned!\n https://t.me/+KpZdeUAFU-UxNjcy")

    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if the user that sent the message is an admin in the chat."""
        user_id = update.effective_user.id
        member = await update.effective_chat.get_member(user_id)
        return member.status in ['administrator', 'creator']

    async def ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.is_admin(update, context):
            await update.message.reply_text("Эта команда доступна только администраторам.")
            return
        if update.message.reply_to_message:
            if len(context.args) != 1:
                await update.message.reply_text("Формат команды: /ban <причина>\n"
                                                "Укажите пользователя для бана ответом на его сообщение.")
                return
            reason = context.args[0]
            user = update.message.reply_to_message.from_user
            log = {
                "user_id": user.id,
                "chat_id": update.effective_chat.id,
                "reason": reason,
                "message": update.message.reply_to_message.text,
            }
            await self.logs.awrite(FirebaseAction.BAN, dumps(log))
            await update.message.reply_text(f"{user.first_name} был заблокирован.\n"
                                            f"Причина: {reason}.")
            await update.effective_chat.ban_member(user.id)
            await update.message.delete()
            return
        else:  #TODO: Бан пользователя по его никнейму
            if len(context.args) != 2:
                await update.message.reply_text("Формат команды: /ban @<username> <причина>")
                return
            username, reason = context.args[0].lstrip('@'), context.args[1]
            pass

    async def temp_ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.is_admin(update, context):
            await update.message.reply_text("Эта команда доступна только администраторам.")
            return
        if update.message.reply_to_message:
            if len(context.args) != 2:
                await update.message.reply_text("Формат команды: /time_ban <время> <причина>\n"
                                                "Формат времени: <число><символ>, например: 1m, 12h, 2d,\n"
                                                "Укажите пользователя для временного бана ответом на его сообщение.")
                return
            time_duration, reason = context.args[0], context.args[1]
            user = update.message.reply_to_message.from_user
            try:
                until_date = datetime.now(timezone.utc) + timedelta(
                    seconds=self.parse_duration(time_duration)
                )
            except:
                await update.message.reply_text(f"Invalid duration format: {time_duration}")
                return
            log = {
                "user_id": user.id,
                "chat_id": update.effective_chat.id,
                "reason": reason,
                "message": update.message.reply_to_message.text,
            }
            await self.logs.awrite(FirebaseAction.BAN, dumps(log))
            await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=user.id, until_date=until_date,
                                              revoke_messages=False)
            await update.message.reply_text(f"{user.first_name} был заблокирован на {time_duration}.\n"
                                            f"Причина: {reason}.")
            await update.message.delete()
            return
        else:  #TODO: Временный бан пользователя по его никнейму
            if len(context.args) != 3:
                await update.message.reply_text("Формат команды: /ban @<username> <причина>")
                return
            username, time, reason = context.args[0].lstrip('@'), context.args[1], context.args[2]
            pass

    async def set_user_permissions(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int,
                                   permission: bool) -> None:
        """Set user permissions to be able to send messages in the chat."""
        await context.bot.restrict_chat_member(chat_id=chat_id,
                                               user_id=user_id,
                                               permissions=ChatPermissions(can_send_messages=permission,
                                                                           can_send_polls=permission,
                                                                           can_send_audios=permission,
                                                                           can_send_photos=permission,
                                                                           can_send_videos=permission,
                                                                           can_send_documents=permission,
                                                                           can_send_video_notes=permission,
                                                                           can_send_voice_notes=permission,
                                                                           can_send_other_messages=permission,
                                                                           can_pin_messages=permission, )
                                               )

    def parse_duration(self, s: str):
        match = re.match(r"(\d+)([mhd])", s)
        if not match:
            return None

        value, unit = match.groups()
        value = int(value)
        if unit == "m":
            return value * 60
        elif unit == "h":
            return value * 60 * 60
        elif unit == "d":
            return value * 60 * 60 * 24
        return None
