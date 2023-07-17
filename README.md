# SpotifyUtil
SpotifyUtils is a very useful library made over Spotipy to automate some rather tiring tasks.

## Features
- Add songs to a playlist/album (creates one if name is provided instead of playlist url)
- Add songs to a playlist/album from a text file if it has the tracks' name and artist ("Name - Artist" format) in a newline separated way.
- Removes duplicates while adding songs if the flag is set to true.
- Creates a playlist out of your liked songs
- Create a playlist out of all the unavailable songs present in your playlist. Can also avoid unavailable songs while creating a new playlist.

## Usage
```python
from SpotifyUtil import SpotifyUtil

os.environ["SPOTIPY_CLIENT_ID"] = "Your Spotify Client ID"
os.environ["SPOTIPY_CLIENT_SECRET"] = "Your Spotify Client Secret"
os.environ["SPOTIPY_REDIRECT_URI"] = "Your Spotify Redirect URI"

sp = SpotifyUtil()
sp.add_liked_songs_to_playlist(name="Test Liked songs", limit=20)
```
or
```python
from SpotifyUtil import SpotifyUtil


sp = SpotifyUtil(
    spotify_client_id="Your Spotify Client ID",
    spotify_client_secret="Your Spotify Client Secret",
    spotify_redirect_uri="Your Spotify Redirect URI"
    )
    
sp.add_liked_songs_to_playlist(name="Test Liked songs", limit=20)
```