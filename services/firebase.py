from firebase_admin.db import reference, Reference


class Firebase:
    def ref(self, path='/', app=None, url=None) -> Reference:
        """alias for firebase_admin.db.reference"""
        return reference(path, app, url)