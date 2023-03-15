"""
This class holds classes essential for:
- displaying the current playlist
- playing specific songs from the current playlist
"""
# imports
import pygame
import math

import theme
from music_player import MusicPlayer
from classes.playlist import Playlist
from classes.button import ImageButton

# initialise pygame and create some fonts
pygame.init()
title = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Bold.ttf", 40)
subtitle = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Medium.ttf", 30)
small = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Thin.ttf", 20)


class SongTile:
    """
    A class to blueprint each SongTile in the PlaylistView, containing the title and the artist
    """
    def __init__(self, pos: tuple[float, float], title: str = "Hello", artist: str = "World", on_click = None, height: int = 60, length: int = 400, song_id: int = 0) -> None:
        """
        Arguments:
        - pos: (tuple[float, float]) the position of the SongTile
        - title: (str) the song name
        - artist: (str) the artist name
        - on_click: (function) to be executed if the tile is clicked
        - height: (int) the height of the song tile
        - length: (int) the length of the song tile
        - song_id: (int) the position of the song relative to the playlist
        """
        # initialise the song info to make it available within the class
        self.title = title
        self.artist = artist

        # initialise more info to make it available to the class
        self.on_click = on_click
        self.pos = pos
        self.size = (length, height)

        # to keep track on whether the user is hovering/has clicked them
        self.hover: bool = False
        self.click: bool = False
        
        # the text colour of the class
        self.colour = theme.current.norm_col
        self.song_id = song_id # make the song_id available to play the song when clicked
        return None
    
    
    def get_tile(self) -> pygame.Surface:
        """
        returns the tile to be drawn as a surface
        """
        # create the surface to be returned
        a = pygame.Surface(self.size)
        a.fill(theme.current.bg)
        # renderthe artist and title on the surface
        a.blit(subtitle.render(self.title, True, self.colour), (5, 0))
        a.blit(small.render(self.artist, True, self.colour), (5, 35))
        # create a divider at the bottom
        pygame.draw.line(a, theme.current.norm_col, (5, self.size[1]-2), (self.size[0]-5, self.size[1]-2))
        return a
    

    def check_hover(self, mouse: tuple[int, int], m_down: bool) -> None:
        """
        Arguments:
        - mouse: tuple with the x, y coords of the mouse
        - m_down: bool showing whether the user is right-clicking or not

        This method checks whether the user is hovering the sound slider:
        - returns None if it the user is clicking the mouse
        - if not, then it checks whether the mouse position is 
        """
        if self.click or m_down:
            # return if the user is clicking, as that cancels the hover
            return
        if mouse[0] > self.pos[0] and mouse[0] < self.pos[0]+self.size[0] and mouse[1] > self.pos[1] and mouse[1] < self.pos[1]+self.size[1]:
            # if the mouse is within the bounds and not clicking, well that is called hover.
            self.hover = True
            # reflect this in the colour of the text
            self.colour = theme.current.hov_col
        else:
            # else the user is not hovering or clicking, so let it be normal
            self.colour = theme.current.norm_col
            self.hover = False
        return None
    
    
    def check_click(self, m_down: bool):
        """
        Arguments:
        - m_down: bool showing whether the user is right-clicking or not

        This method checks whether the user is clicking on the button and executes a relevant function:
        - checks if self.click is true (i.e. rightclicked and mouse is hovering)
        - if so then checks if the user has lifted the click to complete the click
        - if so it executes the relevant function
        - else if the user is no longer hovering over the clickable element, cancel the self.click and reset to normal
        - if self.click is not true, then check if self.click should be true (so it can check if the click is completed in the next frame)
        """
        if self.click:
            # the user was already hovering and had their mouse down
            if not m_down and self.hover:
                # if the mouse has been lifted, the click is complete
                self.click = False
                # set the colours to normal aga
                self.colour = theme.current.hov_col
                # execute the functoin (if it exists)
                if self.on_click:
                    self.on_click(self.song_id)
            elif not self.hover:
                # stop the click and hover if the click is incomplete and the user stopped hovering
                self.hover = False
                self.click = False
                self.colour = theme.current.norm_col
        # if the user wasn't already hovering and had their mouse down, check if they are now
        elif m_down and self.hover:
            self.click = True
            self.colour = theme.current.click_col
        return None
    
    def update_colours(self) -> None:
        """Update the colours in accordance with the theme"""
        self.colour = theme.current.norm_col
        return None
    

def create_pages(song_list, songspp: int) -> list:
    """
    Arguments:
    - song_list: (list) list of the objects to be put into pages
    - songspp: (int) amount of songs per page
    """
    # establish the number count of pages
    count = math.ceil(len(song_list)/songspp)
    pages = []
    # append the pages by slicing the list accordingly
    for p in range(count):
        pages.append(song_list[p*songspp:(p+1)*songspp])
    return pages


