from dotenv import load_dotenv
import os
import logging

from telegram import Update
from telegram.ext import Application
import firebase_admin
from firebase_admin import credentials

from bot import Bot
from services import LLMService, ConsoleLog, FirebaseLog


def main() -> None:
    load_dotenv()

    console_log = ConsoleLog("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_log.set_name("httpx").set_level(logging.WARNING)
    console_log.set_name(__name__)

    cred = credentials.Certificate(os.getenv("FIREBASE_DB_SECRET"))
    firebase_admin.initialize_app(cred, {"databaseURL": os.getenv("FIREBASE_DB_URL")})

    firebase_log = FirebaseLog()

    llm_service = LLMService()

    app = Application.builder().token(os.getenv("TOKEN")).build()

    bot = Bot(llm_service=llm_service, logs=firebase_log)
    for handler in bot.handlers():
        app.add_handler(handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
