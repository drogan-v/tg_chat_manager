from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

from telegram.ext import CommandHandler, filters, MessageHandler

from services.firebase import FirebaseService
from services.llm import LLMService

class BotAuthHandlers:
    def __init__(self, firebase_service: FirebaseService, llm_service: LLMService):
        self.firebase_service = firebase_service
        self.llm_service = llm_service

    def get_handlers(self) -> list:
        return [
            MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.user_entered_group),
            MessageHandler(filters.ChatType.PRIVATE, self.verify_user),
        ]

    async def user_entered_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Authorize user that entered the group"""
        for member in update.message.new_chat_members:
            user_id = member.id
            chat_id = update.message.chat.id
            if not self.firebase_service.has_user_verified(user_id):
                self.firebase_service.mark_chat_as_unavailable(chat_id, user_id)
                await self.set_user_permissions(context, chat_id, user_id, False)
                await context.bot.send_message(chat_id=update.message.chat_id,
                                               text=(
                                                   f"Привет, @{member.username}, чтобы писать в группу, "
                                                   f"<a href='https://t.me/tmp_tg_chat_manager_bot?start=access'>нажми сюда</a>."
                                               ), parse_mode="HTML")

    async def verify_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user:
            return

        user_id = user.id

        self.firebase_service.mark_user_as_verified(user_id)
        chats = self.firebase_service.get_unavailable_chat(user_id)
        for chat_id in chats.values():
            await self.set_user_permissions(context, chat_id, user_id, True)
        self.firebase_service.mark_chat_as_available(user_id)
        await update.message.reply_text(
            "Спасибо, что написали мне! Теперь вы можете писать в группе."
        )

    async def set_user_permissions(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int,
                                   permission: bool) -> None:
        """Set user permissions to be able to send messages in the chat."""
        await context.bot.restrict_chat_member(chat_id=chat_id,
                                               user_id=user_id,
                                               permissions=ChatPermissions(can_send_messages=permission,
                                                                           can_send_polls=permission,
                                                                           can_send_audios=permission,
                                                                           can_send_photos=permission,
                                                                           can_send_videos=permission,
                                                                           can_send_documents=permission,
                                                                           can_send_video_notes=permission,
                                                                           can_send_voice_notes=permission,
                                                                           can_send_other_messages=permission,
                                                                           can_pin_messages=permission,)
                                               )