class PlaylistView:
    """
    A class to structure the songs in the current playlist
    """
    def __init__(self, pos: tuple[int, int], playlist: Playlist, player: MusicPlayer, length: int = 400) -> None:
        """
        Arguments:
        - pos (tuple[int, int]) the top left position of the playlist view
        - playlist (Playlist) the playlist object to be displayed [passed by reference]
        - player (MusicPlayer) to access the playlist info and execute some functions [passed by reference]
        - length (int) for length of SongTiles in the PlaylistView
        """
        # intialise values
        self.player = player
        self.length = length
        self.pos = pos
        self.title = title.render(playlist.name, True, theme.current.norm_col)
        self.songs: list[SongTile] = []

        # initialise page stuff
        self.pages: list[list[SongTile]] = []
        self.songspp = 5 # songs per page
        self.page_num = 0
        self.page_text = small.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        self.show_pages: bool = False

        # page navigation buttons
        self.next_page_button = ImageButton(self.next_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", ((self.pos[0]+self.length)/2+45, self.pos[1]+120+60*self.songspp), (10, 10))
        self.prev_page_button = ImageButton(self.prev_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", ((self.pos[0]+self.length)/2-55, self.pos[1]+120+60*self.songspp), (10, 10), flip=True)
        self.prev_page_button.image = self.prev_page_button.hov_img
        self.next_page_button.image = self.next_page_button.hov_img
        
        # load the playlist
        self.load_playlist()
        return None
    
    
    def load_theme(self) -> None:
        """
        Reinitialise values/update their colours to match the theme
        """
        # reinitialise page stuff
        self.next_page_button = ImageButton(self.next_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", ((self.pos[0]+self.length)/2+55, self.pos[1]+120+60*self.songspp), (10, 10))
        self.prev_page_button = ImageButton(self.prev_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", ((self.pos[0]+self.length)/2-55, self.pos[1]+120+60*self.songspp), (10, 10), flip=True)
        self.page_text = small.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        # update the title and song tiles
        self.title = title.render(self.player.current_playlist.name, True, theme.current.norm_col)
        for p in self.pages:
            for tile in p:
                tile.update_colours()
        return None
    

    def load_playlist(self) -> None:
        """
        Load the current playlist from the MusicPlayer
        """
        # change the title
        self.title = title.render(self.player.current_playlist.name, True, theme.current.norm_col)
        # clear and add the new songs
        self.songs.clear()
        for i, song in enumerate(self.player.current_playlist.songs):
            self.songs.append(SongTile((self.pos[0], self.pos[1]+50+60*i), song.name, artist=song.artist, on_click=self.player.play, length=self.length, song_id=i))
        
        # clear and initalise pages
        self.pages.clear()
        self.pages = create_pages(self.songs, self.songspp)
        self.page_num = 0
        self.page_text = small.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        self.prev_page_button.image = self.prev_page_button.hov_img
        self.next_page_button.image = self.next_page_button.hov_img
        self.show_pages = len(self.pages)>1 # only show pages if there's more than one
        return None
    
    
    def next_page(self) -> None:
        """
        Move to the next page if possible
        """
        if self.page_num < len(self.pages):
            self.page_num += 1
            self.page_text = small.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        return None
    

    def prev_page(self) -> None:
        """
        Move to the previous page if possible
        """
        if self.page_num > 0:
            self.page_num -= 1
            self.page_text = small.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        return None


    def draw(self, screen: pygame.Surface, mouse: tuple[int, int], r_click: bool, check: bool) -> None:
        """
        Arguments:
        - screen: the pygame surface to draw the elements on [passed by reference]
        - check: a boolean indicating whether the elements should check for hover and clicks or not
        - mouse: a tuple with the x, y coords of the mouse on the screen.
        - m_down: a bool indicating whether the user is right clicking or not

        Render the title and songs and check for hover/clicks if allowed, render the page navigator if there's more than one
        """
        # render the playlist title
        screen.blit(self.title, (self.pos[0], self.pos[1]+20))
        # render each tile on the current page and check if they work
        for i, tile in enumerate(self.pages[self.page_num]):
            # update the tile's position before rendering it
            tile.pos = self.pos[0], self.pos[1]+100+60*i
            screen.blit(tile.get_tile(), tile.pos)
            if check:
                # only check for hover/click if allowed
                tile.check_hover(mouse, r_click)
                tile.check_click(r_click)
        
        if self.show_pages: # only show the page navigator if there's more than 1 page
            # leave the next page button inactive if there is no next page to go to
            check = True
            if self.page_num == len(self.pages)-1:
                check = False
            self.next_page_button.draw(screen, check, mouse, r_click)
            # leave the previous page button inactive if there is no previous page to go to
            check = True
            if self.page_num == 0:
                check = False
            self.prev_page_button.draw(screen, check, mouse, r_click)
            screen.blit(self.page_text, ((self.pos[0]+self.length)/2-42, self.pos[1]+116+60*self.songspp))
        return None
    
    
    def shift(self, val: int) -> None:
        """
        Arguments:
        - val (int) the value to shift the playlist view by

        Shifts all elements of this class by `val` on the x axis
        """
        # update the structure position
        self.pos = (self.pos[0]+val, self.pos[1])
        # update position of each song tile
        for s in self.songs:
            s.pos = (s.pos[0]+val, s.pos[1])
        # update the posiiton of the page buttons
        self.prev_page_button.pos = (self.prev_page_button.pos[0]+val/2, self.prev_page_button.pos[1])
        self.next_page_button.pos = (self.next_page_button.pos[0]+val/2, self.next_page_button.pos[1])
        return None
