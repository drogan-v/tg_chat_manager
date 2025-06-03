from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler, filters

from services import Log
from comands import Mute, Ban, Kick


class Admin:
    def __init__(self, logs: Log) -> None:
        self.logs = logs

    def handlers(self) -> list:
        return [
            CommandHandler("kick", Kick(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("dkick", Kick().with_delete(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("skick", Kick().with_silent(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("sdkick", Kick().with_silent().with_delete(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),

            CommandHandler("ban", Ban(self.logs), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("dban", Ban(self.logs).with_delete(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("sban", Ban(self.logs).with_silent(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("sdban", Ban(self.logs).with_delete().with_silent(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("tban", Ban(self.logs).with_timer(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("tdban", Ban(self.logs).with_timer().with_delete(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("tsdban", Ban(self.logs).with_timer().with_delete().with_silent(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("unban", Ban(self.logs).with_invert(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),

            CommandHandler("mute", Mute(self.logs), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("dmute", Mute(self.logs).with_delete(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("smute", Mute(self.logs).with_silent(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("sdmute", Mute(self.logs).with_delete().with_silent(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("tmute", Mute(self.logs).with_timer(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("tdmute", Mute(self.logs).with_timer().with_delete(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("tsdmute", Mute(self.logs).with_timer().with_delete().with_silent(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("unmute", Mute(self.logs).with_invert(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
        ]

    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if the user that sent the message is an admin in the chat."""
        user_id = update.effective_user.id
        member = await update.effective_chat.get_member(user_id)
        return member.status in ['administrator', 'creator']

