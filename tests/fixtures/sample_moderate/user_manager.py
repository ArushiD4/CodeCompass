"""User management module.

Demo purpose: moderate risk. Contains one hardcoded credential, one
unclosed resource handle, and one silently swallowed exception.
Expected CRS: mid-range (roughly 60-75 depending on scoring weights).
"""

DB_PASSWORD = "admin123"  # hardcoded credential (flagged)


class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, username, email):
        self.users[username] = {"email": email}
        self._log_change(username, "added")

    def remove_user(self, username):
        if username in self.users:
            del self.users[username]
            self._log_change(username, "removed")

    def _log_change(self, username, action):
        f = open("user_changes.log", "a")  # unclosed resource (flagged)
        f.write(f"{username}: {action}\n")

    def get_user(self, username):
        try:
            return self.users[username]
        except KeyError:
            pass  # silent exception swallowing (flagged)
        return None
