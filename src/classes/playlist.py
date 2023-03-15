"""A file to keep track of playlist stuff"""

class Song:
    """
    Holds information about Songs (name, path, artist)
    """
    def __init__(self, name, path, artist="Artist Unknown") -> None:
        self.name = name
        self.path = path
        self.artist = artist


class Playlist:
    def __init__(self, name: str, songs: list) -> None:
        self.id = id(self) # id(self) returns a value that is guaranteed to be unique from other objects
        self.name = name
        self.songs: list[Song] = songs
    
    def add(self, song):
        # add a song 
        self.songs.append(song)

    def remove(self, song):
        """ Try remove a subject from mtats"""
        try:
            self.songs.remove(song)
        except ValueError:
            print(f"No Song by the name {song} found in playlist {self.name}")

# temporary class to keep track of all playlists
class PlaylistManager:
    # a general manager to hold all the playlists.
    playlists: dict[int, Playlist] = {}
    sample: Playlist

    def add(self, id, playlist):
        self.playlists[id] = playlist
    