import os
import secret

class Config:
    def __init__(self):
        self.client_id = os.getenv("SPOTIPY_CLIENT_ID", secret.client_id)
        self.client_secret = os.getenv("SPOTIPY_CLIENT_SECRET", secret.client_secret)
        self._scopes = ['playlist-modify-private', 'playlist-modify-public', 'user-library-read', 'user-read-email', 'user-read-private']
        self._scope_str = " ".join(self._scopes)
        self.redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "localhost:65355")

    def add_scope(self, scope_name):
        self._scopes.append(scope_name)
        self._scope_str = " ".join(self._scopes)

    def remove_scope(self, scope_name):
        self._scopes.remove(scope_name)
        self._scope_str = self._scope_str.replace(scope_name, "")

    def get_scopes(self):
        return self._scopes

    @property
    def redirect_uri(self):
        return self.redirect_uri
    
    @redirect_uri.setter
    def redirect_uri(self, uri):
        self.redirect_uri = uri

    @property
    def client_id(self):
        return self._client_id
    
    @client_id.setter
    def client_id(self, id):
        self._client_id = id

    @property
    def client_secret(self):
        return self._client_secret
    
    @client_secret.setter
    def client_secret(self, secret):
        self._client_secret = secret