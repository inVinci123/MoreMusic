"""
This File contains the theme class and the themes dictionary to hold data about what themes can be used
"""

# Current Theme
class Theme:
    """
    Manages all colour values that exist in the app per theme
    """
    def __init__(self, norm = (240, 240, 240), hov = (120, 120, 120), click = (60, 60, 60), progress_norm = (120, 120, 120), progress_hov = (60, 60, 60), progress_click = (30, 30, 30), bg = (69, 69, 69), sidebar_bg = (0, 0, 0), text_field_text = (0, 0, 0), text_field_bg = (255, 255, 255)):
        self.norm_col = norm
        self.hov_col = hov
        self.click_col = click
        self.progress_norm_col = progress_norm
        self.progress_hov_col = progress_hov
        self.progress_click_col = progress_click
        self.text_field_bg = text_field_bg
        self.text_field_text = text_field_text
        self.bg = bg
        self.sidebar = sidebar_bg

default = Theme() # default uses default values

# the themes dictionry keepts track of all the themes that can be chosen from
themes = {
    "default": default,
    "blue": Theme(norm = (245, 217, 37), hov=(163, 145, 25), click=(123, 109, 19), progress_norm=(168, 146, 0), progress_hov=(112, 98, 0), progress_click=(84, 73, 0), bg=(62, 36, 244), sidebar_bg=(33, 13, 168)),
    "mint": Theme(norm=(221, 255, 247), hov=(221*0.5, 255*0.5, 247*0.5), sidebar_bg=(104*0.75, 223*0.75, 218*0.75), progress_norm=(147, 225, 216), bg=(104*0.75, 223*0.75, 218*0.75)),
    "nebula": Theme(norm=(25, 179, 184), hov=(25*0.55, 179*0.55, 184*0.55), click=(25*0.35, 179*0.35, 184*0.35), progress_norm=(190, 60, 136), progress_hov=(95, 30, 68), progress_click=(48, 15, 34), bg=(33*0.5, 33/2, 153/2), sidebar_bg=0x0B0B32)#(36, 36, 86))
    }
current_name = "mint"
current = themes[current_name]