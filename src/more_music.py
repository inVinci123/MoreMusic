import os

import pygame
from youtubesearchpython import VideosSearch, ResultMode

import theme
from search_result import SearchResult
from classes.input_field import InputField
from classes.button import TextButton

pygame.init()
clock: pygame.time.Clock = pygame.time.Clock()

BG = theme.current.bg
L, H = 1080, 600
FRAMERATE = 24

subtitle_font = pygame.font.Font("./Assets/Fonts/Roboto-Medium.ttf", 24)

screen: pygame.Surface = pygame.display.set_mode((L, H))
pygame.display.set_caption("More Music")

query_text = subtitle_font.render("Enter Query:", True, theme.current.norm_col)
search_field = InputField((180, 100))
search_field.text = "Never Gonna Give You Up"
search_button = TextButton(lambda: fetch_results(search_field.text), (500, 100), (0, 0), "Search", 24)

display_results = []

search_limit = 6
no_internet = None

def fetch_results(query):
    global display_results, no_internet
    display_results.clear()
    try:
        vs = VideosSearch(query, limit = search_limit)
        search_results = vs.result(ResultMode.dict)["result"] # type: ignore
        for i, r in enumerate(search_results):
            display_results.append(SearchResult(query, (30, 180+i*50), f"{r['title']}, by {r['channel']['name']}", f"youtube.com/watch?v={r['id']}", r["duration"])) # type: ignore
    except:
        no_internet = subtitle_font.render("An error occured. Please close this window and try again later.", True, theme.current.norm_col)

running: bool = True
shift = False
while running:
    screen.fill(BG)
    events = pygame.event.get()

    for e in events:
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYUP:
            if e.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                shift = False
        if e.type == pygame.KEYDOWN:
            if e.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                shift = True
    
    mouse = pygame.mouse.get_pos()
    m_down = pygame.mouse.get_pressed()[0]

    if m_down:
        search_field.is_active = False

    if no_internet:
        screen.blit(no_internet, (30, H/2-10))

    for r in display_results:
        r.draw(screen, True, mouse, m_down)
    
    search_field.draw(screen, True, mouse, m_down)
    search_button.draw(screen, True, mouse, m_down)
    screen.blit(query_text, (30, 100))

    if search_field.is_active:
        for e in events:
            if e.type == pygame.KEYDOWN:
                search_field.update_text(e, shift)
                if e.key == pygame.K_RETURN:
                    fetch_results(search_field.text)

    clock.tick(FRAMERATE)
    pygame.display.flip()
pygame.quit()