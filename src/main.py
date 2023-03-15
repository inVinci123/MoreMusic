"""
Main file, renders the main window and runs the program
"""
# imports
import os
import pygame
import time
# to check the performance
start = time.perf_counter()

# Temporary measure (to ensure the correct directory is used)
if __name__ == "__main__":
    try:
        os.chdir(os.path.join(os.getcwd(), "PROG2"))
    except FileNotFoundError:
        pass
# End temporary measure

# more imports
import theme
from music_player import MusicPlayer
from classes.sidebar import Sidebar
from classes.button import Button, ImageButton, TextButton
from screen_elements.controls_tray import ControlsTray
from screen_elements.progress_bar import ProgressBar
from classes.playlist import PlaylistManager
from screen_elements.playlist_view import PlaylistView
from screen_elements.playlist_dialog import PlaylistDialog

# initialise pygame
pygame.init()

# set the dimensions of the window
L, H = 1080, 720

# create the window and set it's title
screen: pygame.Surface = pygame.display.set_mode((L, H))
pygame.display.set_caption("More Music")
# set a constant FRAMERATE
FRAMERATE = 60
# clock to to implement the frame rate
clock: pygame.time.Clock = pygame.time.Clock()

# initialise some fonts
title_font = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Bold.ttf", 40)
subtitle_font = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Medium.ttf", 24)
small_font = pygame.font.Font("./Assets_PROG2/Fonts/Roboto-Thin.ttf", 16)

# quick loading screen to not give the user a heart attack when the app is loading
screen.fill(theme.current.bg)
screen.blit(title_font.render("Loading...", True, theme.current.norm_col), (L/2-100, H/2-10))
pygame.display.update()

rootpath = "./Music/" # rootpath of where the music will normally be located

def update_playlist(id) -> None:
    """
    Arguments:
    - id: (int) the id of the playlist to be loaded in

    Loads a playlist in and updates the info in relevant places
    """
    global player, p_view
    player.change_playlist(id, L/4) # use the music player to load it in
    p_view.load_playlist() # update the info in the playlist view
    return None


def refresh_playlists(id=None) -> None:
    """
    Arguments:
    - id (optional, int) indicates whether the playlist should also be updated to the provided id

    Refreshes the playlists shown in the playlist bar and reloads the playlist in the playlist view
    """
    global playlistbar, p_view
    open = playlistbar.is_open # temp variable to keep track of if the playlistbar was open or not
    # reinitialising the playlist bar to refresh the playlists in the bar
    playlistbar = Sidebar((L/4, H), (0, 0), "Playlists", [(PlaylistManager.playlists[id].name[:13]+"..." if len(PlaylistManager.playlists[id].name)>16 else PlaylistManager.playlists[id].name, get_id(id)) for id in PlaylistManager.playlists.keys()], -1, False, shift_screen_elements, open_playlist, list(PlaylistManager.playlists.keys()))
    playlistbar.is_open = open # set it's state to open/close based on the previous stuff
    p_view.load_playlist()
    if id:
        update_playlist(id) # also start a new playlist if required
    return None

# music Player
player = MusicPlayer(rootpath, refresh_playlists, (L, H))

# controls Tray (for playing, pausing, stopping, skipping, sound controls, etc.)
tray = ControlsTray(player, (L/2-185, H-70), 60, (28, 28))

# the progress bar
progress_bar = ProgressBar(player, (100, 0.85*H), (L-200, 10), player.skip_to)

# temp var to keep track of where the song title should be positioned
song_title_pos = (100, 0.85*H-55)

