from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler, filters, MessageHandler

from services.llm import LLMService


class BotHandlers:
    def __init__(self, llm_service: LLMService) -> None:
        self.llm_service = llm_service

    def get_handlers(self) -> list:
        return [
            CommandHandler("help", self.help_command),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.validate)
        ]

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        await update.message.reply_text("Help!")

    async def validate(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Validate the message sent by the user."""
        status, reason = self.llm_service.validate_message(update.message.text)
        if 'unsafe' in status:
            await update.message.delete()
            await context.bot.send_message(chat_id=update.message.from_user.id, text=f'Вы были забанены за сообщение: '
                                                                                     f'{update.message.text}\nПричина: {reason}')
            try:
                await context.bot.ban_chat_member(chat_id=update.message.chat_id, user_id=update.message.from_user.id)
            except TelegramError:
                # Значит, типок является админом
                pass
