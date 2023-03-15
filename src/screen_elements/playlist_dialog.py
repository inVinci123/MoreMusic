"""
This file holds classes essential for the playlist dialog, which allows the user to:
- edit playlists
- delete playlists
- create new playlists
"""

# imports
import pygame
from copy import deepcopy
from tkinter import Tk, filedialog
from math import ceil

# the following two lines are necessary to allow tkinter's filedialog to work
root = Tk()
root.withdraw()

# more imports
import theme
from classes.button import TextButton, ImageButton
from classes.playlist import Playlist, PlaylistManager, Song
from classes.input_field import InputField
from classes.sidebar import Sidebar
from music_player import MusicPlayer
from screen_elements.playlist_view import create_pages

# intialise pygame to use the following fonts
pygame.init()

# declare the fonts to be used in the classes
title_font = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Bold.ttf", 40)
subtitle_font = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Medium.ttf", 24)
small_font = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Thin.ttf", 16)

class SongCard:
    """
    Class to blueprint SongCards (editable display for songs)
    """
    def __init__(self, song_name: str = "Add a new song", song_path = "Add a path", song_artist="Artist Unknown", song_id = -1, delete_function = lambda *_: None, change_song_function = lambda *_:None, pos = (0, 0), size = (850, 20)) -> None:
        """
        Arguments:
        - song_name: (string) name of the song
        - song_path: (string) path to the song
        - song_artist: (string) artist of the song
        - song_id: (integer) position of the song in the playlist (not to be confused with Song.id)
        - delete_function: (function) function to execute if the delete icon is pressed
        - change_song_function: (function) function to reflect the value of this song in the PlaylistDialog's songs
        - pos: (tuple) position of the SongCard
        - size: (tuple) size of the SongCard
        """
        # set the dimensions and location to use in the class
        self.pos, self.size = pos, size

        # set the song information to use in the class
        self.name, self.path, self.artist = song_name, song_path, song_artist
        self.song_id = song_id

        # set the functions to use in the class
        self.remove = delete_function
        self.change_song = change_song_function

        # this boolean keeps track of whether the song card is modified from the playlist dialog list or not
        self.modified: bool = False

        # initialise these booleans to be false, to keep track of whether one of them is being edited
        self.editing_name, self.editing_path, self.editing_artist = False, False, False

        # intialise the relevant buttons that both show the respective field and allow the user to edit the field
        self.name_button = TextButton(self.edit_name, (self.pos[0] + 5, self.pos[1] + 5), (0, 0), self.name[:32]+"..."if len(self.name)>35 else self.name)
        self.artist_button = TextButton(self.edit_artist, (self.pos[0] + 245, self.pos[1] + 5), (0, 0), self.artist[:32]+"..."if len(self.artist)>35 else self.artist)
        self.path_button = TextButton(self.edit_path, (self.pos[0] + 455, self.pos[1] + 5), (0, 0), self.path[:38]+"..." if len(self.path) > 40 else self.path)
        
        # initialise the input field for the name to edit the name and default it's name to the song name 
        self.name_field = InputField((self.pos[0]+5, self.pos[1]+5))
        self.name_field.is_active = True # the name_field will be controlled manually so leave it to be always true
        self.name_field.text = song_name

        # initialise the input field for the artist to edit the name and default it's name to the song artist 
        self.artist_field = InputField((self.pos[0]+245, self.pos[1]+5))
        self.artist_field.is_active = True # the artist_field will be controlled manually so leave it to be always true
        self.artist_field.text = song_artist

        # initialise the two buttons that delete or confirm changes on the song card
        self.delete_icon = ImageButton(lambda: self.remove(self.song_id), "cross.png", f"./Assets_PROG2/Icons/{theme.current_name}_cross.png", f"./Assets_PROG2/Icons/{theme.current_name}_cross_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_cross_click.png", (self.pos[0]+self.size[0]-20, self.pos[1]+5), (15, 15))
        self.confirm_icon = ImageButton(self.confirm, "tick.png", f"./Assets_PROG2/Icons/{theme.current_name}_tick.png", f"./Assets_PROG2/Icons/{theme.current_name}_tick_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_tick_click.png", (self.pos[0]+self.size[0]-45, self.pos[1]+5), (15, 15))
        return None
    

    def edit_name(self) -> None:
        """
        Called through the name_button to activate the name input field and disallow the name button from rendering.
        """
        self.stop_editing_artist() # stop editing the artist field if it was being edited to avoid multiple inputs
        self.editing_name = True
        self.name_field.text = self.name # change the name_field text and activate it
        self.name_field.is_active = True
        return None
    
    
    def confirm(self) -> None:
        """
        Apply the modifications on the SongCard to the Songs in the Playlist Dialog
        """
        self.change_song(self.song_id, Song(self.name, self.path, self.artist))
        return None
    
    
    def edit_artist(self) -> None:
        """
        Called through the artist_button to activate the artist input field and disallow the artist button from rendering.
        """
        self.stop_editing_name() # stop editing the name field if it was being edited to avoid multiple inputs
        self.editing_artist = True
        self.artist_field.text = self.artist # change the artist_field text and activate it
        self.artist_field.is_active = True
        return None
    

    def stop_editing_name(self) -> None:
        """
        Disable the name_field, allow the name button to render and note that the name has been modified
        """
        self.name_button.click, self.name_button.hover = False, False # needed else it bugs out
        
        self.editing_name = False # allows the name button to render

        # update the name in accordance to the name field text
        self.name = self.name_field.text if self.name_field.text != "" else "Add the song title"
        self.name_button.update_text(self.name[:32]+"..."if len(self.name)>35 else self.name)
        self.modified = True # note that the SongCard was modified
        return None
        

    def stop_editing_artist(self) -> None:
        """
        Disable the artist_field, allow the artist button to render and note that the artist has been modified
        """
        self.artist_button.click, self.artist_button.hover = False, False # needed else it bugs out
        
        self.editing_artist = False # allows the artist button to render

        # update the aritst in accordance to the artist field text
        self.artist = self.artist_field.text if self.artist_field.text != "" else "Artist Unknown"
        self.artist_button.update_text(self.artist[:32]+"..."if len(self.artist)>35 else self.artist)
        self.modified = True # note that the SongCard has been modified
        return None
    
        
    def edit_path(self) -> str:
        """
        Stops editing all fields and uses Tkinter's file dialog to open an mp3 file to record it as a path
        """
        # stop all other edits
        self.stop_editing_name()
        self.stop_editing_artist()
        # obtain the file path from the user
        path = filedialog.askopenfilename(title="Select your song", filetypes=[("Mp3 files", "*.mp3")])

        # if the user put a path, update the path and update the changes in the playlist dialog
        if path:
            self.path = path
            self.path_button.update_text(self.path[:38]+"..." if len(self.path) > 40 else self.path)
            self.change_song(self.song_id, Song(self.name, self.path, self.artist))
            self.modified = False
        return path # required to work with the inherited class
    

    def draw(self, screen, check, mouse, r_click) -> None:
        """
        Arguments:
        - screen: the pygame surface to draw the elements on [passed by reference]
        - check: a boolean indicating whether the elements should check for hover and clicks or not
        - mouse: a tuple with the x, y coords of the mouse on the screen.
        - m_down: a bool indicating whether the user is right clicking or not

        This method:
        - draws the delete_icon if it exists
        - draws the confirm icon if modifications have been made
        - draws the name_field/name_button depending on which one is active
        - draws the artist_field/artist_button depending on which one is active
        """
        # if the delete icon exists, draw it (it doesn't exist in the inherited class, which is why this measure is necessary)
        if self.delete_icon:
            if self.delete_icon.hover:
                # if the mouse is hovering over the delete icon, draw a translucent surface indicating which SongCard is subject to being deleted
                a = pygame.Surface(self.size)
                a.fill(theme.current.hov_col)
                a.set_alpha(100)
                screen.blit(a, (self.pos[0], self.pos[1]+3))
            # draw the delete icon
            self.delete_icon.draw(screen, check, mouse, r_click)
        
        # if there are modifications in the SongCard, draw it (the icon should only show up if there are modifications in the song card to save)
        if self.modified:
            if self.confirm_icon.hover:
                # if the mouse is hovering over the confirm icon, draw a translucent surface indicating which SongCard is subject to being confirmed
                a = pygame.Surface(self.size)
                a.fill(theme.current.hov_col)
                a.set_alpha(100)
                screen.blit(a, (self.pos[0], self.pos[1]+3))
            # draw the confirm icon
            self.confirm_icon.draw(screen, check, mouse, r_click)

        # draw the name field or the name button depending on what is supposed to be drawn
        if self.editing_name:
            self.name_field.draw(screen, check, mouse, r_click)
        else:
            self.name_button.draw(screen, check, mouse, r_click)
        
        # draw the artist field or the artist button depending on what is supposed to be drawn
        if self.editing_artist:
            self.artist_field.draw(screen, check, mouse, r_click)
        else:
            self.artist_button.draw(screen, check, mouse, r_click)
        
        # always draw the path button
        self.path_button.draw(screen, check, mouse, r_click)
        return None
        

