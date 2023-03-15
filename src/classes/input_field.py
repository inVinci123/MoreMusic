"""
This file contains the class of Input Fields, used as the primary input system throughout the app.
"""
# imports
import pygame
import theme

# initialising pygame and creating a font
pygame.init()
font = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Medium.ttf", 22)

class InputField:
    def __init__(self, pos: tuple, size: tuple = (300, 35)) -> None:
        """
        Arguments:
        - pos (tuple) the position of the input field
        - size (tuple) the size of the input field
        """
        # make the variables available class wide
        self.pos = pos
        self.size: tuple = size

        # initialise with some default text, like it should be
        self.text = "Hello, world!"

        # initialise the active status, hover and click  to False
        self.is_active = False
        self.hover = False
        self.click = False

        # to keep track of the colour
        self.colour = theme.current.norm_col

        # typing variables
        self.blink_cool = 5
        self.display_limit = 280
        self.current_index = 0
        return None
    
    
    def get_rect(self) -> pygame.Rect:
        """Returns the rect formed field"""
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
            self.colour = theme.current.hov_col
        else:
            # else the user is not hovering or clicking, so let it be normal
            self.colour = theme.current.norm_col
            self.hover = False
        return None
    
    
    def check_click(self, m_down: bool) -> None:
        """
        Arguments
        - m_down: bool showing whether the user is right-clicking or not

        This method checks whether the user is clicking on the button and executes a relevant function:
        - checks if self.click is true (i.e. rightclicked and mouse is hovering)
        - if so then checks if the user has lifted the click to complete the click
        - if so it activates the input field
        - else if the user is no longer hovering over the clickable element, cancel the self.click and reset to normal
        - if self.click is not true, then check if self.click should be true (so it can check if the click is completed in the next frame)
        """
        if self.click:
            # the user was already hovering and had their mouse down
            if not m_down and self.hover:
                # if the mouse has been lifted, the click is complete
                self.click = False
                self.colour = theme.current.hov_col
                self.is_active = True
            elif not self.hover:
                # stop the click and hover if the click is incomplete and the user stopped hovering
                self.hover = False
                self.click = False
                self.colour = theme.current.norm_col
        # if the user wasn't already hovering and had their mouse down, check if they are now
        elif m_down and self.hover:
            self.click = True
            self.is_active = True
            self.colour = theme.current.click_col
        return None
    
        
    def draw(self, screen: pygame.Surface, check = False, mouse = (0, 0), m_down = False) -> None:
        """
        Arguments:
        - screen: the pygame surface to draw the elements on [passed by reference]
        - check: a boolean indicating whether the elements should check for hover and clicks or not
        - mouse: a tuple with the x, y coords of the mouse on the screen.
        - m_down: a bool indicating whether the user is right clicking or not
        
        Check for hover/click if allowed, render the input field stuff
        """
        # update the blink cooldown
        self.blink_cool -= 1
        if self.blink_cool < -40:
            self.blink_cool = 40
        
        a = pygame.Surface(self.size)

        if check:
            # check for hover/click
            self.check_hover(mouse, m_down)
            self.check_click(m_down)

        # create the border and the text field
        border = pygame.rect.Rect((0, 0), self.size)
        text_field = pygame.rect.Rect((4, 4), (self.size[0]-8, self.size[1]-8))
        # draw the two
        pygame.draw.rect(a, self.colour, border)
        pygame.draw.rect(a, theme.current.text_field_bg, text_field)

        if self.is_active: # if the field is active, continue blinking
            current_text = font.render(self.text+"|" if self.blink_cool>0 else self.text, True, theme.current.text_field_text)
        else: # else render item aynywas
            current_text = font.render(self.text, True, theme.current.text_field_text)

        # update the font stuff
        text_size = font.render(self.text, True, (0, 0, 0)).get_rect().size[0]
        if text_size > self.display_limit:
            text_surf = pygame.Surface((self.size[0]-8, self.size[1]-8))
            text_surf.fill(theme.current.text_field_bg)
            text_surf.blit(current_text, (self.display_limit-text_size, 0))
            a.blit(text_surf, (4, 4))
        else:
            a.blit(current_text, (4, 4))

        screen.blit(a, self.pos)
        return None


    def update_text(self, event, shift) -> None:
        """ Updates the text by checking each event and whether it is a valid key press or not """
        try:
            # try see if the unicode value can be used to type
            if event.unicode in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^*()+=-_{}[]:;'\",<>.?/`~|\\ ":
                self.text += event.unicode
                self.current_index += 1
            # shift backspace deletes the entire text field
            elif event.key == pygame.K_BACKSPACE:
                if shift:
                    self.text = ""
                    self.current_index = 0
                self.text = self.text[:len(self.text)-1]
                self.current_index = max(self.current_index-1, 0)
        except AttributeError:
            # if the value is invalid, continue to the next iteration
            pass