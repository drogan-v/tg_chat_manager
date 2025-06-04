from datetime import datetime, timezone, timedelta
import re
from typing import Self, Optional
from enum import Enum
from json import dumps

from telegram import Update, ChatPermissions, ChatMember, ChatMemberRestricted
from telegram.ext import ContextTypes

from services import Log
from services.log import FirebaseAction
from storage import Permissions


class Additions(Enum):
    DELETE = "DELETE"
    SILENT = "SILENT"
    TIMER = "TIMER"


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


class Mute:
    def __init__(self, logs: Log) -> None:
        self.adds: set[Additions] = set()
        self.invert: bool = False
        self.logs = logs
        self.permissions: Permissions = Permissions()

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

    def chat_permissions(self, user: ChatMember) -> ChatPermissions:
        if isinstance(user, ChatMemberRestricted):
            data = user.to_dict()
            return ChatPermissions(
                can_send_messages = data["can_send_messages"],
                can_send_polls = data["can_send_polls"],
                can_send_other_messages = data["can_send_other_messages"],
                can_add_web_page_previews = data["can_add_web_page_previews"],
                can_change_info = data["can_change_info"],
                can_invite_users = data["can_invite_users"],
                can_pin_messages = data["can_pin_messages"],
                can_manage_topics = data["can_manage_topics"],
                can_send_audios = data["can_send_audios"],
                can_send_documents = data["can_send_documents"],
                can_send_photos = data["can_send_photos"],
                can_send_videos = data["can_send_videos"],
                can_send_video_notes = data["can_send_video_notes"],
                can_send_voice_notes = data["can_send_voice_notes"],
            )
        return ChatPermissions.all_permissions()

    def is_muted(self, permissions: ChatPermissions) -> bool:
        return permissions == ChatPermissions.no_permissions()

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        user = update.message.reply_to_message.from_user
        message = update.message.reply_to_message

        until_date = None
        if not self.invert and Additions.TIMER in self.adds:
            try:
                duration = parse_duration(context.args[0])
                until_date = datetime.now(timezone.utc) + timedelta(seconds=duration)
            except IndexError:
                return
            except TypeError:
                return

        member = await context.bot.get_chat_member(chat.id, user.id)
        if not self.invert and not self.is_muted(self.chat_permissions(member)):
            self.permissions.set_user_permissions(user.id, self.chat_permissions(member).to_dict())
            permissions = ChatPermissions.no_permissions()
        elif not self.invert:
            return
        if self.invert and self.is_muted(self.chat_permissions(member)):
            try:
                permissions = ChatPermissions.de_json(self.permissions.user_permissions(user.id))
            except Exception as e:
                print(e)
                permissions = ChatPermissions.all_permissions()
        elif self.invert:
            return


        # TODO: Нужно давать юзеру не все права, а только те, которые у него были
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=update.message.reply_to_message.from_user.id,
            permissions=permissions,
            until_date=until_date if not self.invert else None,
        )

        if not self.invert and Additions.DELETE in self.adds:
            await update.message.reply_to_message.delete()

        if Additions.SILENT in self.adds:
            return

        if not self.invert:
            await context.bot.send_message(update.effective_chat.id,
                                           f"Пользователь @{update.message.reply_to_message.from_user.username} в мьюте 🤫")
        else:
            await context.bot.send_message(update.effective_chat.id,
                                           f"Пользователь @{update.message.reply_to_message.from_user.username} разговаривает! 🥳")

        # TODO: Добавить причину для мьюта
        log = {
            "user_id": user.id,
            "chat_id": chat.id,
            "message": message.text,
            "reason": "",
        }
        if not self.invert:
            await self.logs.awrite(FirebaseAction.MUTE, dumps(log))
        else:
            await self.logs.awrite(FirebaseAction.UNMUTE, dumps(log))
