"""
This file holds the Sidebar class
"""

# imports
import pygame

import theme
from classes.button import TextButton, ImageButton
from screen_elements.playlist_view import create_pages

# initialise pygame and create a font
pygame.init()
small = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Thin.ttf", 16)

# get a function to pass as an argument in a for loop (the functions requiring arguments of the for loop elements behave weirdly, so this is a work around)
def get_on_click(func, argument) -> object:
    return lambda: func(argument)

class Sidebar:
    def __init__(self, dimensions: tuple[float, float], location: tuple[float, float], title: str, options: list[tuple[str, object]], anim_dir: int = 1, overlay:bool = True, shift = None, edit_pl=None, ids = None) -> None:
        """
        Arguments:
        - dimensions: (tuple[int, int]) the size of the sidebar
        - location: (tuple[int, int]) the location of the sidebar
        - title: (str) the header
        - options: (list[tuple[str, function]]) the list of options in the sidebar
            - str is the text of the button
            - function is the onclick
        - anim_dir: (int) what direction it opens in (1 for open to the left, -1 for open to the right)
        - overlay: (bool) create a translucent surface before rendering the sidebar or not
        - shift: (function) function to shift screen elements (used for one of the sidebars)
        - edit_pl: (function) function to open a playlist for editing (done by the trailing icon in the Options)
        - ids: (list) a list of the ids of the playlists (to pass into the edit_pl function)

        Note:
        There are two types of sidebars generally used, with distinctive directions
        - the playlistbar has anim_dir -1, so whenever it is referred to, anim_dir is checked to be -1
        - the themebar has anim_dir 1, so whenever it is referred to, anm_dir is checked to be 1
        """
        # initialise it as closed
        self.is_open = False
        # make some arguments available to the class
        self.dimensions = dimensions
        self.location = location
        self.edit_pl = edit_pl
        self.ids = ids
        self.title = TextButton(lambda : None, (location[0]+20, location[1]+10), (1, -1), title, text_size=3) # title/header of the sidebar
        
        # options is a list of the options in the side bar
        self.options: list[TextButton] = []
        if anim_dir == -1: # if it is a playlistbar
            for i, opt in enumerate(options): # the options will have a trailing Image Button that allows users to edit the playlist
                self.options.append(TextButton(opt[1], (location[0]+20, location[1]+70+i*40), (dimensions[0]-20, 40), opt[0], text_size=2, trailing=ImageButton(get_on_click(edit_pl, ids[i]), "edit.png", f"./Assets_PROG2/Icons/{theme.current_name}_edit.png", f"./Assets_PROG2/Icons/{theme.current_name}_edit_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_edit_click.png", (location[0]+dimensions[0]-30, location[1]+70+i*40+7), (20, 20)))) # type: ignore
        else: # if it is a themebar
            for i, opt in enumerate(options): # theoptions will be normal
                self.options.append(TextButton(opt[1], (location[0]+20, location[1]+70+i*40), (dimensions[0]-20, 40), opt[0], text_size=2))
        
        # initialie some animation variables
        self.animate = False
        self.anim_delta = 0
        self.anim_speed = 0.1
        self.opening = False
        self.closing = False
        self.anim_dir = anim_dir
        self.moved = 0

        self.shift = shift # function to shift the screen elements
        self.overlay = overlay # bool indicating whether or not to have a translucent screen below the bar

        # initialise page variables
        self.pages: list[list[TextButton]] = []
        self.optionspp = 15 # options per page
        self.pages = create_pages(self.options, self.optionspp) # create pages is defined in playlist view
        self.page_num = 0

        # page navigator stuff
        self.next_page_button = ImageButton(self.next_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", (self.location[0]+(self.dimensions[0])/2+35, self.location[1]+75+40*self.optionspp), (10, 10))
        self.prev_page_button = ImageButton(self.prev_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", (self.location[0]+(self.dimensions[0])/2-45, self.location[1]+75+40*self.optionspp), (10, 10), flip=True)
        self.prev_page_button.image = self.prev_page_button.hov_img
        self.next_page_button.image = self.next_page_button.hov_img
        self.page_text = small.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        
        self.show_pages: bool = False
        
        # more page variables
        self.prev_page_button.image = self.prev_page_button.hov_img
        self.next_page_button.image = self.next_page_button.hov_img
        self.show_pages = len(self.pages)>1
        self.page_num = 0

        return None
    

    def next_page(self) -> None:
        """ Go to the next page if possible and update the page number"""
        if self.page_num < len(self.pages):
            self.page_num += 1
            self.page_text = small.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        return None
    

    def prev_page(self) -> None:
        """ Go to the previous pagei s possible and update the page number """
        if self.page_num > 0:
            self.page_num -= 1
            self.page_text = small.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        return None
    

    def open(self) -> None:
        """ Open the sidebar and start the animation """
        self.is_open = True
        self.opening = True
        self.anim_delta = self.anim_dir*self.dimensions[0]
        return None
    
    
    def close(self) -> None:
        """ Reset the animation delta (where to move to) and start the closing animation"""
        self.closing = True
        self.anim_delta = 0
        return None
    
    
    def load_theme(self) -> None:
        """ update the options (reinitalise the trailing icons if necessary) and reinitialies other variables to load the new theme """
        if self.anim_dir == -1: # if it is a playlist bar, the trailing icons also need to be reinitialised
            for i, opt in enumerate(self.options):
                opt.update_colors()
                opt.trailing = ImageButton(get_on_click(self.edit_pl, self.ids[i]), "edit.png", f"./Assets_PROG2/Icons/{theme.current_name}_edit.png", f"./Assets_PROG2/Icons/{theme.current_name}_edit_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_edit_click.png", (self.location[0]+self.dimensions[0]-30, self.location[1]+70+i*40+7), (20, 20)) # type: ignore
        else: # else just do the options (TextButtons)
            for opt in self.options:
                opt.update_colors()
        
        # reinit page navigator stuff
        self.next_page_button = ImageButton(self.next_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", (self.location[0]+(self.dimensions[0])/2+35, self.location[1]+75+40*self.optionspp), (10, 10))
        self.prev_page_button = ImageButton(self.prev_page, "play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_play_click.png", (self.location[0]+(self.dimensions[0])/2-45, self.location[1]+75+40*self.optionspp), (10, 10), flip=True)
        self.page_text = small.render(f"Page {self.page_num+1}/{len(self.pages)}", True, theme.current.norm_col)
        # finish it with a titular update
        self.title.update_colors()
        return None
    

    def add_option(self, option: tuple[str, object]) -> None:
        """
        Arguments:
        option: TextButton (tuple[str, function])
            - str refers to what the text is in the option
            - function is what to call when the option is clicked
        
        This method is usually passed to the playlist dialog to create a new playlist
        """
        self.options.append(TextButton(option[1], (self.location[0]+20, self.location[1]+70+(len(self.options)-1)*40), (0, 0), option[0], 2))
        self.pages = create_pages(self.options, self.optionspp)
        return None
    

    def draw(self, screen: pygame.Surface, mouse: tuple[int, int], m_down: bool, check: bool = True) -> None:
        """
        Arguments:
        - screen: the pygame surface to draw the elements on [passed by reference]
        - check: a boolean indicating whether the elements should check for hover and clicks or not
        - mouse: a tuple with the x, y coords of the mouse on the screen.
        - m_down: a bool indicating whether the user is right clicking or not

        This method draws the screen elements of the sidebar, animates them if necessary and checks for relevant hover/clicking in the options
        """
        if self.is_open: # only draw it if it is open
            if self.overlay: # if overlay is enabled
                # draw a layer of less transparency
                opaque = pygame.Surface(screen.get_size())
                opaque.fill((50, 50, 50))
                opaque.set_alpha(153)
                screen.blit(opaque, (0, 0))

            if self.opening: # if the opening animation is on
                # move it by a constant amount every frame
                self.moved = self.dimensions[0]*self.anim_speed
                # change the amount remaining
                self.anim_delta -= self.moved*self.anim_dir
                if self.shift: # if shift is given as a function (happens only in the playlist bar), shift the screen elements by the amount the side bar was moved
                    self.shift(self.moved)
                if self.anim_dir*self.anim_delta < 1: # check if the opening animation is complete
                    self.anim_delta = 0
                    self.opening = False
            if self.closing: # if the closing animation is on
                # move it by a constant amount every frame
                self.moved = self.dimensions[0]*self.anim_speed
                # change the amount remaining
                self.anim_delta += self.moved*self.anim_dir
                if self.shift:# if shift is given as a function (happens only in the playlist bar), shift the screen elements by the amount the side bar was moved
                    self.shift(-self.moved)
                if self.anim_dir*self.anim_delta > self.dimensions[0]-1: # check if the opening animation is complete
                    self.anim_delta = 0
                    self.closing = False
                    self.is_open = False
                    return None # leave is method as the sidebar is on longer open, meaning no point of drawing anything anymore
            
            # create the sidebar rectangle/bottom surface and render that on the screen could (could've also used rect)
            a = pygame.Surface(self.dimensions)
            a.fill(theme.current.sidebar)
            a.set_alpha(255)
            screen.blit(a, (self.location[0]+self.anim_delta, self.location[1]))
            
            # render all the options on the current page
            for i, opt in enumerate(self.pages[self.page_num]):
                opt.pos = (opt.pos[0], self.location[1]+70+i*40)
                if not self.opening and not self.closing and check:
                    # draw the options normally and check them if no animation is playing and check is True
                    opt.draw(screen, check, mouse, m_down)
                else:
                    # else show them with an inactive colour and render their text
                    opt.colour = opt.hov_col
                    screen.blit(opt.get_text(), (opt.pos[0]+self.anim_delta, opt.pos[1]))
            # finally, render the title
            screen.blit(self.title.get_text(), (self.title.pos[0]+self.anim_delta, self.title.pos[1]))

            # if there's more than one page and it's not animating
            if self.show_pages and not self.opening and not self.closing:
                # draw the next page button as active if there is a next page, else inactive
                check = True
                if self.page_num == len(self.pages)-1:
                    check = False
                self.next_page_button.draw(screen, check, mouse, m_down)
                # draw the previous page button as active if there is a previous page, else inactive
                check = True
                if self.page_num == 0:
                    check = False
                self.prev_page_button.draw(screen, check, mouse, m_down)
                # draw the page text
                screen.blit(self.page_text, (self.location[0]+(self.dimensions[0])/2-32, self.location[1]+73+40*self.optionspp))
        return None