def shift_screen_elements(val) -> None:
    """
    Arguments:
    val: (int/float) the amount to shift the screen elements by

    Shifts the screen elements by val, called by the playlistbar to adjust the position of the screen elements as requied
    """
    global tray, progress_bar, song_title_pos, player, p_view, playlist_button, themebar_button, add_playlist_button
    # shift all screen elements
    tray.shift(val)
    progress_bar.shift(val)
    p_view.shift(val)
    song_title_pos = song_title_pos[0]+val, song_title_pos[1]
    playlist_button.pos = playlist_button.pos[0]+(val-5*(val/abs(val))), playlist_button.pos[1]
    add_playlist_button.pos = add_playlist_button.pos[0]+(val-5*(val/abs(val))), add_playlist_button.pos[1]
    for s in player.playlist_texts: # shift each playlist view text
        s.pos = (s.pos[0]+val, s.pos[1])
    return None


def get_id(id) -> object:
    """
    work around since passing functions as lambda doesn't work very well with for loops
    if the argument of the function is being iterated
    """
    return lambda: update_playlist(id)


def change_theme(id) -> None:
    """
    Arguments:
    - id: (int) the id of the theme to be loaded in

    Changes the global theme of the application by refreshing objects,
    usually called by the theme options in the themebar
    """
    global playlist_button, themebar_button, add_playlist_button
    # change the theme in the Theme module
    theme.current_name = id
    theme.current = theme.themes[id]

    # load the theme in screen elements
    tray.load_theme()
    themebar.load_theme()
    playlistbar.load_theme()
    p_view.load_theme()
    progress_bar.load_theme()
    player.set_song_title()
    p_dialog.load_theme()
    # redefine some elements with the new theme
    add_playlist_button = TextButton(p_dialog.open, add_playlist_button.pos, add_playlist_button.size, "+", 3)
    playlist_button = ImageButton(playlistbar.open, "playlist.png", f"./Assets_PROG2/Icons/{theme.current_name}_playlist.png", f"./Assets_PROG2/Icons/{theme.current_name}_playlist_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_playlist_click.png", playlist_button.pos, playlist_button.size)
    themebar_button = ImageButton(themebar.open, "settings.png", f"./Assets_PROG2/Icons/{theme.current_name}_settings.png", f"./Assets_PROG2/Icons/{theme.current_name}_settings_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_settings_click.png", themebar_button.pos, themebar_button.size)
    return None


def get_change_theme(id) -> object:
    """
    work around since passing functions as lambda doesn't work very well with for loops
    if the argument of the function is being iterated
    """
    return lambda: change_theme(id)


def open_playlist(id) -> None:
    """ open a playlist for editing """
    p_dialog.edit_playlist(id)
    return None

# load the sidebars
themebar = Sidebar((L/3, H), (2*L/3, 0), "Themes", [(f"{t}", get_change_theme(t)) for t in theme.themes.keys()], 1, True)
playlistbar = Sidebar((L/4, H), (0, 0), "Playlists", [(PlaylistManager.playlists[id].name[:13]+"..." if len(PlaylistManager.playlists[id].name)>16 else PlaylistManager.playlists[id].name, get_id(id)) for id in PlaylistManager.playlists.keys()], -1, False, shift_screen_elements, open_playlist, list(PlaylistManager.playlists.keys()))

# initialise the playlist view, playlist dialog
p_view = PlaylistView((100, 50), player.current_playlist, player, length=L-200)
p_dialog = PlaylistDialog(playlistbar, player, update_playlist, refresh_playlists)
# buttons to trigger the opening of the playlistbar, playlist dialog and the themebar
playlist_button = ImageButton(playlistbar.open, "playlist.png", f"./Assets_PROG2/Icons/{theme.current_name}_playlist.png", f"./Assets_PROG2/Icons/{theme.current_name}_playlist_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_playlist_click.png", (5, 5), (40, 40))
add_playlist_button = TextButton(p_dialog.open, (55, 5), (0, 0), "+", 3)
themebar_button = ImageButton(themebar.open, "settings.png", f"./Assets_PROG2/Icons/{theme.current_name}_settings.png", f"./Assets_PROG2/Icons/{theme.current_name}_settings_hov.png", f"./Assets_PROG2/Icons/{theme.current_name}_settings_click.png", (L-50, 10), (40, 40))

