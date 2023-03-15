import os
from pytube import YouTube
from moviepy.audio.io.AudioFileClip import AudioFileClip
import pygame

import theme
from classes.button import TextButton

pygame.init()

title_font = pygame.font.Font("./Assets/Fonts/Roboto-Bold.ttf", 40)
subtitle_font = pygame.font.Font("./Assets/Fonts/Roboto-Medium.ttf", 16)
small_font = pygame.font.Font("./Assets/Fonts/Roboto-Thin.ttf", 16)

class SearchResult:
    def __init__(self, query, pos, title, link, duration) -> None:
        self.query = query
        self.text = title
        self.pos = pos
        self.link = link
        self.title = TextButton(self.get_music, pos, (0, 0), title[:100]+"..." if len(title)>100 else title, 1)
        self.duration = subtitle_font.render(duration, True, theme.current.norm_col)
        self.done = None
    
    def get_music(self):
        print("fetching", self.link)
        # download the video file
        video = YouTube(self.link).streams.filter(only_audio=True).first()
        vid_file = video.download(output_path="./Music") # type: ignore
        
        # convert the video file into an audio
        self.convert_music(vid_file)

        # delete the video file
        if os.path.exists(vid_file):
            os.remove(vid_file)
        else:
            print("the file does not exist")
        
        self.done = small_font.render("Song Downloaded in ./Music", True, theme.current.norm_col)
    
    def convert_music(self, vid_file):
        mp3_file = AudioFileClip(vid_file)
        try:
            mp3_file.write_audiofile(f"./Music/{self.text}.mp3")
            mp3_file.close()
        except:
            mp3_file.close()
            mp3_file = AudioFileClip(vid_file)
            mp3_file.write_audiofile(f"./Music/{self.query}.mp3")
            mp3_file.close()
    
    def draw(self, screen, check, mouse, m_down):
        self.title.draw(screen, check, mouse, m_down)
        screen.blit(self.duration, (self.pos[0], self.pos[1]+20))
        if self.done:
            screen.blit(self.done, (self.pos[0]+40, self.pos[1]+20))