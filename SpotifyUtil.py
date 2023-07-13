from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from config import Config
import logging


log = logging.getLogger(__name__)


class SpotifyClient(Config):
    def __init__(self):
        super().__init__()
        self._client_creds = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        self.spotify = Spotify(client_credentials_manager=self._client_creds)
        # self.auth_manager = SpotifyOAuth(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        # self.spotify2 = Spotify(auth_manager=self.auth_creds)
        # access_token = self.auth_manager.get_access_token(as_dict=False)
        # log.info(access_token)
        # self.spotify = Spotify(auth=access_token)
        self.user = self.spotify.current_user()
        self.user_id = self.user['id']
        log.info(msg=self.user_id)

    def get_id(self, url:str, type="track"):
        return url.split(type+"/")[1].split('?')[0]

    def create_uri(self, url:str, type="track"):
        id = self.get_id(url=url, type=type)
        return f'spotify:{type}:{id}'
    
    def create_tracks_uri_list(self, url:str, type="playlist"):
        uri = self.create_uri(url=url, type=type)
        items = None
        if type=="playlist":
            items = self.spotify.playlist(uri)
        else:
            items = self.spotify.album(uri)
        return [track['track']['uri'] for track in items['tracks']['items']]
    
    def create_playlist(self, name, desc=None, is_public=True, is_collaborative=False):
        playlist = self.spotify2.user_playlist_create(user=self.user_id, name=name, public=is_public, collaborative=is_collaborative, description=desc)
        return playlist['id']

    def add_songs_to_playlist(self, playlist_id, from_url=None, type="playlist", iterable=None):
        assert from_url is not None and iterable is not None
        if not iterable:
            iterable = self.create_tracks_uri_list(from_url, type=type)
        self.spotify.user_playlist_add_tracks(user=self.user_id, playlist_id=playlist_id, tracks=iterable)

    def create_liked_songs_playlist(self):
        playlist_id = self.create_playlist(name="Test Liked songs")
        tracks = self.spotify.current_user_saved_tracks()
        self.add_songs_to_playlist(playlist_id=playlist_id, iterable=tracks)


if __name__ == "__main__":
    client = SpotifyClient()
    # client.create_playlist(name="Test Playlist via spotify util")
