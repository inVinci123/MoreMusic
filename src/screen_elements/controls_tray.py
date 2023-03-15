"""
This file contains the controls tray: the lower tray on the default screen that allows the user to
- play/pause
- rewind/skip 10 seconds
- go to next/previous song
- control the volume

all structured in the ControlsTray class

It changes its colours and themes when prompted to in the load_theme function and utilises the module image_editor to generate images if it is unable to find the desired image.
"""

# imports
import pygame

import image_editor
import theme
from classes.button import ImageButton, TextButton
from music_player import MusicPlayer


class ControlsTray:
    """
    Class to organise a structure for the music controls
    """
    def __init__(self, player: MusicPlayer, pos: tuple[float, float] = (100, 100), spacing: int = 60, size: tuple = (30, 30), sound_bar_size=(100, 12)) -> None:
        """
        Arguments:
        - player: (of type MusicPlayer) to execute functions associated with the buttons (e.g. play/pause) [passed by reference]
        - pos: position of the ControlsTray
        - spacing: distance between adjacent elements
        - size: of each button
        - sound_bar_size: max size of the sound bar, the slider to adjust sound
        """

        # assigning some positioning stuff to be used inside the class
        self.pos = pos
        self.size = size
        self.spacing = spacing

        # the music player variable (passed by reference, as it is an object of a class) to access stuff in the class methods
        self.player = player

        # these methods can also be accessed using self.player, however they have been assigned to make it easier to access within the class
        self.pause = player.pause
        self.stop = player.stop
        self.next = player.next
        self.prev = player.prev
        self.mute = player.mute
        self.skip10 = player.skip10
        self.rewind10 = player.rewind10

        # bar size is the length of the sound slider
        self.bar_size = sound_bar_size

        # create a preset sound bar position based on other parameters to use for the sound slider
        self.sound_bar_pos = (self.pos[0]-4.5*self.spacing+45, self.pos[1]+8)

        # total sound is the background rectangle of the sound slider, currrent_sound is the foreground rectangle. Odd names are used to not confuse with other variables existing in other classes.
        self.total_sound = pygame.Rect(self.sound_bar_pos, self.bar_size)
        self.current_sound = pygame.Rect(
            self.sound_bar_pos, (0, self.bar_size[1]))

        # these keep track of whether the mouse is hovering over the sound slider or not.
        self.hover = False
        self.click = False

        # load the theme to initialise other variables
        self.load_theme()
        return None


    def load_theme(self) -> None:
        """
        This method reinitialises the control buttons:
        - loads the necessary colours for the sound slider
        - tries to load the control buttons and position them at their previous positions
        - if they haven't been intialised yet, it positions them at their default positions
        - tries to load in different variations of the play/pause buttons and the sound buttons
        - if those files with the variations are not found, it generates them
        """
        # load the three colours of the background rectangle for the sound slider
        self.bar_norm_col = theme.current.norm_col
        self.bar_hov_col = theme.current.hov_col
        self.bar_click_col = theme.current.click_col

        # the three colours of the foregroud rectangle for the sound slider
        self.done_norm_col = theme.current.progress_norm_col
        self.done_hov_col = theme.current.progress_hov_col
        self.done_click_col = theme.current.progress_click_col

        # default the rectangle colours to normal
        self.bar_colour = self.bar_norm_col
        self.done_colour = self.done_norm_col

        try:
            # try to position the new buttons where they previously were (this runs is the buttons are reinitialising, ie: a new theme has been loaded)
            # the use of ImageButton is described in the file button.py
            self.prev_button = ImageButton(self.prev, "prev.png", f"./Assets_PROG2/Icons/{theme.current_name}_prev.png",
                                           f"./Assets_PROG2/Icons/{theme.current_name}_prev_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_prev_click.png", self.prev_button.pos, self.size)
            self.play_button = ImageButton(self.pause, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png",
                                           f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", self.play_button.pos, self.size)
            self.stop_button = ImageButton(self.stop, "stop.png", f"./Assets_PROG2/Icons/{theme.current_name}_stop.png",
                                           f"./Assets_PROG2/Icons/{theme.current_name}_stop_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_stop_click.png", self.stop_button.pos, self.size)
            self.next_button = ImageButton(self.next, "next.png", f"./Assets_PROG2/Icons/{theme.current_name}_next.png",
                                           f"./Assets_PROG2/Icons/{theme.current_name}_next_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_next_click.png", self.next_button.pos, self.size)
            self.sound_button = ImageButton(self.mute, "soundon.png", f"./Assets_PROG2/Icons/{theme.current_name}_soundon.png",
                                            f"./Assets_PROG2/Icons/{theme.current_name}_soundon_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_soundon_click.png", self.sound_button.pos, self.size)
            self.rewind10_button = TextButton(
                self.rewind10, self.rewind10_button.pos, (0, 0), "-10s", 2)
            self.skip10_button = TextButton(
                self.skip10, self.skip10_button.pos, (0, 0), "+10s", 2)

        except AttributeError:
            # if the buttons weren't initialised, initialise them with the defaults values
            self.prev_button = ImageButton(self.prev, "prev.png", f"./Assets_PROG2/Icons/{theme.current_name}_prev.png", f"./Assets_PROG2/Icons/{theme.current_name}_prev_hov.png",
                                           f"./Assets_PROG2/Icons/{theme.current_name}_prev_click.png", (self.pos[0]+1*self.spacing+12, self.pos[1]), self.size)
            self.play_button = ImageButton(self.pause, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png",
                                           f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", (self.pos[0]+2*self.spacing+12, self.pos[1]), self.size)
            self.stop_button = ImageButton(self.stop, "stop.png", f"./Assets_PROG2/Icons/{theme.current_name}_stop.png", f"./Assets_PROG2/Icons/{theme.current_name}_stop_hov.png",
                                           f"./Assets_PROG2/Icons/{theme.current_name}_stop_click.png", (self.pos[0]+3*self.spacing+12, self.pos[1]), self.size)
            self.next_button = ImageButton(self.next, "next.png", f"./Assets_PROG2/Icons/{theme.current_name}_next.png", f"./Assets_PROG2/Icons/{theme.current_name}_next_hov.png",
                                           f"./Assets_PROG2/Icons/{theme.current_name}_next_click.png", (self.pos[0]+4*self.spacing+12, self.pos[1]), self.size)
            self.sound_button = ImageButton(self.mute, "soundon.png", f"./Assets_PROG2/Icons/{theme.current_name}_soundon.png", f"./Assets_PROG2/Icons/{theme.current_name}_soundon_hov.png",
                                            f"./Assets_PROG2/Icons/{theme.current_name}_soundon_click.png", (self.pos[0]-4.5*self.spacing+12, self.pos[1]), self.size)
            self.rewind10_button = TextButton(
                self.rewind10, (self.pos[0]+0*self.spacing-4, self.pos[1]-3), (0, 0), "-10s", 2)
            self.skip10_button = TextButton(
                self.skip10, (self.pos[0]+5*self.spacing, self.pos[1]-3), (0, 0), "+10s", 2)

        # try loading the different variations (normal, hover, click) of the buttons based on the current theme
        try:
            # try loading the normal image
            self.play_image = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current_name}_play.png")
        except FileNotFoundError:
            # if the file doesn't exist, make it
            # the use of this method is described in the image_editor module, refer to it.
            self.play_image = image_editor.change_colour(
                "Assets_PROG2/Icons/default_play.png", theme.current.norm_col, f"Assets_PROG2/Icons/{theme.current_name}_play.png")
        try:
            # try loading the hover image
            self.play_image_hov = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current.hov_col}_play_hov.png")
        except FileNotFoundError:
            # generate it if it doesn't exist
            self.play_image_hov = image_editor.change_colour(
                "Assets_PROG2/Icons/default_play.png", theme.current.hov_col, f"Assets_PROG2/Icons/{theme.current_name}_play_hov.png")
        try:
            # try loading the click image
            self.play_image_click = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current.click_col}_play_click.png")
        except FileNotFoundError:
            # make it if it doesn't exist
            self.play_image_click = image_editor.change_colour(
                "Assets_PROG2/Icons/default_play.png", theme.current.click_col, f"Assets_PROG2/Icons/{theme.current_name}_play_click.png")
        
        # load variations (normal, hover, click) for the pause images
        try:
            # try load the normal image
            self.pause_image = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current_name}_pause.png")
        except FileNotFoundError:
            # generate it if it doesn't exist
            self.pause_image = image_editor.change_colour(
                "Assets_PROG2/Icons/default_pause.png", theme.current.norm_col, f"Assets_PROG2/Icons/{theme.current_name}_pause.png")
        try:
            # try loading the hover image
            self.pause_image_hov = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current_name}_pause_hov.png")
        except FileNotFoundError:
            # generate it if it doesn't exist
            self.pause_image_hov = image_editor.change_colour(
                "Assets_PROG2/Icons/default_pause.png", theme.current.hov_col, f"Assets_PROG2/Icons/{theme.current_name}_pause_hov.png")
        try:
            # try loading the click image
            self.pause_image_click = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current_name}_pause_click.png")
        except FileNotFoundError:
            # generate it if it doesn't exist
            self.pause_image_click = image_editor.change_colour(
                "Assets_PROG2/Icons/default_pause.png", theme.current.click_col, f"Assets_PROG2/Icons/{theme.current_name}_pause_click.png")
        
        # now load the soundon and soundoff images
        try:
            # try loading the normal image
            self.soundon_image = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current_name}_soundon.png")
        except FileNotFoundError:
            # generate it if it doesn't exist
            self.soundon_image = image_editor.change_colour(
                "Assets_PROG2/Icons/default_soundon.png", theme.current.norm_col, f"Assets_PROG2/Icons/{theme.current_name}_soundon.png")
        try:
            # try loading the hover image
            self.soundon_image_hov = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current.hov_col}_soundon_hov.png")
        except FileNotFoundError:
            # generate it if it doesn't exist
            self.soundon_image_hov = image_editor.change_colour(
                "Assets_PROG2/Icons/default_soundon.png", theme.current.hov_col, f"Assets_PROG2/Icons/{theme.current_name}_soundon_hov.png")
        try:
            # try loading the click image
            self.soundon_image_click = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current.click_col}_soundon_click.png")
        except FileNotFoundError:
            # generate it if it doesn't exist
            self.soundon_image_click = image_editor.change_colour(
                "Assets_PROG2/Icons/default_soundon.png", theme.current.click_col, f"Assets_PROG2/Icons/{theme.current_name}_soundon_click.png")
        # soundoff images
        try:
            # try loading the normal image
            self.soundoff_image = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current_name}_soundoff.png")
        except FileNotFoundError:
            # generate it if it doesn't exist
            self.soundoff_image = image_editor.change_colour(
                "Assets_PROG2/Icons/default_soundoff.png", theme.current.norm_col, f"Assets_PROG2/Icons/{theme.current_name}_soundoff.png")
        try:
            # try loading the hover image
            self.soundoff_image_hov = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current.hov_col}_soundoff_hov.png")
        except FileNotFoundError:
            # generate it if it doesn't exist
            self.soundoff_image_hov = image_editor.change_colour(
                "Assets_PROG2/Icons/default_soundoff.png", theme.current.hov_col, f"Assets_PROG2/Icons/{theme.current_name}_soundoff_hov.png")
        try:
            # try loading the click image
            self.soundoff_image_click = pygame.image.load(
                f"Assets_PROG2/Icons/{theme.current.click_col}_soundoff_click.png")
        except FileNotFoundError:
            # generate it if it doesn't exist
            self.soundoff_image_click = image_editor.change_colour(
                "Assets_PROG2/Icons/default_soundoff.png", theme.current.click_col, f"Assets_PROG2/Icons/{theme.current_name}_soundoff_click.png")
        
        return None


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
            return None
        if mouse[0] > self.sound_bar_pos[0] and mouse[0] < self.sound_bar_pos[0]+self.bar_size[0] and mouse[1] > self.sound_bar_pos[1] and mouse[1] < self.sound_bar_pos[1]+self.bar_size[1]:
            # if the mouse is within the bounds and not clicking, well that is called hover.
            self.hover = True
            # reflect this in the colour of the sound slider
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
                # set the colours to normal again
                self.bar_colour = self.bar_hov_col
                self.done_colour = self.done_hov_col
                # find out the normalised (a decimal value out of 1) value of where the user clicked on the slider
                val = (mouse[0]-self.sound_bar_pos[0])/self.bar_size[0]
                # set the volume accordingly
                self.player.set_volume(val)
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
    

    def draw(self, screen: pygame.Surface, check: bool, mouse: tuple[int, int], m_down: bool) -> None:
        """
        Arguments:
        - screen: the pygame surface to draw the elements on [passed by reference]
        - check: a boolean indicating whether the elements should check for hover and clicks or not
        - mouse: a tuple with the x, y coords of the mouse on the screen.
        - m_down: a bool indicating whether the user is right clicking or not

        This method draws the screen elements of the controls tray:
        - if check is enabled, checks for hover and click on the sound slider before updating the value of the sound slider
        - updates the play/pause button and sound button based on whether the music player is paused/muted or not
        - draws the individual buttons and the sound slider
        """
        if check:
            # check for hover/click if it is supposed to
            self.check_hover(mouse, m_down)
            self.check_click(mouse, m_down)
        
        # update the width of the slider's fg rectange relative to the bg based on the current volume
        self.current_sound.width = int(
            self.player.volume*self.total_sound.width)

        if self.player.paused:
            # use the play images (prompting the user to play) if the music is paused
            self.play_button.norm_img = self.play_image
            self.play_button.hov_img = self.play_image_hov
            self.play_button.click_img = self.play_image_click
        else:
            # else use the pause images if the music is playing
            self.play_button.norm_img = self.pause_image
            self.play_button.hov_img = self.pause_image_hov
            self.play_button.click_img = self.pause_image_click

        if self.player.muted:
            # indicate the sound is muted if it is
            self.sound_button.norm_img = self.soundoff_image
            self.sound_button.hov_img = self.soundoff_image_hov
            self.sound_button.click_img = self.soundoff_image_click
        else:
            # else indicate the sound is on
            self.sound_button.norm_img = self.soundon_image
            self.sound_button.hov_img = self.soundon_image_hov
            self.sound_button.click_img = self.soundon_image_click

        # draw the sound slider rectangles
        pygame.draw.rect(screen, self.bar_colour, self.total_sound)
        pygame.draw.rect(screen, self.done_colour, self.current_sound)

        # draw the rest of the control elements
        self.play_button.draw(screen, True, mouse, m_down)
        self.stop_button.draw(screen, check, mouse, m_down)
        self.next_button.draw(screen, check, mouse, m_down)
        self.prev_button.draw(screen, check, mouse, m_down)
        self.skip10_button.draw(screen, check, mouse, m_down)
        self.rewind10_button.draw(screen, check, mouse, m_down)
        self.sound_button.draw(screen, check, mouse, m_down)

        return None
    

    def shift(self, val: float) -> None:
        """
        Arguments:
        - val: a float indicating how much the screen elements are shifted

        This function edits the position of the screen elements when prompted to shift:
        - shifts most elements by half the value to keep the controls tray at the centre
        - shifts the sound slider by a specific amount to keep it in the view.
        """
        # shift most elements by half the prompted value on the x to maintain their centre
        self.prev_button.pos = (self.prev_button.pos[0]+val/2, self.prev_button.pos[1])
        self.next_button.pos = (self.next_button.pos[0]+val/2, self.next_button.pos[1])
        self.play_button.pos = (self.play_button.pos[0]+val/2, self.play_button.pos[1])
        self.stop_button.pos = (self.stop_button.pos[0]+val/2, self.stop_button.pos[1])
        self.skip10_button.pos = (self.skip10_button.pos[0]+val/2, self.skip10_button.pos[1])
        self.rewind10_button.pos = (self.rewind10_button.pos[0]+val/2, self.skip10_button.pos[1])

        # shift the sound slider and sound icon by 7/10 of the value to keep them in sight (a work around for another feature to exist)
        self.sound_button.pos = (self.sound_button.pos[0]+7*val/10, self.sound_button.pos[1])
        self.sound_bar_pos = (self.sound_bar_pos[0]+7*val/10, self.sound_bar_pos[1])
        self.total_sound = pygame.Rect(self.sound_bar_pos, self.bar_size)
        self.current_sound = pygame.Rect(self.sound_bar_pos, (0, self.bar_size[1]))
        
        return None
