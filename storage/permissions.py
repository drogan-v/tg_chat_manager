from firebase_admin.exceptions import FirebaseError

from services import Firebase


class Permissions:
    def __init__(self):
        self.firebase = Firebase()

    def set_user_permissions(self, user_id: int, permissions: dict) -> None:
        """
        Mapping user to permissions.
        permissions: Serializable
        """
        try:
            ref = self.firebase.ref(f"users/{user_id}/permissions")
            ref.update(permissions)
        except FirebaseError as e:
            raise Exception(f"storage.permission: {e}")

    def user_permissions(self, user_id: int) -> dict:
        try:
            ref = self.firebase.ref(f"users/{user_id}/permissions")
            return ref.get()
        except FirebaseError as e:
            raise Exception(f"storage.permission: {e}")
