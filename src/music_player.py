"""
This file contains the music player class, which structures all the methods to
- play/pause/unpause music
- stop music
- go to the previous/next song
- skip to a certain part
and others
"""
# imports
import os
import pygame
from pygame import mixer
import fnmatch
import json

import theme
from classes.button import TextButton
from classes.playlist import Playlist, PlaylistManager, Song

# initialise pygame and set a title font
pygame.init()
title = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Bold.ttf", 40)

class MusicPlayer:
    def __init__(self, rootpath: str, refresh_global_playlists, dimensions: tuple[float, float]) -> None:
        """
        Arguments:
        - rootpath (str) path to the directory where all the music is stored
        - refresh_global_playlists (function) executed when the playlists are changed (in case of an error)
        - dimensions (tuple[int, int]) dimensions of the screen, required to pass into some other functions
        """
        # set the dimensions as the length and the height
        self.L, self.H = dimensions

        # load the playlists from Assets_PROG2/playlists.json
        with open("Assets_PROG2/playlists.json", "r") as playlists:
            loaded_object = json.load(playlists)
        sample_done: bool = False # sample refers to the first playlist to be loaded, as it is not otherwise possible to access the first playlist in a dictionary (unfortunately they don't work like lists)
        for p in loaded_object:
            # loading the songs
            songs = []
            for s in p['songs']:
                songs.append(Song(s["name"], s["path"], s["artist"]))
            if sample_done:
                # load it as a new playlist if there is already a sample in
                pl = Playlist(p['name'], songs)
                PlaylistManager.playlists[pl.id] = pl
            else:
                # if there isn't a sample yet, make one
                PlaylistManager.sample = Playlist(p['name'], songs)
                PlaylistManager.playlists[PlaylistManager.sample.id] = PlaylistManager.sample
                sample_done = True
            
        mixer.init() # initialise the mixer

        # make the arguments available class wide
        self.refresh_global_playlists = refresh_global_playlists
        self.rootpath = rootpath

        # initialise
        self.current_playlist = PlaylistManager.sample
        self.playlist_texts: list[TextButton] # refers to the TextButtons of the playlist view, not playlists themselves

        # music variables
        self.stopped = False
        self.paused = False
        self.current = 0
        self.muted = False

        # initialise the volume to be at 50%
        mixer.music.set_volume(0.5)
        self.volume = mixer.music.get_volume()

        # initialise some current song variables
        self.song_length = 0
        self.length_done: float = 0
        self.start_time = 0
        self.song_title: str = ""
        self.song_title_text = title.render(self.song_title, True, theme.current.norm_col)
        
        # start playing the sample (first playlist) after everything has been initialised
        self.change_playlist(PlaylistManager.sample.id, 0)
        return None
    
    
    def save_playlists(self) -> None:
        """
        Save the current playlist data into Assets_PROG2/playlists.json
        """
        data = []
        for k in PlaylistManager.playlists.keys():
            p = PlaylistManager.playlists[k] # get the playlist
            songs = []
            for s in p.songs: # append each song as a dictionary (class objects are best stored as dictionary items in json files)
                songs.append({"name": s.name, "path": s.path,"artist": s.artist})
            data.append({"name": p.name, "songs": songs}) # append each playlist as a dictionary too

        with open("Assets_PROG2/playlists.json", "w") as pl:
            # dump our data in the json file (overwrites previous changes)
            json.dump(data, pl)
        return None
    

    def change_playlist(self, id, offset) -> None:
        """
        Arguments:
        - id: (int) the id of the playlist to be played
        - offset (float/int) of screen elements at that time (required as this class also keeps track of the playlist view items)

        This method changes the current playlist and starts the provided playlits if possible
        """
        # set the current song to 0 (first song in the playlist)
        self.current = 0
        try: # try to change the playlist
            self.current_playlist = PlaylistManager.playlists[id]
        except KeyError: # if the playlist doesn't exist, something has gone wrong, so check what's going wrong by reloading all the playlists
            self.check_playlists() # saviour method to stop the application from breaking
            self.change_playlist(PlaylistManager.sample.id, offset) # once the playlists have been reloaded, just change the playlist to the sample (technically recursion, but that shouldn't actually happen)
            return None # return, the user can redo this method to open a different playlist
        
        # if the playlist exists, we can load it in
        # create the text boxes for the playlist view
        cp: list[TextButton] = []
        for i, s in enumerate(self.current_playlist.songs):
            s = s.name
            if len(s) > 32:
                s = s[:30]+"..." # shorten the title if it is too long
            cp.append(TextButton(self.play, (20+offset, 35+20*i), (0, 0), s, 1, id=i))

        self.playlist_texts = cp
        # start by playing the first song in the playlist
        self.play(0)
        return None
    

    def loadSongs(self) -> list:
        """
        Old way of loading songs, still kept as a last resort
        """
        all_songs = [] # to contain all mp3 files in our rootpath
        # walk through all the files in the rootpath
        for root, dirs, files in os.walk(self.rootpath):
            for filename in fnmatch.filter(files, "*.mp3"):
                # filter to only have .mp3 files
                all_songs.append(Song(filename[:len(filename)-4], self.rootpath+filename))
        return all_songs
    

    def set_song_title(self) -> None:
        """ Sets the song title for the main to a font object with the current song title """
        self.song_title_text = title.render(self.song_title, True, theme.current.norm_col)
        return None
    
    
    def check_playlists(self) -> None:
        """
        Check for whether the playlists in question are actually valid, existing playlists
        """
        new_playlists = {} # a dictionary to contain the new playlists
        sample_done: bool = False # to keep track of whether the first playlist has been added
        for playlist in PlaylistManager.playlists:
            # loop through the current dictionary of playlists
            songs: list[Song] = []
            for song in PlaylistManager.playlists[playlist].songs:
                if os.path.exists(song.path): # check if every song exists in the playlist
                    songs.append(song) # if any songs exists, it will exist in the new playlist too
            if len(songs) > 0: # the playlist will only exist if there are songs in it
                if not sample_done: # add the sample playlist if not added already
                    PlaylistManager.sample = Playlist(PlaylistManager.playlists[playlist].name, songs)
                    new_playlists[PlaylistManager.sample.id] = PlaylistManager.sample
                    sample_done = True
                else: # else add it as a new playlist
                    p = Playlist(PlaylistManager.playlists[playlist].name, songs)
                    new_playlists[p.id] = p
        # check if there are any valid playlists to load, and if so, load them in and refresh the global playlists
        if len(new_playlists) > 0:
            PlaylistManager.playlists = new_playlists
            self.change_playlist(PlaylistManager.sample.id, self.L/4)
            self.refresh_global_playlists()
        else:
            # this is an Avengers level threat, nothing can save the application anymore.
            print("FATAL ERROR: No Playlists Found.")
        return None
        

    def play(self, id, error=False) -> None:
        """
        Arguments:
        - id: (int) index of the song in the playlist
        - error: (bool) whether an error has occured and the song is being retried to load (this basically prevents recursion and breaking the playlist)
        
        Try to play the song, deal with error if they come up
        """
        if error: # if there has alrady been an error
            try: # retry loading the song
                mixer.music.load(self.current_playlist.songs[id].path)
                self.current = id
            except pygame.error: # if that doesn't work, stop and resort to checking errors with the playlist
                self.stop()
                # check the validity of this playlist
                self.check_playlists()
                return None
        else: # loading the song normally
            try: # try loading the song
                mixer.music.load(self.current_playlist.songs[id].path)
                self.current = id
            except IndexError: # if the song index is out of range, load the first song in the playlist
                mixer.music.load(self.current_playlist.songs[0].path)
                self.current = 0
            except pygame.error: # if the song doesn't exist, retry with error set to true
                print(f"Song {self.current_playlist.songs[id].name} not found at {self.current_playlist.songs[id].path}")
                self.loadSongs()
                self.play(id, True)
                return None
        # if the song has been successfully loaded, play it
        self.stopped = False
        self.paused = False
        mixer.music.play()
        # get the total song length for the time stamp (unoptimised)
        self.song_length = mixer.Sound.get_length(mixer.Sound(self.current_playlist.songs[self.current].path))
        # set progress bar stuff to 0 to start the new song from the very start
        self.length_done = 0
        self.start_time = 0
        # change the song title
        self.song_title = self.current_playlist.songs[self.current].name
        self.set_song_title()
        return None
    

    def pause(self) -> None:
        """ Pause the song if unpaused else unpause it """
        if self.paused:
            if self.stopped:
                # if the user is trying to play it while it has been stopped, restart the song
                self.play(self.current)
                self.stopped = False
            # unpause it regardless
            mixer.music.unpause()
            self.paused = False
        else:
            # pause it if the song was unpaused
            mixer.music.pause()
            self.paused = True
        return None
    

    def next(self) -> None:
        """ Go to the next song """
        self.play(self.current+1)
        return None


    def prev(self):
        """ Go to the previous song """
        self.play(self.current-1)
        return None


    def stop(self) -> None:
        """ Stop playing this song """
        mixer.music.pause() # using pause() instead of stop() since it was acting weird
        self.paused = True
        self.stopped = True
        return None
    

    def skip10(self) -> None:
        """ Moves 10 seconds ahead in the song """
        if self.stopped: # don't do it if it is stopped, as no music should be loaded
            return None
        if self.paused: # if it is paused, unpause it
            self.pause()
        # whatever the previous start time for the song was, add the length done since then + 10 to the new start time
        self.start_time += self.length_done+10
        mixer.music.play(start = self.start_time) # start the music at the new start time
        return None
    
        
    def rewind10(self) -> None:
        """ Rewinds 10 seconds in the song """
        if self.stopped: # don't do it if stopped
            return
        if self.paused: # unpause if the song is paused
            self.pause()
        self.start_time = max(0, self.start_time+self.length_done-10) # start from 0 if less than 10 seconds have elapsed, else move 10 seconds back in the song
        mixer.music.play(start = self.start_time)
        return None
    

    def skip_to(self, place) -> None:
        """
        Arguments:
        place: (float) what percent (as a decimal <= 1) of the song to skip to
        
        This method skips to a certain time in the song
        """
        self.start_time = place*self.song_length # set the start_time of the song in seconds to where the song should be
        mixer.music.play(start = self.start_time)
        self.stopped, self.paused = False, False # unpause it if needed
        return None
    
    
    def set_volume(self, val: float) -> None:
        """
        Arguments:
        val: (float) what the volume should be (as a decimal <= 1)

        This method sets the volume of the music player
        """
        self.volume = val
        if self.volume <= 0: # set it to zero and mute it if at zero or below
            self.volume = 0
            self.muted = True
        elif self.volume >= 1: # set it to max (one) and make sure it's unmuted
            self.volume = 1
            self.muted = False
        else: # keep it unmuted
            self.muted = False
        mixer.music.set_volume(self.volume)
        return None
    

    def change_volume(self, val: float) -> None:
        """
        Arguments:
        - val: (float) how much to change the volume by (usually + or - 0.05)

        Changes volume by increments/decrements of val
        """
        self.set_volume(mixer.music.get_volume()+val)
        return None
    
    
    def mute(self) -> None:
        """ Mute/Unmute the mixer """
        if self.muted: # if muted, unmute with atleast 5% of the volume
            if self.volume < 0.05:
                self.set_volume(0.05)
            else:
                mixer.music.set_volume(self.volume)
            self.muted = False
        else: # else mute it
            mixer.music.set_volume(0)
            self.muted = True
        return None
    
    
    def get_progress(self) -> float:
       """ Update the progress of the song """
       # find out how much of the song has been done
       self.length_done = mixer.music.get_pos()/1000
       try:
           return (self.length_done+self.start_time)/self.song_length # return it as a decimal out of 1
       except ZeroDivisionError:
           return 0

