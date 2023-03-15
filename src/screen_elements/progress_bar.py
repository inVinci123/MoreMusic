"""
This file holds the progress bar class, which shows the progress of the song
"""
# imports
import pygame

import theme
from music_player import MusicPlayer

# init pygame and import a small sized font
pygame.init()
font = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Thin.ttf", 16)

class ProgressBar:
    def __init__(self, player: MusicPlayer, pos: tuple, size: tuple, on_click) -> None:
        """
        Arguments:
        - player (MusicPlayer) Music Player to execute functions and access information from [passed by reference]
        - pos (tuple[int, int]) the position of the progress bar
        - size (tuple[int, int]) the size of the progress bar
        - on_click (function) the function to execute when the progress bar is clicked
        """
        # initialise variables for the background bar and the foreground done bit
        self.bar = pygame.Rect(pos, size)
        self.done = pygame.Rect(pos, (0, size[1]))

        # make pos and size available to the class
        self.pos = pos
        self.size = size

        # time stamps for elapsed and remaining
        self.elapsed = font.render("0:00", True,  (240, 240, 240))
        self.remaining = font.render("0:00", True,  (240, 240, 240))

        # to access information and execute functions
        self.player: MusicPlayer = player

        # initialise the colours with the theme
        self.bar_norm_col = theme.current.norm_col
        self.bar_hov_col = theme.current.hov_col
        self.bar_click_col = theme.current.click_col
        self.done_norm_col = theme.current.progress_norm_col
        self.done_hov_col = theme.current.progress_hov_col
        self.done_click_col = theme.current.progress_click_col

        # default with the normal colours
        self.bar_colour = self.bar_norm_col
        self.done_colour = self.done_norm_col

        # to keep track of whether the user is hovering/has clicked
        self.hover = False
        self.click = False

        # to execute when the click is complete
        self.on_click = on_click
        return None
    
    
    def draw(self, screen: pygame.Surface, check: bool, mouse, m_down) -> None:
        """
        Arguments:
        - screen: the pygame surface to draw the elements on [passed by reference]
        - check: a boolean indicating whether the elements should check for hover and clicks or not
        - mouse: a tuple with the x, y coords of the mouse on the screen.
        - m_down: a bool indicating whether the user is right clicking or not

        Evaluate the position and draw the progress bar on the screen
        """
        # get progress from the music player
        progress = self.player.get_progress()
        if progress > 0.9999:
            # go to the next song if it is about to end
            self.player.next()
        if progress < 0:
            # go to the previous song if it somehow went beyond
            self.player.prev()
        # calculate the time elapsed and remaining
        elapsed = int(self.player.start_time+self.player.length_done)
        remaining = int(self.player.song_length - elapsed)

        self.done.width = int(progress*self.bar.width)
        if check:
            # check for hover/click if allowed to
            self.check_hover(mouse, m_down)
            self.check_click(mouse, m_down)
        else:
            # else default it to nothing
            self.bar_colour = self.bar_norm_col
            self.done_colour = self.done_norm_col
            self.done.width = 0
            elapsed = 0
            remaining = 0
        
        # draw the foreground and backgroud rectangles for the progress bar
        pygame.draw.rect(screen, self.bar_colour, self.bar)
        pygame.draw.rect(screen, self.done_colour, self.done)

        # render the timestamps and draw them
        self.elapsed = font.render(f"{elapsed//60}:{'0' if elapsed%60 < 10 else ''}{elapsed%60}", True,  theme.current.norm_col)
        self.remaining = font.render(f"{remaining//60}:{'0' if remaining%60 < 10 else ''}{remaining%60}", True,  theme.current.norm_col)
        screen.blit(self.elapsed, (self.pos[0], self.pos[1]+12))
        screen.blit(self.remaining, (self.pos[0]+self.size[0]-30, self.pos[1]+12))
        return None
    
    
    def load_theme(self) -> None:
        """
        Reinitialise the current theme on the progress bar colours
        """
        self.bar_norm_col = theme.current.norm_col
        self.bar_hov_col = theme.current.hov_col
        self.bar_click_col = theme.current.click_col
        self.done_norm_col = theme.current.progress_norm_col
        self.done_hov_col = theme.current.progress_hov_col
        self.done_click_col = theme.current.progress_click_col
        return None
        

    def check_hover(self, mouse: tuple[int, int], m_down: bool) -> None:
        """
        Arguments:
        - mouse: tuple with the x, y coords of the mouse
        - m_down: bool showing whether the user is right-clicking or not

        This method checks whether the user is hovering the progress bar:
        - returns None if it the user is clicking the mouse
        - if not, then it checks whether the mouse position is 
        """
        if self.click or m_down:
            # return immediately if the user is clicking, as that cancels the hover
            return
        if mouse[0] > self.pos[0] and mouse[0] < self.pos[0]+self.size[0] and mouse[1] > self.pos[1] and mouse[1] < self.pos[1]+self.size[1]:
            # if the mouse is within the bounds and not clicking, it is hovering
            self.hover = True
            self.bar_colour = self.bar_hov_col
            self.done_colour = self.done_hov_col
        else:
            # else the user is not hovering or clicking, so let it be normal
            self.bar_colour = self.bar_norm_col
            self.done_colour = self.done_norm_col
            self.hover = False
        return None
    
    
    def check_click(self, mouse: tuple[int, int], m_down: bool) -> None:
        """
        Arguments:
        - mouse: tuple with the x, y coords of the mouse
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
                # set the colours to hover again
                self.bar_colour = self.bar_hov_col
                self.done_colour = self.done_hov_col
                # find what time to play at
                play_time = (mouse[0]-self.pos[0])/self.size[0]
                # play at that time
                self.on_click(play_time)
            elif not self.hover:
                # stop the click and hover if the click is incomplete and the user stopped hovering
                self.hover = False
                self.click = False
                self.bar_colour = self.bar_norm_col
                self.done_colour = self.done_norm_col
        # if the user wasn't already hovering and had their mouse down, check if they are now
        elif m_down and self.hover:
            self.click = True
            self.bar_colour = self.bar_click_col
            self.done_colour = self.done_click_col
        return None
    
    
    def shift(self, val: int) -> None:
        """
        Arguments:
        - val (int) the value to shift the playlist view by

        Shifts all elements of this class by `val` on the x axis
        """
        # update the size of the progress bar (to keep it from going out of sight)
        self.size = (self.size[0]-val, self.size[1])
        self.bar.size = self.size

        # shift the position of the progress bar
        self.pos = (self.pos[0]+val, self.pos[1])
        self.bar.topleft = self.pos
        self.done.topleft = self.pos
        return None
        