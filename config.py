import os
import secret

class Config:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID", secret.client_id)
        self.client_secret = os.getenv("CLIENT_SECRET", secret.client_secret)
        self.scopes = ['playlist-modify-private', 'playlist-modify-public', 'user-library-read', 'user-read-email', 'user-read-private']
        self.scope_str = ""

    def add_scope(self, scope_name):
        self.scopes.append(scope_name)
        self.scope_str = " ".join(self.scopes)

    def remove_scope(self, scope_name):
        self.scopes.remove(scope_name)
        self.scope_str = self.scope_str.replace(scope_name, "")