from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler, filters

from services import ConsoleLog, FirebaseLog
from comands import Mute, Ban, Kick


class Admin:
    def __init__(self, firebase_log: FirebaseLog, console_log: ConsoleLog) -> None:
        self.firebase_logs = firebase_log
        self.console_logs = console_log.set_name(__name__)
        self.command_filter = ~filters.ChatType.PRIVATE & filters.COMMAND
        self.kick = Kick(console_log=self.console_logs)
        self.ban = Ban(firebase_log=self.firebase_logs, console_log=self.console_logs)
        self.mute = Mute(firebase_log=self.firebase_logs, console_log=self.console_logs)

    def handlers(self) -> list:
        return [
            CommandHandler("kick", self.kick, filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("dkick", self.kick.with_delete(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("skick", self.kick.with_silent(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),
            CommandHandler("sdkick", self.kick.with_silent().with_delete(), filters=~filters.ChatType.PRIVATE & filters.COMMAND),

            CommandHandler("ban", self.ban, filters=self.command_filter),
            CommandHandler("dban", self.ban.with_delete(), filters=self.command_filter),
            CommandHandler("sban", self.ban.with_silent(), filters=self.command_filter),
            CommandHandler("sdban", self.ban.with_delete().with_silent(), filters=self.command_filter),
            CommandHandler("tban", self.ban.with_timer(), filters=self.command_filter),
            CommandHandler("tdban", self.ban.with_timer().with_delete(), filters=self.command_filter),
            CommandHandler("tsdban", self.ban.with_timer().with_delete().with_silent(), filters=self.command_filter),
            CommandHandler("unban", self.ban.with_invert(), filters=self.command_filter),

            CommandHandler("mute", self.mute, filters=self.command_filter),
            CommandHandler("dmute", self.mute.with_delete(), filters=self.command_filter),
            CommandHandler("smute", self.mute.with_silent(), filters=self.command_filter),
            CommandHandler("sdmute", self.mute.with_delete().with_silent(), filters=self.command_filter),
            CommandHandler("tmute", self.mute.with_timer(), filters=self.command_filter),
            CommandHandler("tdmute", self.mute.with_timer().with_delete(), filters=self.command_filter),
            CommandHandler("tsdmute", self.mute.with_timer().with_delete().with_silent(), filters=self.command_filter),
            CommandHandler("unmute", self.mute.with_invert(), filters=self.command_filter),
        ]

    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if the user that sent the message is an admin in the chat."""
        user_id = update.effective_user.id
        member = await update.effective_chat.get_member(user_id)
        return member.status in ['administrator', 'creator']

