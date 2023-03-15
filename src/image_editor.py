# imports
import pygame

def change_colour(image, col, filename) -> pygame.Surface:
    """ This method takes in a default image, colours it in with `col` and saves it + returns it to where it as called """
    # load the normal image
    img = pygame.image.load(image).convert_alpha()

    w, h = img.get_size()
    r, g, b = col
    # iterate through every pixel and edit them to the spcified make a new file.
    for x in range(w):
        for y in range(h):
            if img.get_at((x, y))[3] > 0:
                img.set_at((x, y), (r, g, b, 255))
    pygame.image.save(img, filename, filename[:len(filename)-4])
    return img