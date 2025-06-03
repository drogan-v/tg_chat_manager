from datetime import datetime, timezone, timedelta
import re
from typing import Self
from enum import Enum
from json import dumps

from telegram import Update
from telegram.ext import ContextTypes

from services import Log
from services.log import FirebaseAction


class Additions(Enum):
    DELETE = "DELETE"
    SILENT = "SILENT"
    TIMER= "TIMER"


# TODO: ТУТ ЯВНОЕ ПОВТОРЕНИЕ КОДА. НУЖНО СДЕЛАТЬ ОБЩИЙ ИНТЕРФЕЙС КОМАНД И КОМПОЗИЦИЮ
def parse_duration(s: str):
    match = re.match(r"(\d+)([mhd])", s)
    if not match:
        raise TypeError("Invalid duration")

    value, unit = match.groups()
    value = int(value)
    if unit == "m":
        return value * 60
    elif unit == "h":
        return value * 60 * 60
    elif unit == "d":
        return value * 60 * 60 * 24
    raise TypeError("Invalid duration")


class Ban:
    def __init__(self, logs: Log) -> None:
        self.adds: set[Additions] = set()
        self.invert: bool = False
        self.logs = logs

    def with_delete(self) -> Self:
        """
        Works only in the MUTE case
        The message you replied to will be deleted.
        """
        self.adds.add(Additions.DELETE)
        return self

    def with_silent(self) -> Self:
        """
        Works only in the MUTE case
        After the user is banned, the bot will send a notification.
        """
        self.adds.add(Additions.SILENT)
        return self

    def with_timer(self) -> Self:
        """Works only in the MUTE case"""
        self.adds.add(Additions.TIMER)
        return self

    def with_invert(self) -> Self:
        """
        Now it is not MUTE, it is UNMUTE
        The Silent and Timer modes are disabled.
        """
        self.invert = not self.invert
        return self

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # TODO: Добавить причину для бана
        log = {
            "user_id": update.message.reply_to_message.from_user.id,
            "chat_id": update.effective_chat.id,
            "message": update.message.reply_to_message.text,
            "reason": "",
        }
        if not self.invert:
            await self.logs.awrite(FirebaseAction.BAN, dumps(log))
        else:
            await self.logs.awrite(FirebaseAction.UNBAN, dumps(log))

        until_date = None
        if not self.invert and Additions.TIMER in self.adds:
            try:
                duration = parse_duration(context.args[0])
                until_date = datetime.now(timezone.utc) + timedelta(seconds=duration)
            except IndexError:
                return
            except TypeError:
                return

        if self.invert:
            await context.bot.unban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=update.message.reply_to_message.from_user.id
            )
        else:
            await context.bot.ban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=update.message.reply_to_message.from_user.id,
                until_date=until_date,
                revoke_messages=True if Additions.DELETE in self.adds else False
            )

        if Additions.SILENT in self.adds:
            return

        if not self.invert:
            await context.bot.send_message(update.effective_chat.id,
                                       f"Пользователь @{update.message.reply_to_message.from_user.username} забанен!")
        else:
            await context.bot.send_message(update.effective_chat.id,
                                           f"Пользователь @{update.message.reply_to_message.from_user.username} разбанен! 🥳")
