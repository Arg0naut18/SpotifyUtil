from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from SpotifyUtil.config import Config
import os
import logging
from SpotifyUtil.file_reader import FileReader


log = logging.getLogger(__name__)


class SpotifyUtil(Config):
    def __init__(self, spotify_client_id=None, spotify_client_secret=None, spotify_redirect_uri=None):
        super().__init__(client_id=spotify_client_id, client_secret=spotify_client_secret, redirect_uri=spotify_redirect_uri)
        self.auth_manager = SpotifyOAuth(client_id=self._client_id, client_secret=self._client_secret, redirect_uri=self._redirect_uri, scope=self._scope_str)
        self.spotify = Spotify(auth_manager=self.auth_manager)
        self.user = self.spotify.current_user()
        self.user_id = self.user['id']
        log.debug(msg=self.user_id)

    def get_track_details(self, url: str):
        song = self.spotify.track(url)
        name = song['name']
        artist = song['album']['artists'][0]['name']
        return {"track": song, "name": name, "artist": artist, "uri": song['uri'], "available": self.check_track_is_available(song)}

    @staticmethod
    def get_id(url:str, type="track"):
        return url.split(type+"/")[1].split('?')[0]

    def create_uri(self, url:str, type="track"):
        id = self.get_id(url=url, type=type)
        return f'spotify:{type}:{id}'
    
    def get_playlist_name_from_id(self, playlist_id):
        playlist = self.spotify.user_playlist(user=None, playlist_id=playlist_id, fields="name")
        return playlist['name']
    
    def get_playlist_tracks(self, playlist_id):
        results = self.spotify.user_playlist_tracks(self.user_id, playlist_id)
        tracks = results['items']
        while results['next']:
            results = self.spotify.next(results)
            tracks.extend(results['items'])
        return tracks
    
    def get_tracks(self, url:str, type="playlist", verbose=False):
        uri = self.create_uri(url=url, type=type)
        items = None
        uri_list = []
        track_details_list = []
        if type=="playlist":
            items = self.get_playlist_tracks(uri)
            for track in items:
                temp = self.get_track_details(track['track']['uri'])
                track_details_list.append(temp)
                if not temp['available']:
                    continue
                uri_list.append(temp['uri'])
        else:
            items = self.spotify.album(uri)
            for track in items['tracks']['items']:
                temp = self.get_track_details(track['track']['uri'])
                track_details_list.append(temp)
                if not temp['available']:
                    continue
                uri_list.append(temp['uri'])
        if verbose:
            return track_details_list
        return uri_list
    
    def create_playlist(self, name, desc=None, is_public=True, is_collaborative=False):
        playlist = self.spotify.user_playlist_create(user=self.user_id, name=name, public=is_public, collaborative=is_collaborative, description=desc)
        log.debug(f"Created playlist with name: {name}")
        return playlist['id'], playlist['external_urls']['spotify']
    
    def get_difference(self, list1, list2):
        return list(set(list1)^set(list2))
        
    def get_different_tracks(self, url1, url2):
        list1 = self.get_tracks(url1, verbose=True)
        list2 = self.get_tracks(url2, verbose=True)
        return self.get_difference(list1, list2)
    
    def check_track_is_available(self, track) -> bool:
        result = False
        try:
            result = len(track['available_markets'])>0
        except:
            result = len(track['track']['available_markets'])>0
        return result
    
    def get_unavailable_songs(self, tracks):
        return [track['uri'] for track in tracks if not self.check_track_is_available(track)]
    
    def add_tracks_in_chunks(self, iterable, playlist_id):
        for idx in range(0, len(iterable), 100):
            chunk = iterable[idx:idx+100]
            self.spotify.user_playlist_add_tracks(user=self.user_id, playlist_id=playlist_id, tracks=chunk)

    def add_songs_to_playlist(self, playlist_url: str=None, from_url=None, type="playlist", iterable=None, name="Test Playlist", allow_duplicates:bool=False, description=None, is_public=True, is_collaborative=False):
        assert not ((from_url is not None) and (iterable is not None))
        if playlist_url is None or len(playlist_url)==0:
            playlist_id, playlist_url = self.create_playlist(name=name, desc=description, is_public=is_public, is_collaborative=is_collaborative)
        else: playlist_id = self.get_id(playlist_url, type="playlist")
        if not iterable:
            iterable = self.get_tracks(from_url, type=type)
        if allow_duplicates:
            self.add_tracks_in_chunks(iterable, playlist_id)
            log.debug("Songs added to playlist successfully")
        else:
            already_present_tracks = self.get_tracks(playlist_url)
            non_matching_tracks = self.get_difference(iterable, already_present_tracks)
            self.add_tracks_in_chunks(non_matching_tracks, playlist_id)
            log.debug("Songs added to playlist successfully")
        return self.get_playlist_name_from_id(playlist_id=playlist_id)

    def add_liked_songs_to_playlist(self, name="Test Liked songs", playlist_url=None, limit=20, offset=0):
        if not playlist_url or len(playlist_url)==0: playlist_id, playlist_url = self.create_playlist(name=name)
        else: playlist_id = self.get_id(playlist_url, type="playlist")
        tracks = [track['track']['uri'] for track in self.spotify.current_user_saved_tracks(limit=limit, offset=offset)['items']]
        name = self.add_songs_to_playlist(name=name, playlist_id=playlist_id, iterable=tracks)
        log.debug(f"Liked songs have been added to the playlist with name: {name}")

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
    
    def add_songs_to_playlist_from_file(self, file_path, playlist_url=None, name="Test Playlist", allow_duplicates=False):
        """File structure has to be Song Name - Artist"""
        assert os.path.isfile(file_path)
        songs = FileReader.read_songs(file_path=file_path)
        Track_ids = self.get_track_IDs_from_names(songs)
        Track_ids = ["spotify:track:" + track for track in Track_ids]
        name = self.add_songs_to_playlist(playlist_url=playlist_url, iterable=Track_ids, name=name, allow_duplicates=allow_duplicates)
        log.debug(f"Added songs from the file {file_path} to the playlist with name: {name}")

    def create_unavailable_track_playlist(self, name, playlist_id, description=None, is_public=True, is_collaborative=False):
        songs = self.get_tracks(playlist_id, verbose=True)
        to_be_added = self.get_unavailable_songs(songs)
        self.add_songs_to_playlist(name=name, iterable=to_be_added, description=description, is_public=is_public, is_collaborative=is_collaborative)