# printing how long it takes to load the Assets_PROG2
print(f"Execution starts. Time taken = {time.perf_counter()-start}")

# whether the shift key has been pressed
shift_key = False

running = True
while running: # main loop
    # fill with bg every frame
    screen.fill(theme.current.bg)
    # get the events that occured in this frame
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT: # if the user wants to quit, stop running the main loop
            running = False
        if e.type == pygame.KEYUP:
            if e.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]: # check if the shift key was lifted
                shift_key = False
        if e.type == pygame.KEYDOWN:
            if e.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]: # check if the shift key was pressed
                shift_key = True
            if p_dialog.is_open: continue # don't check anything else if we are in playlist editing mode
            if e.key == pygame.K_n: # next song
                player.next()
            if e.key == pygame.K_p: # previous song
                player.prev()
            if e.key == pygame.K_SPACE: # pause or unpause
                player.pause()
            if e.key == pygame.K_s: # stop the song
                player.stop()
            if e.key == pygame.K_RIGHT: # skip 10 seconds forward
                player.skip10()
            if e.key == pygame.K_LEFT: # skip 10 seconds back
                player.rewind10()
            if e.key == pygame.K_ESCAPE: # close or open the themebar based on it's current state
                if not themebar.closing and not themebar.opening:
                    themebar.open() if not themebar.is_open else themebar.close()
            if e.key == pygame.K_x: # close or open the playlistbar based on it's current state
                if not playlistbar.closing and not playlistbar.opening:
                    playlistbar.open() if not playlistbar.is_open else playlistbar.close()
            if e.key == pygame.K_UP: # increase the volume by an increment of 0.05
                player.change_volume(0.05)
            if e.key == pygame.K_DOWN: # decrease the volume by an increment of 0.05
                player.change_volume(-0.05)
    
    # get the mouse position and whether the right moueskey was pressed or not
    mouse = pygame.mouse.get_pos()
    r_click = pygame.mouse.get_pressed(3)[0]
    
    # draw the controls tray and only check if neither the themebar nor the playlist dialog are open
    tray.draw(screen, not themebar.is_open and not p_dialog.is_open, mouse, r_click)

    # only draw the progress bar if the player music hasn't stopped and the playlist_dialog isn't open
    progress_bar.draw(screen, not player.stopped and not p_dialog.is_open, mouse, r_click)
    
    # draw the song title
    screen.blit(player.song_title_text, song_title_pos)

    # draw the playlist view and the playlist bar (playlistbar.draw will know whether to draw or not)
    # don't check for element clicking/hovering if the themebar or the playlist dialog is open
    p_view.draw(screen, mouse, r_click, not themebar.is_open and not p_dialog.is_open)
    playlistbar.draw(screen, mouse, r_click, not themebar.is_open and not p_dialog.is_open)

    # set the playlist button to close if it is open else open
    playlist_button.on_click = playlistbar.close if playlistbar.is_open else playlistbar.open
    # draw the playlist buttons, same check rules apply
    playlist_button.draw(screen, not themebar.is_open and not p_dialog.is_open, mouse, r_click)
    add_playlist_button.draw(screen, not themebar.is_open and not p_dialog.is_open, mouse, r_click)
    
    # draw the themebar and the themebar button and change it's on click appropriately
    # this is drawn almost last because it can potentially overlay everything
    themebar.draw(screen, mouse, r_click, not p_dialog.is_open)
    themebar_button.draw(screen, not p_dialog.is_open, mouse, r_click)
    themebar_button.on_click = themebar.close if themebar.is_open else themebar.open

    # last screen element is the p_dialog, as if it is open, it overlays everything else
    if p_dialog.is_open: p_dialog.draw(screen, events, shift_key, mouse, r_click)

    # update the display with the drawn elements and move to the next frame
    pygame.display.update()
    clock.tick(FRAMERATE)

# once out of the loop quit pygame so as to not cause any errors
pygame.quit()