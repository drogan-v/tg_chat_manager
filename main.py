from dotenv import load_dotenv
import os
import logging

from telegram import Update
from telegram.ext import Application

from handlers.handlers import BotHandlers
from services.llm import LLMService

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv()

    llm_service = LLMService()

    app = Application.builder().token(os.getenv("TOKEN")).build()

    bot_handlers = BotHandlers(llm_service=llm_service)
    for handler in bot_handlers.get_handlers():
        app.add_handler(handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