class NewSongCard(SongCard):
    """
    Inherited class that works as a way to add new songs instead of modifying old ones
    """
    def __init__(self, song_name="Add a new song", song_path="Add a path", pos=(0, 0), size=(700, 20), add_song_function = lambda *_: None, song_artist="Artist Unknown") -> None:
        """
        Arguments:
        - song_name: (string) name of the song, usually just "Add a new song"
        - song_path: (string) path to the song, usually just "Add a path"
        - song_artist: (string) artist of the song, usually just "Artist Unknown"
        - change_song_function: (function) function to reflect the value of this song in the PlaylistDialog's songs
        - pos: (tuple) position of the SongCard
        - size: (tuple) size of the SongCard
        """
        # call the parent class's constructor with some default values (delete function and change song function are defaulted as they won't be utilised in this version of the SongCard)
        super().__init__(song_name=song_name, song_path=song_path, song_artist=song_artist, song_id=-1, pos=pos, size=size)

        # add_song function to add a new song to the list instead of changing pre-existing songs
        self.add_song = add_song_function
        self.delete_icon = None # the delete_icon has been... deleted. (It won't be necessary since you can't delete a non existing song)
        return None
    

    def edit_path(self) -> None:
        """
        Takes the returned path value from the constructor and updates the song list with a new song if the path is valid
        """
        path = super().edit_path()
        if path:
            self.add_song(Song(self.name, self.path, self.artist))
        return None
    
    
    def draw(self, screen, check, mouse, r_click) -> None:
        """
        Execute the normal draw method but always set modified to false, since it won't be necessary for a NewSongCard
        """
        self.modified = False
        super().draw(screen, check, mouse, r_click)
        return None


