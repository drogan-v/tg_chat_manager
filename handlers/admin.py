from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler, filters, MessageHandler


class Admin:
    def __init__(self) -> None:
        pass

    def handlers(self) -> list:
        return [
            CommandHandler("ban", self.ban_user),
        ]

    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if the user that sent the message is an admin in the chat."""
        user_id = update.effective_user.id
        member = await update.effective_chat.get_member(user_id)
        return member.status in ['administrator', 'creator']

    async def ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self.is_admin(update, context):
            await update.message.reply_text("Эта команда доступна только администраторам.")
            return
        try:
            reason = context.args[0]
        except IndexError:
            await update.message.reply_text("Укажите причину бана.")
        if update.message.reply_to_message:
            user = update.message.reply_to_message.from_user
            await update.message.reply_text(f"{user.first_name} забанен по причине: {reason}.")
            await update.effective_chat.ban_member(user.id)
            return
        await update.message.reply_text("Укажите пользователя для бана ответом на его сообщение.")
