from dotenv import load_dotenv
import os
import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, filters, MessageHandler

from handlers import handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv()
    app = Application.builder().token(os.getenv("TOKEN")).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handlers.user_auth))
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("help", handlers.help_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.validate))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