class PlaylistDialog:
    def __init__(self, playlist_bar: Sidebar, music_player: MusicPlayer, update_global_playlist, refresh_global_songs) -> None:
        """
        Arguments:
        - playlist_bar: (Sidebar) the sidebar that contains the playlists (to add a new playlist when necessary) [passed by reference]
        - music_player: (MusicPlayer) the global MusicPlayer to save playlists and access other variables [passed by reference]
        - update_global_playlist: (function) a function in the main that changes the current playlist being played, required to pass to a new options for the playlist bar
        - refresh_global_songs: (function) a function in the main that will refresh the playlists in the sidebar and update the playlist view
        """
        # set functions and references to be used in the class
        self.pl_option_func = update_global_playlist
        self.refresh_global_songs = refresh_global_songs
        self.pl_bar = playlist_bar
        self.player = music_player
        
        # initialise the input field and prompt for the playlist's name
        self.name_text = subtitle_font.render("Playlist Name: ", True, theme.current.norm_col)
        self.name_field = InputField((420, 100))

        # intialise two lists, songs (to hold actual song objects) and song_cards (to hold the song cards including the NewSongCard)
        self.songs: list[Song] = []
        self.song_cards: list[SongCard] = []
        self.song_cards.append(NewSongCard(pos = (100, 220+len(self.songs)*20), add_song_function=self.add_new_song)) # type: ignore

        # initialise the page variables
        self.pages: list[list[SongCard]] = []
        self.songspp: int = 10 # songs per page
        self.page_num: int = 0
        self.show_pages: bool = False

        # initalise the next page and previous page images and default them to an inactive colour, intialise the page text
        self.next_page_button = ImageButton(self.next_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", (535, 250+23*self.songspp), (10, 10))
        self.prev_page_button = ImageButton(self.prev_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", (450, 250+23*self.songspp), (10, 10), flip=True)
        self.prev_page_button.image = self.prev_page_button.hov_img
        self.next_page_button.image = self.next_page_button.hov_img
        self.page_text = small_font.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)

        # more playlist stuff to check if it's open and whether it is being edited or is it a new playlist
        self.is_open: bool = False
        self.playlist_id = None # None = new playlist, if there is an id it means it is editing that playlist

        # intialise the save, close and delete buttons
        self.submit_button = TextButton(self.submit, (60, 100), (0, 0), "Save", 2)
        self.close_button = ImageButton(self.close, "cross.png", f"./Assets_PROG2/Icons/{theme.current_name}_cross.png", f"./Assets_PROG2/Icons/{theme.current_name}_cross_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_cross_click.png", (1045, 10), (25, 25))
        self.delete_button = TextButton(self.delete_playlist, (750, 100), (0, 0), "Delete Playlist")

        # refresh songs to update the pages to be displayed
        self.refresh_songs(self.songs)
        return None
    

    def delete_playlist(self) -> None:
        """
        Deletes the playlist if it is not the only playlist in existence (according to the application)
        """
        if len(PlaylistManager.playlists) == 1:
            return # don't delete it if there are no othre playlists
        
        if self.playlist_id:
            # if it is a playlist that was being edited, delete it by removing it from the Playlist Manager (go the classes.playlist for more info)
            PlaylistManager.playlists.pop(self.playlist_id)
            self.refresh_global_songs(PlaylistManager.sample.id) # update the global playlists to reflect the change
        
        # clear the songs and refresh the view ready for the next time it will be edited
        self.songs.clear()
        self.refresh_songs(self.songs)
        self.name_field.text = ""
        self.playlist_id = None
        self.player.save_playlists() # save the playlists in playlists.json to reflect the change everytime the playlists are loaded (more on that in music_player)
        self.close()
        return None
    

    def open(self, new=True) -> None:
        """
        Arguments:
        - new: (bool) to see if the playlist dialog should produce a new playlist or not
        """
        self.is_open = True 
        if self.playlist_id == None or new:
            # if there is no playlist id or if it is to be a new playlist, clear the song lists and title and make a new playlits
            self.songs.clear()
            self.song_cards.clear()
            self.name_field.text = ""
            self.refresh_songs(self.songs)
        return None
    
    
    def close(self) -> None:
        """
        Deactivate all the fields and close the playlist dialog
        """
        self.name_field.is_active = False
        for s in self.song_cards:
            s.name_field.is_active = False
        self.is_open = False
        return None


    def next_page(self) -> None:
        """
        Move to the next page if possible and update the page text
        """
        if self.page_num < len(self.pages):
            self.page_num += 1
            self.page_text = small_font.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        return None
    
    
    def prev_page(self) -> None:
        """
        Move to the previous page if possible and update the page text
        """
        if self.page_num > 0:
            self.page_num -= 1
            self.page_text = small_font.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        return None
    

    def load_theme(self) -> None:
        """
        Reinitialise the necessary buttons and images and refresh the songs to load the new theme
        """

        self.name_text = subtitle_font.render("Playlist Name: ", True, theme.current.norm_col)
        
        # buttons
        self.submit_button = TextButton(self.submit, (60, 100), (0, 0), "Save", 2)
        self.delete_button = TextButton(self.delete_playlist, (750, 100), (0, 0), "Delete Playlist")
        self.close_button = ImageButton(self.close, "cross.png", f"./Assets_PROG2/Icons/{theme.current_name}_cross.png", f"./Assets_PROG2/Icons/{theme.current_name}_cross_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_cross_click.png", self.close_button.pos, self.close_button.size)
        # page buttons
        self.next_page_button = ImageButton(self.next_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", (535, 250+23*self.songspp), (10, 10))
        self.prev_page_button = ImageButton(self.prev_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", (450, 250+23*self.songspp), (10, 10), flip=True)
        self.prev_page_button.image = self.prev_page_button.hov_img
        self.next_page_button.image = self.next_page_button.hov_img
        # refresh
        self.refresh_songs(self.songs)
        return None
    

    def update_songs(self, index: int, song: Song) -> None:
        """
        Arguments:
        - index: (index) the index of the song to be updated in the playlist
        - song: (Song) the value of the song to be updated

        This method changes a specific song to another song
        """
        self.songs[index] = song
        self.refresh_songs(self.songs)
        return None
    
    
    def refresh_songs(self, song_list: list[Song]) -> None:
        """
        Arguments:
        - song_list: (list[Song]) the list of songs to update to

        This method:
        - clears the current songs and updates them with the new song list provided
        - creates pages out of the new songs and updates the page info
        """
        # create a deepcopy to ensure that weird stuff doesn't happen (since generally self.songs is passed as a song_list, which becomes problematic as it is cleared inside the method)
        songs = deepcopy(song_list)
        # clear the old songs
        self.songs.clear()
        self.song_cards.clear()
        self.pages.clear()
        
        nsc_added = False # bool to keep track of whether the new song card has been added to the song_cards or not
        for pg in range(ceil(len(songs)/self.songspp)): # iterate through the number of pages to be made
            for i in range(self.songspp): 
                try:
                    self.add_song(songs[pg*self.songspp+i], i) # try adding the corresponding song to the song cards positioned in relation to their page index i
                except IndexError: # if the index is out of range, we can append the New Song Card at the final index and break the loop
                    nsc_added = True
                    self.song_cards.append(NewSongCard(pos=(100, 200+i*23), add_song_function=self.add_new_song)) # type: ignore <- needed to convince the IDE that I am not playing with fire
                    break
        if not nsc_added: # if the new song card was not added (can happen if the number of songs is a multiple of songspp), add it like it's on a page
            self.song_cards.append(NewSongCard(pos = (100, 200), add_song_function=self.add_new_song)) # type: ignore

        # use the method create pages (borrowed from another file to do it's magic) to create a list of pages based on the provided list
        self.pages = create_pages(self.song_cards, self.songspp)
        
        # update the page stuff according to the pages generated
        self.page_text = small_font.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        self.prev_page_button.image = self.prev_page_button.hov_img
        self.next_page_button.image = self.next_page_button.hov_img
        self.show_pages = len(self.pages)>1
        self.page_num = len(self.pages)-1
        self.page_text = small_font.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)

        return None
    

    def add_song(self, song: Song, i: int) -> None:
        """
        Arguments:
        - song (Song) the song to be added
        - i (int) the relative position of the song on the page

        Add a song to the lists and create a Song Card for it. Used exclusively in refresh songs
        """
        self.songs.append(song)
        self.song_cards.append(SongCard(song.name, song.path, song.artist, len(self.songs)-1, self.remove, self.update_songs, (100, 200+i*23))) # type: ignore
        return None
    

    def add_new_song(self, song: Song) -> None:
        """
        Arguments:
        - song (Song) the song to be added to the list

        This method is passed to the NewSongCard to add a new song and refresh the songs
        """
        self.songs.append(song)
        self.refresh_songs(self.songs)
        return None


    def remove(self, index: int) -> None:
        """
        Arguments:
        - index: (int) the index of the song to be removed

        This method is passed to each Song Card to allow them to remove themselves and refresh the songs
        """
        self.songs.pop(index)
        self.refresh_songs(self.songs)
        return None


    def edit_playlist(self, id: int) -> None:
        """
        Arguments:
        - id: (int) the id of the playlist to edit

        Load a pre-existing playlist to edit it
        """
        # set the id of the playlist to be edited as a class variable, change the title to the playlist name, and refresh the songs with the playlist songs
        self.playlist_id = id
        self.name_field.text = PlaylistManager.playlists[id].name
        self.open(False)
        self.refresh_songs(PlaylistManager.playlists[id].songs)
        return None
    

    def submit(self) -> None:
        """
        Checks if the playlist is valid, updates the playlist if it is editing one else creates a new one
        """
        self.refresh_songs(self.songs) # to ensure nothing is missed out
        # check if the playlist actually has songs
        if len(self.songs) == 0:
            return None
        # if the playlist is being edited, update that
        if self.playlist_id:
            PlaylistManager.playlists[self.playlist_id].name = self.name_field.text
            PlaylistManager.playlists[self.playlist_id].songs = deepcopy(self.songs)
        else:
            # else create a new playlist and add it to the playlists as well as the options in the playlist bar
            p = Playlist(self.name_field.text, deepcopy(self.songs))
            PlaylistManager.playlists[p.id] = p
            self.pl_bar.add_option((p.name[:13]+"..." if len(p.name)>16 else p.name, lambda: self.pl_option_func(p.id)))
            self.playlist_id = p.id
        
        # finally, save the playlists and refresh the global songs before closing the dialog
        self.player.save_playlists()
        self.playlist_id = None
        self.refresh_global_songs()
        self.close()
        return None
    

    def draw(self, screen: pygame.Surface, events: list[pygame.event.Event], shift, mouse: tuple[int, int], m_down: bool) -> None:
        """
        Arguments:
        - screen (pygame.Surface) the surface to draw on
        - events (pygame.event.Event) a list of events that happened in the past frame
        - mouse (tuple[int, int]) x, y coords of the mouse
        - m_down (bool) whether the right mouse button has been clicked or not

        This method creates a translucent surface, and draws the dialog elements, updating them as necessary
        """
        # create a translucent surface over the screen
        a = pygame.Surface(screen.get_size())
        a.fill((theme.current.sidebar))
        a.set_alpha(220)
        screen.blit(a, (0, 0))

        # draw the name field and prompt
        screen.blit(self.name_text, (250, 100))
        self.name_field.draw(screen, True, mouse, m_down)

        # draw the submit and close buttons
        self.submit_button.draw(screen, True, mouse, m_down)
        self.close_button.draw(screen, True, mouse, m_down)
        # if the playlist is being edited, draw the delete button
        if self.playlist_id:
            self.delete_button.draw(screen, True, mouse, m_down)

        # if the user has clicked the right mouse button, disable all input fields on the current page (and then draw them regardless)
        # drawing them after disabling all will allow the user to keep active only the field they click on
        if m_down:
            self.name_field.is_active = False
            for s in self.pages[self.page_num]:
                if s.editing_name:
                    s.stop_editing_name()
                if s.editing_artist:
                    s.stop_editing_artist()
                s.draw(screen, True, mouse, m_down)
        else:
            for s in self.pages[self.page_num]:
                s.draw(screen, True, mouse, m_down)
        
        # if there is more than one page, then draw the page navigator underneath the current page songs
        if self.show_pages:
            # allow the next page button to only be active if there is a page to come
            check = True
            if self.page_num == len(self.pages)-1:
                check = False
            self.next_page_button.draw(screen, check, mouse, m_down)
            # allow the previous page button to only be active if there is a page to go bcak to
            check = True
            if self.page_num == 0:
                check = False
            self.prev_page_button.draw(screen, check, mouse, m_down)
            # finally, draw the page text to show what page the user currently is on
            screen.blit(self.page_text, (465, 247+23*self.songspp))
        
        # to update the relevant fields, loop through all events and give the KEYDOWN updates to the relevant fields (can be optimised a little)
        for e in events:
            if e.type == pygame.KEYDOWN:
                if self.name_field.is_active:
                    self.name_field.update_text(e, shift)
                
                for s in self.pages[self.page_num]:
                    if s.editing_name:
                        s.name_field.update_text(e, shift)
                    elif s.editing_artist:
                        s.artist_field.update_text(e, shift)
        return None