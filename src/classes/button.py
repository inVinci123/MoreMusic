"""
This file contains the base button class, which is inherited by the ImageButton and the TextButton to display their relevant content.
"""
# imports
import pygame

import theme
import image_editor

class Button:
    def __init__(self, on_click, position: tuple, size: tuple) -> None:
        """
        Arguments:
        - on_click: (function) to execute when clicked
        - position: (tuple[int, int]) position of the button
        - size: (tuple[int, int]) size of the button
        """
        # initialise the arguments to make them available in the class
        self.on_click = on_click
        self.pos = position
        self.size = size
        # define colours based on the theme
        self.colour = theme.current.norm_col
        self.norm_col = theme.current.norm_col
        self.hov_col = theme.current.hov_col
        self.click_col = theme.current.click_col
        # initalise booleans to keep track of whether the user is hovering over/clicking the button
        self.click = False
        self.hover = False
        return None
    
    
    def get_rect(self) -> pygame.Rect:
        """returns the rect of the button"""
        return pygame.Rect(self.pos, self.size)
    

    def check_hover(self, mouse: tuple, m_down: bool) -> None:
        """
        Arguments:
        - mouse: tuple with the x, y coords of the mouse
        - m_down: bool showing whether the user is right-clicking or not

        This method checks whether the user is hovering the button:
        - returns None if it the user is clicking the mouse
        - if not, then it checks whether the mouse position is 
        """
        if self.click or m_down:
            # return immediately if the user is clicking, as that cancels the hover
            return
        if mouse[0] > self.pos[0] and mouse[0] < self.pos[0]+self.size[0] and mouse[1] > self.pos[1] and mouse[1] < self.pos[1]+self.size[1]:
            # if the mouse is within the bounds and not clicking, it is hovering
            self.hover = True
            self.colour = self.hov_col
        else:
            # else the user is not hovering or clicking, so let it be normal
            self.colour = self.norm_col
            self.hover = False
        return None
    
    def check_click(self, m_down) -> None:
        """
        Arguments
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
                self.colour = self.hov_col
                self.execute()
            elif not self.hover:
                # stop the click and hover if the click is incomplete and the user stopped hovering
                self.hover = False
                self.click = False
                self.colour = self.norm_col
        # if the user wasn't already hovering and had their mouse down, check if they are now
        elif m_down and self.hover:
            self.click = True
            self.colour = self.click_col
        return None

    def update_colors(self) -> None:
        """
        Update the colours to match the current theme
        """
        self.click = False
        self.hover = False
        self.colour = theme.current.norm_col
        self.norm_col = theme.current.norm_col
        self.hov_col = theme.current.hov_col
        self.click_col = theme.current.click_col
        return None
    

    def execute(self) -> None:
        """ Execute the onclick function """
        self.on_click()
        return None
    
    
class ImageButton(Button):
    def __init__(self, on_click, n_str: str, normal_image: str, hover_image: str, click_image: str, position: tuple, size: tuple, flip: bool = False) -> None:
        """
        Arguments:
        - on_click: (function) to execute when clicked
        - n_str: (str) the normal name of the image in the button (e.g. stop.png)
        - normal_image: (str) the path to the normal image (e.g. Assets_PROG2/Icons/default_stop.png)
        - hover_image: (str) the path to the hover image (e.g. Assets_PROG2/Icons/default_stop_hover.png)
        - click_image: (str) the path to the click image (e.g. Assets_PROG2/Icons/default_stop_click.png)
        - position: (tuple[int, int]) the position of the button
        - size: (tuple[int, int]) the size of the image
        - flip: bool whether the flip the image horizontally or not
        """
        # call the parent constructor
        super().__init__(on_click, position, size)
        # try load the normal image, if not possible then genereate it
        try:
            self.norm_img = pygame.image.load(normal_image)
        except FileNotFoundError:
            self.norm_img = image_editor.change_colour(f"./Assets_PROG2/Icons/default_{n_str}", theme.current.norm_col, normal_image)
        try: # try load the hov image, if not possible then generate it
            self.hov_img = pygame.image.load(hover_image)
        except FileNotFoundError:
            self.hov_img = image_editor.change_colour(f"./Assets_PROG2/Icons/default_{n_str}", theme.current.hov_col, normal_image[:len(normal_image)-4]+"_hov.png")
        try: # try load the click image, if not possible then generate it
            self.click_img = pygame.image.load(click_image)
        except FileNotFoundError:
            self.click_img = image_editor.change_colour(f"./Assets_PROG2/Icons/default_{n_str}", theme.current.click_col, normal_image[:len(normal_image)-4]+"_click.png")
        
        # set other variable to be available to the class
        self.size = size
        self.flip = flip
        self.image: pygame.Surface = self.norm_img
        return None
    

    def check_hover(self, mouse: tuple, m_down: bool) -> None:
        """
        Arguments:
        - mouse: tuple with the x, y coords of the mouse
        - m_down: bool showing whether the user is right-clicking or not

        This method checks whether the user is hovering the progress bar:
        - returns None if it the user is clicking the mouse
        - if not, then it checks whether the mouse position is 
        """
        # similar to the base class, but deals with images instead
        if self.click or m_down:
            return
        if mouse[0] > self.pos[0] and mouse[0] < self.pos[0]+self.size[0] and mouse[1] > self.pos[1] and mouse[1] < self.pos[1]+self.size[1]:
            self.hover = True
            self.image = self.hov_img
        else:
            self.image = self.norm_img
            self.hover = False
        return None
    

    def check_click(self, m_down: bool) -> None:
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
        # similar to base class, but deals with images instead
        if self.click:
            if not m_down and self.hover:
                self.click = False
                self.image = self.hov_img
                self.on_click()
            elif not self.hover:
                self.hover = False
                self.click = False
                self.image = self.norm_img
        elif m_down and self.hover:
            self.click = True
            self.image = self.click_img
        return None
    
        
    def get_img(self) -> pygame.Surface:
        """ return the scaled image of the current loaded image"""
        return pygame.transform.scale(pygame.transform.flip(self.image, True, False), self.size) if self.flip else pygame.transform.scale(self.image, self.size)
    

    def draw(self, screen: pygame.Surface, check: bool, mouse: tuple, r_click: bool) -> None:
        """
        Arguments:
        - screen: the pygame surface to draw the elements on [passed by reference]
        - check: a boolean indicating whether the elements should check for hover and clicks or not
        - mouse: a tuple with the x, y coords of the mouse on the screen.
        - r_click: a bool indicating whether the user is right clicking or not
        
        Check for hover/click if allowed, render the button
        """
        if check:
            self.check_hover(mouse, r_click)
            self.check_click(r_click)
        screen.blit(self.get_img(), self.pos)
        return None

# initialise pygame before initialising some fonts    
pygame.init()
title = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Bold.ttf", 40)
subtitle = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Medium.ttf", 30)
small = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Thin.ttf", 16)

class TextButton(Button):
    def __init__(self, on_click, position: tuple, size: tuple, text: str, text_size: int = 1, id: int = -1, trailing: None | ImageButton = None) -> None:
        """
        Arguments:
        - on_click (function) to be executed when clicked
        - position (tuple) where the TextButton to be positions
        - text (str) the text of the text button
        - text_size (int) the size of the text, 1=small,2=medium,3=large, any other positive integer sets the font to that size
        - trailing (None or ImageButton) a trailing image on the text button
        """
        # initialise the parent's constructor
        super().__init__(on_click, position, size)

        # set the variable to be available class wide
        self.text = text
        self.trailing = trailing
        
        # determine the text size
        if text_size == 1:
            self.font = small
        elif text_size == 2:
            self.font = subtitle
        elif text_size == 3:
            self.font = title
        elif int(text_size) > 0:
            self.font = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Medium.ttf", int(text_size))
        else:
            print("error")
        
        self.id = id # id of the song linked to the button (not always used) (only valid if it is > 0)

        # set the size and the text_surface according to text_size
        self.text_surf = self.font.render(text, True, self.colour)
        self.size = self.text_surf.get_size() if size == (0, 0) else size
        return None
    
    
    def get_text(self) -> pygame.Surface:
        """ Returns the text surface when prompted to"""
        return self.font.render(self.text, True, self.colour)
    

    def update_text(self, text):
        """ Update the text """
        self.text = text


    def execute(self): 
        """
        Execute the relevant function on clicking
        """
        if self.id > -1:
            self.on_click(self.id)
        else:
            self.on_click()
    
    def draw(self, screen: pygame.Surface, check: bool, mouse: tuple, r_click: bool) -> None:
        """
        Arguments:
        - screen: the pygame surface to draw the elements on [passed by reference]
        - check: a boolean indicating whether the elements should check for hover and clicks or not
        - mouse: a tuple with the x, y coords of the mouse on the screen.
        - r_click: a bool indicating whether the user is right clicking or not
        
        If allowed, check for hover and click, and then render the buttons
        """
        # check for hover and click
        if check:
            self.check_hover(mouse, r_click)
            if not self.trailing or not self.trailing.hover: # type: ignore
                self.check_click(r_click)
        
        # draw the button and the trailing if it exists
        screen.blit(self.get_text(), self.pos)
        if self.hover and self.trailing:
            self.trailing.draw(screen, check, mouse, r_click)

        return None