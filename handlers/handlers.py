from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler, filters, MessageHandler

from services.firebase import FirebaseService
from services.llm import LLMService
from .auth import BotAuthHandlers
from .manager import ManageHandlers


class BotHandlers:
    def __init__(self, firebase_service: FirebaseService, llm_service: LLMService) -> None:
        self.firebase_service = firebase_service
        self.llm_service = llm_service
        self.bot_auth_handlers = BotAuthHandlers(firebase_service, llm_service)
        self.manage_handlers = ManageHandlers(firebase_service)

    def get_handlers(self) -> list:
        return self.bot_auth_handlers.get_handlers() + self.manage_handlers.get_handlers() + [
            CommandHandler("help", self.help_command),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.validate)
        ]

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        await update.message.reply_text("Help!")

    async def validate(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Validate the message sent by the user."""
        status, reason = LLMClient().validate_message(update.message.text)
        if 'unsafe' in llm_response:
            self.firebase_service.ban_user(update.message.chat_id, update.message.from_user.id)
            await update.message.delete()
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text=f'/ban @{update.message.from_user.username} {reason}')
            await context.bot.send_message(chat_id=update.message.from_user.id, text=f'Вы были забанены за сообщение: '
                                                                                     f'{update.message.text}\nПричина: {reason}')
            try:
                await context.bot.ban_chat_member(chat_id=update.message.chat_id, user_id=update.message.from_user.id)
            except TelegramError:
                # Значит, типок является админом
                pass
