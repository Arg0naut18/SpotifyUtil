from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from SpotifyUtil.config import Config
import os
import logging
from SpotifyUtil.file_reader import FileReader


log = logging.getLogger(__name__)

class TrackSetDetails:
    def __init__(self, total_size: int, playable_size: int, detailed_list: list[dict], unplayable_list:list):
        self.total_size = total_size
        self.playable_size = playable_size
        self.detailed_list = detailed_list
        self.unplayable_uris = unplayable_list


class SpotifyUtil(Config):
    """
    A utility that aims to create and modify spotify playlists and albums for you using a single function.
    """
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
        return {"track": song, "name": name, "artist": artist, "uri": song['uri'], "playable": self.check_track_is_playable(song)}

    @staticmethod
    def get_id(url:str, type="track"):
        return url.split(type+"/")[1].split('?')[0]

    def create_uri(self, url:str, type="track"):
        id = self.get_id(url=url, type=type)
        return f'spotify:{type}:{id}'
    
    def get_playlist_name_from_id(self, playlist_id):
        playlist = self.spotify.user_playlist(user=None, playlist_id=playlist_id, fields="name")
        return playlist['name']
    
    def get_playlist_tracks(self, playlist_id, market=None) -> list[dict]:
        results = self.spotify.user_playlist_tracks(self.user_id, playlist_id, market=market)
        tracks = results['items']
        while results['next']:
            results = self.spotify.next(results)
            tracks.extend(results['items'])
        return tracks
    
    def get_liked_songs(self, limit, offset) -> list[dict]:
        results = self.spotify.current_user_saved_tracks(limit=limit, offset=offset)
        tracks = results['items']
        while results['next']:
            results = self.spotify.next(results)
            tracks.extend(results['items'])
        return tracks
    
    def get_playlist_snapshot(self, playlist_id):
        return self.spotify.playlist(playlist_id=playlist_id)['snapshot_id']
    
    def distribute_tracks(self, iterable, avoid_unavailable):
        track_details_list = []
        unplayable_tracks_list = []
        uri_list = []
        for track in iterable:
            temp = self.get_track_details(track['track']['uri'])
            track_details_list.append(temp)
            if not temp['playable']:
                unplayable_tracks_list.append(temp['uri'])
                if avoid_unavailable: continue
            uri_list.append(temp['uri'])
        return track_details_list, unplayable_tracks_list, uri_list
    
    def get_tracks(self, url:str, type="playlist", verbose=False, avoid_unavailable=False, market=None):
        """
        Returns a dict containing list of URIs ("tracks"), No. of total tracks present ("total_tracks_length") and No. of playable tracks present ("playable_tracks_length") of all the tracks playable in the given url.\n
        Params:\n
        - `verbose` -> Set this to True if you want to get the entire track detail of each track present instead of only the URIs.\n
        - `type` -> Set the type of track set is it. Takes "Playlist" or "Album" as input. By default set to "Playlist"\n
        - `avoid_unavailable` -> Avoid getting tracks which are unavailable/unplayable. 
        """
        uri = self.create_uri(url=url, type=type)
        items = None
        if type=="playlist":
            items = self.get_playlist_tracks(uri, market=market)
            track_details_list, unplayable_tracks_list, uri_list = self.distribute_tracks(iterable=items, avoid_unavailable=avoid_unavailable)
        else:
            items = self.spotify.album(uri)
            track_details_list, unplayable_tracks_list, uri_list = self.distribute_tracks(iterable=items['tracks']['items'], avoid_unavailable=avoid_unavailable)
        if verbose:
            total_size = len(track_details_list)
            unplayable_tracks_size = len(unplayable_tracks_list)
            playable_size = total_size - unplayable_tracks_size
            return TrackSetDetails(total_size=total_size, playable_size=playable_size, detailed_list=track_details_list, unplayable_list=unplayable_tracks_list)
        return uri_list
    
    def create_playlist(self, name, desc=None, is_public=True, is_collaborative=False):
        """
        Creates a playlist in the user account in spotify.\n
        Params:\n
        - `name` -> The name of the playlist\n
        - `desc` -> The description of the playlist. (Optional)\n
        - `is_public` -> Set if the playlist is supposed to be public. By default set to True. When set to False, it creates a private playlist.\n
        - `is_collaborative` -> Set if the type of playlist is collaborative or not. By default set to False.
        """
        playlist = self.spotify.user_playlist_create(user=self.user_id, name=name, public=is_public, collaborative=is_collaborative, description=desc)
        log.debug(f"Created playlist with name: {name}")
        return playlist['id'], playlist['external_urls']['spotify']
    
    def get_difference(self, list1: list|TrackSetDetails, list2: list|TrackSetDetails, mode="to_be_added"):
        if isinstance(list1, TrackSetDetails):
            full_list1 = list1.detailed_list
            list1 = [track['uri'] for track in full_list1]
            full_list2 = list2.detailed_list
            list2 = [track['uri'] for track in full_list2]
        set1 = set(list1)
        set2 = set(list2)
        if mode=="to_be_added":
            return list(set2.difference(set1))
        return list(set1.difference(set2))
    
    def get_difference_multi(self, main, mode="to_be_added", *lists):
        result = set()
        if mode=="to_be_removed":
            return list(set(main).difference([set(li) for li in lists]))
        for li in lists:
            result = result.union(set(li).difference(set(main)))
        return list(result)
    
    def get_total_songs_length(self, url):
        results = self.spotify.user_playlist_tracks(self.user_id, url)
        tracks = results['total']
        while results['next']:
            results = self.spotify.next(results)
            tracks+=results['total']
        return tracks
    
    def get_playable_songs_length(self, url):
        results = self.get_playlist_tracks(url)
        count = 0
        for track in results:
            if self.check_track_is_playable(track):
                count+=1
        return count
        
    def get_different_tracks(self, url1, url2):
        """
        Returns a list of all the track URIs that are not present in any one of the track sets.
        """
        list1 = self.get_tracks(url1, verbose=True)
        list2 = self.get_tracks(url2, verbose=True)
        return self.get_difference(list1, list2)
    
    def check_track_is_playable(self, track) -> bool:
        """
        Checks if the market of the track is null or not.
        """
        result = False
        try:
            result = len(track['available_markets'])>0
        except:
            try:
                result = track['is_playable']==True
            except:
                result = len(track['track']['available_markets'])>0
        return result
    
    def get_unplayable_songs(self, tracks):
        return [track['uri'] for track in tracks if not self.check_track_is_playable(track)]
    
    def add_tracks_in_chunks(self, iterable, playlist_id):
        for idx in range(0, len(iterable), 100):
            chunk = iterable[idx:idx+100]
            self.spotify.user_playlist_add_tracks(user=self.user_id, playlist_id=playlist_id, tracks=chunk)

    def add_songs_to_playlist(self, 
                            playlist_url: str=None, 
                            from_url=None, 
                            type="playlist", 
                            iterable=None, 
                            name="Test Playlist", 
                            allow_duplicates:bool=False,
                            skip_unplayables:bool=False,
                            description=None, 
                            is_public=True, 
                            is_collaborative=False
                            ):
        """
        Adds songs to a playlist.\n
        Params:\n
        - `playlist_url` -> The url of the playlist you want to add your songs to. (Optional)\n
        - `from_url` -> The url of the track set you want to add your songs from. (Optional)\n
        - `type` -> The type of the track set. Can be "playlist" or "Album". Set to "playlist" by default\n
        - `iterable` -> If you have a list of track urls you want to add your songs from use this to store the iterable. Should not be used if there is already a from_url\n
        - `allow_duplicates` -> A boolean to set if you want to allow duplicate songs to be added again in the playlist. Set to False by default.\n
        - `skip_unplayables` -> A boolean to set if you want to allow unplayable songs to be added again in the playlist. Set to False by default.\n
        *If you do not have a playlist url then the following params are needed:\n
        - `name` -> Name of the playlist you want to create.\n
        - `description` -> The description of the playlist. (Optional)\n
        - `is_public` -> Set if the playlist is supposed to be public. By default set to True. When set to False, it creates a private playlist.\n
        - `is_collaborative` -> Set if the type of playlist is collaborative or not. By default set to False.
        """
        assert not ((from_url is not None) and (iterable is not None))
        if playlist_url is None or len(playlist_url)==0:
            playlist_id, playlist_url = self.create_playlist(name=name, desc=description, is_public=is_public, is_collaborative=is_collaborative)
        else: playlist_id = self.get_id(playlist_url, type="playlist")
        if not iterable:
            iterable = self.get_tracks(from_url, type=type, avoid_unavailable=skip_unplayables)
        if allow_duplicates:
            self.add_tracks_in_chunks(iterable, playlist_id)
            log.debug("Songs added to playlist successfully")
        else:
            already_present_tracks = self.get_tracks(playlist_url, avoid_unavailable=skip_unplayables)
            non_matching_tracks = self.get_difference(already_present_tracks, iterable)
            self.add_tracks_in_chunks(non_matching_tracks, playlist_id)
            log.debug("Songs added to playlist successfully")
        return self.get_playlist_name_from_id(playlist_id=playlist_id)

    def add_liked_songs_to_playlist(self, name="Test Liked songs", playlist_url=None, limit=20, offset=1, is_public=True, is_collaborative=False, desc=None):
        """
        Adds your liked songs to a playlist.\n
        Params:\n
        - `name` -> Name of the playlist if playlist doesn't exist already. (Optional)\n
        - `playlist_url` -> The URL of the playlist you want to add your liked songs to. If provided, new playlist will not be created. (Optional)\n
        - `limit` -> The no. of songs you want to add to your playlist.\n
        - `offset` -> The playlist will contain songs starting from this numbered track in your liked songs.
        """
        if not playlist_url or len(playlist_url)==0: playlist_url = self.create_playlist(name=name, desc=desc, is_public=is_public, is_collaborative=is_collaborative)[1]
        tracks = [track['track']['uri'] for track in self.get_liked_songs(limit=limit, offset=offset-1)]
        name = self.add_songs_to_playlist(name=name, playlist_url=playlist_url, iterable=tracks, is_public=is_public, is_collaborative=is_collaborative)
        log.debug(f"Liked songs have been added to the playlist with name: {name}")

    def delete_tracks(self, playlist_url, iterable):
        for idx in range(0, len(iterable), 100):
            chunk = iterable[idx:idx+100]
            self.spotify.user_playlist_remove_all_occurrences_of_tracks(self.user_id, playlist_url, chunk)

    def clear_playlist(self, playlist_url):
        tracks = self.get_tracks(playlist_url)
        self.delete_tracks(playlist_url=playlist_url, iterable=tracks)

    def search(self, search_str):
        """
        Searches for a song in spotify with the given search string and returns it's ID.
        """
        return self.spotify.search(search_str)["tracks"]["items"][0]["external_urls"]["spotify"].split("track/")[1]

    def get_track_IDs_from_names(self, iterable):
        """
        Searches for a song in spotify with the given list of search strings and returns their IDs.
        """
        track_ids = []
        for line in iterable:
            try:
                track_ids.append(self.search(line))
            except Exception as e:
                print("Error:")
                print(e)
        return track_ids
    
    def add_songs_to_playlist_from_file(self, file_path, playlist_url=None, name="Test Playlist", allow_duplicates=False, skip_unplayables=False):
        """
        Adds songs to a playlist from a given file.\n
        Note: File content structure has to be Song Name - Artist\n
        Params:\n
        - `name` -> Name of the playlist if playlist doesn't exist already. (Optional)\n
        - `playlist_url` -> The URL of the playlist you want to add songs to. If provided, new playlist will not be created. (Optional)\n
        - `file_path` -> The path of the file you want to add your songs from. The content of the file has to be "Song Name - Artist" separated by newlines.\n
        - `allow_duplicates` -> A boolean to set if you want to allow duplicate songs to be added again in the playlist. Set to False by default.\n
        - `skip_unplayables` -> A boolean to set if you want to allow unplayable songs to be added again in the playlist. Set to False by default.\n
        """
        assert os.path.isfile(file_path)
        songs = FileReader.read_songs(file_path=file_path)
        Track_ids = self.get_track_IDs_from_names(songs)
        Track_ids = ["spotify:track:" + track for track in Track_ids]
        name = self.add_songs_to_playlist(playlist_url=playlist_url, iterable=Track_ids, name=name, allow_duplicates=allow_duplicates, skip_unplayables=skip_unplayables)
        log.debug(f"Added songs from the file {file_path} to the playlist with name: {name}")

    def create_unplayable_track_playlist(self, name, playlist_url, description=None, is_public=True, is_collaborative=False, market=None):
        """
        Creates a playlist with all the unplayable tracks present in the given playlist url.\n
        Params:\n
        - `name` -> Name of the playlist you want to create.\n
        - `playlist_url` -> The URL of the playlist you want to add songs from.\n
        - `description` -> The description of the playlist. (Optional)\n
        - `is_public` -> Set if the playlist is supposed to be public. By default set to True. When set to False, it creates a private playlist.\n
        - `is_collaborative` -> Set if the type of playlist is collaborative or not. By default set to False.
        """
        songs = self.get_tracks(playlist_url, verbose=True, market=market)
        to_be_added = self.get_unplayable_songs(songs.detailed_list)
        self.add_songs_to_playlist(name=name, iterable=to_be_added, description=description, is_public=is_public, is_collaborative=is_collaborative)
