import pygame, random, math

#keybinds
up = [pygame.K_UP, pygame.K_w]
down = [pygame.K_DOWN, pygame.K_s]
left = [pygame.K_LEFT, pygame.K_a]
right = [pygame.K_RIGHT,pygame.K_d]


#get random texture for drawing
def pencil_sprite(width, height):
    img = pygame.image.load("Sprites/draw_texture.png")
    x = random.randint(0, img.get_width() - width)
    y = random.randint(0, img.get_height() - height)
    return img.subsurface((x, y, width, height)).convert_alpha()
def get_vector_length(vektor):
    return math.sqrt(vektor[0]**2 + vektor[1]**2)
def big_render(renders):
    renders = sorted(renders, key=lambda obj: obj.pos[1]+obj.sprite.get_height())
    for rend in renders:
        rend.render()