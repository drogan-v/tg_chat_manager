from telegram import ForceReply, Update
from telegram.ext import ContextTypes
from services.llm import LLMClient


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Validate the message sent by the user."""
    llm_response = LLMClient().validate_message(update.message.text)
    print(llm_response.split())
    status, reason = llm_response.split()
    if 'unsafe' in llm_response:
        await update.message.delete()
        await context.bot.ban_chat_member(chat_id=update.message.chat_id, user_id=update.message.from_user.id)
        await context.bot.send_message(chat_id=update.message.from_user.id, text=f'Вы были забанены за сообщение: '
                                                                                 f'{update.message.text}. Причина: {reason}')
