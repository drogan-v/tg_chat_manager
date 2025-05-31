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
    await update.message.reply_html(f"{LLMClient().validate_message(update.message.text)}")
