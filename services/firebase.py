import firebase_admin
from firebase_admin import credentials, db
import logging

logger = logging.getLogger(__name__)


class FirebaseService():
    def __init__(self, service_account_path: str, db_url: str) -> None:
        self.service_account_path = service_account_path
        self.db_url = db_url

    def initialize(self):
        """Initializes the Firebase Admin SDK."""
        try:
            cred = credentials.Certificate(self.service_account_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': self.db_url
            })
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise

    def mark_user_as_verified(self, user_id: int):
        """Marks a user as verified in the Firebase database."""
        try:
            ref = db.reference(f'users/{user_id}')
            ref.set({'verified': True})
        except Exception as e:
            logger.error(f"Firebase error in mark_user_messaged: {e}")

    def has_user_verified(self, user_id: int):
        """Checks if a user has been verified in the Firebase database."""
        try:
            ref = db.reference(f'users/{user_id}')
            user_data = ref.get()
            return user_data is not None
        except Exception as e:
            logger.error(f"Firebase error in has_user_verified: {e}")
            return False

    def mark_chat_as_unavailable(self, chat_id: int, user_id: int):
        """Marks a chat as unavailable for a user in the Firebase database."""
        try:
            ref = db.reference(f'users_unavailable_chats/{user_id}')
            ref.set({f'{chat_id}': chat_id})
        except Exception as e:
            logger.error(f"Firebase error in mark_chat_as_unavailable: {e}")

    def get_unavailable_chat(self, user_id: int):
        """Gets the unavailable chat for a user from the Firebase database."""
        try:
            ref = db.reference(f'users_unavailable_chats/{user_id}')
            data = ref.get()
            return data
        except Exception as e:
            logger.error(f"Firebase error in get_unavailable_chat: {e}")

    def mark_chat_as_available(self, user_id: int):
        """Marks all chats as available for a user in the Firebase database."""
        try:
            ref = db.reference(f'users_unavailable_chats/{user_id}')
            ref.delete()
        except Exception as e:
            logger.error(f"Firebase error in mark_chat_as_available: {e}")