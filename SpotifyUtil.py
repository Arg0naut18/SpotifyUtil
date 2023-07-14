from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from config import Config
import os
import logging


log = logging.getLogger(__name__)


class SpotifyUtil(Config):
    def __init__(self):
        super().__init__()
        self.auth_manager = SpotifyOAuth(client_id=self._client_id, client_secret=self._client_secret, redirect_uri=self._redirect_uri, scope=self._scope_str)
        self.spotify = Spotify(auth_manager=self.auth_manager)
        self.user = self.spotify.current_user()
        self.user_id = self.user['id']
        log.info(msg=self.user_id)

    def get_id(self, url:str, type="track"):
        return url.split(type+"/")[1].split('?')[0]

    def create_uri(self, url:str, type="track"):
        id = self.get_id(url=url, type=type)
        return f'spotify:{type}:{id}'
    
    def get_playlist_name_from_id(self, playlist_id):
        playlist = self.spotify.user_playlist(user=None, playlist_id=playlist_id, fields="name")
        return playlist['name']
    
    def get_tracks(self, url:str, type="playlist"):
        uri = self.create_uri(url=url, type=type)
        items = None
        if type=="playlist":
            items = self.spotify.playlist(uri)
        else:
            items = self.spotify.album(uri)
        return [track['track']['uri'] for track in items['tracks']['items']]
    
    def create_playlist(self, name, desc=None, is_public=True, is_collaborative=False):
        playlist = self.spotify.user_playlist_create(user=self.user_id, name=name, public=is_public, collaborative=is_collaborative, description=desc)
        log.info(f"Created playlist with name: {name}")
        return playlist['id']

    def add_songs_to_playlist(self, playlist_id=None, from_url=None, type="playlist", iterable=None, name="Test Playlist"):
        assert not ((from_url is not None) and (iterable is not None))
        if playlist_id is None:
            playlist_id = self.create_playlist(name=name)
        if not iterable:
            iterable = self.get_tracks(from_url, type=type)
        self.spotify.user_playlist_add_tracks(user=self.user_id, playlist_id=playlist_id, tracks=iterable)
        log.info("Songs added to playlist successfully")
        return self.get_playlist_name_from_id(playlist_id=playlist_id)

    def add_liked_songs_to_playlist(self, name="Test Liked songs", playlist_id=None):
        if not playlist_id: playlist_id = self.create_playlist(name=name)
        tracks = [track['track']['uri'] for track in self.spotify.current_user_saved_tracks()['items']]
        name = self.add_songs_to_playlist(name=name, playlist_id=playlist_id, iterable=tracks)
        log.info(f"Liked songs have been added to the playlist with name: {name}")

    def search(self, search_str):
        return self.spotify.search(search_str)["tracks"]["items"][0]["external_urls"]["spotify"].split("track/")[1]

    def get_track_IDs_from_names(self, iterable):
        track_ids = []
        for line in iterable:
            try:
                track_ids.append(self.search(line))
            except Exception as e:
                print("Error:")
                print(e)
        return track_ids
    
    def add_songs_to_playlist_from_file(self, file_path, playlist_id=None, name="Test Playlist"):
        """File structure has to be Song Name - Artist"""
        assert os.path.isfile(file_path)
        songs = []
        with open(file_path, "r") as file:
            for line in file:
                songs.append(line)
        Track_ids = self.get_track_IDs_from_names(songs)
        Track_ids = ["spotify:track:" + track for track in Track_ids]
        name = self.add_songs_to_playlist(playlist_id=playlist_id, iterable=Track_ids, name=name)
        log.info(f"Added songs from the file {file_path} to the playlist with name: {name}")
