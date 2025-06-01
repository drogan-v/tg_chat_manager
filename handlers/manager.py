from telegram import Update
from telegram.ext import ContextTypes

from telegram.ext import CommandHandler, filters

from services.firebase import FirebaseService


class ManageHandlers:
    def __init__(self, firebase_service: FirebaseService):
        self.firebase_service = firebase_service

    def get_handlers(self):
        return [
            CommandHandler("ban", self.ban_user, filters=~filters.ChatType.PRIVATE),
        ]

    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if the user that sent the message is an admin in the chat."""
        user_id = update.effective_user.id
        member = await update.effective_chat.get_member(user_id)
        return member.status in ['administrator', 'creator']

    async def ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Bans a user from the chat by username."""
        if not await self.is_admin(update, context):
            await update.message.reply_text("Эта команда доступна только администраторам.")
            return

        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Использование: /ban <@username> причина")
        username, reason = args[0].lstrip('@'), args[1]

        try:
            member = self.firebase_service.get_user_by_username(username)
            user_id = member['user_id']
        except Exception as e:
            await update.message.reply_text("Пользователь не найден.")

        self.firebase_service.ban_user(update.message.chat_id, user_id)
        await context.bot.ban_chat_member(chat_id=update.message.chat_id, user_id=user_id)
