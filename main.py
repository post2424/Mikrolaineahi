import pygame, sys, threading, math
from pygame.transform import scale
import functions_values as fv
pygame.init()
pygame.font.init()

# Põhi sätted
font = pygame.font.Font('GOTHIC.TTF', 40)  # valib fondi ja selle suuruse
timer = pygame.time.Clock()
FPS = 60
pygame.display.set_caption("Mäng")

# Ekraan
ekraan_laius,ekraan_pikkus = 880, 700
ekraan_suurus = (ekraan_laius, ekraan_pikkus)  # kui suur on aken kus mäng toimub
aken = pygame.display.set_mode(ekraan_suurus,pygame.NOFRAME)
time = 0

# Mõned värvid
must = (0, 0, 0)
valge = (255, 255, 255)

class Objekt:
    def __init__(self, sprite = None, pos = None, speed = None, width = None, base_speed = None):
        self.speed = speed or [0,0]
        self.pos = pos or [0, 0]
        self.width = width or self.sprite.get_width()
        self.change_sprite(sprite)
        self.base_speed = base_speed or [0,0]
    def render(self):
        self.pos = [i + j for i, j in zip(self.pos, self.speed)]
        aken.blit(self.sprite, self.pos)
    def change_sprite(self, sprite = None):
        sprite = sprite or "placeholder.png"
        self.sprite = pygame.image.load("Sprites/"+sprite)
        heightdivwidth = (self.sprite.get_height() / self.sprite.get_width())
        if self.width is not None:
            self.sprite = pygame.transform.scale(self.sprite,(self.width, heightdivwidth*self.width))
    def flip_sprite(self):
        self.sprite = pygame.transform.flip(self.sprite, True, False)
# pmst kui  callid objekti siis objekt(sprite filei nimi, pos = (X,Y) /
#kiirus, kui suureks teha sprite), ainuke nõutud on sprite file


class Pintsel(Objekt):
    def render(self):
        global speed_length
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1] -self.sprite.get_height() # selleks, et pintsli vasak alumine äär oleks kursori peal
        speed_x = mouse_x - self.pos[0]
        speed_y = mouse_y - self.pos[1]
        if speed_length  < 20:
            self.pos = [mouse_x, mouse_y]
        else:
            jump_slow = 3.75
            speed_length =fv.get_vector_length([speed_x,speed_y])
            self.speed = (speed_x/jump_slow, speed_y/jump_slow)
        super().render()

#self.speed toimib nii et võtab asukoha kuhu saada tahab ja asukoha, kus on ja leieb nende vektori
#,suunaga sinna poole kuhu saada tahetakse ja jagab selle jump slow-iga


class Värv(Objekt):
    def __init__(self, sprite, pos):
        self.sprite = sprite
        self.pos = pos
        self.speed = [0,0]
class Vastane(Objekt):
    pass

taust = Objekt('background.png', width=ekraan_laius)
mikro = Objekt("mikro_left.png", [100,300], width=100, base_speed=8)
pintsel = Pintsel("pencil.png", width=200 )
vastane = Vastane("man_shoot.png",[700,300], speed=(-2.5,0), width=100, base_speed=8)
# Mängu tsükkel
joonistab = False
strokes = []
walk_change, brush_size,brush_size2,last_pos = 0,0,0,None
to_render = []
while True:

    time +=1
    #TODO: liigutada see vastasesse või objekti
    if time == 120:
        vastane.speed = [0,0]
    taust.render()
    to_render.append(vastane)
    to_render.append(mikro)
    if abs(vastane.speed[0]) > 0:
        walk_change += 1
        if walk_change > 10:
            vastane.change_sprite('man_side2.png')
        else:
            vastane.change_sprite('man_side.png')
        if walk_change > 20:
            walk_change = 0
    else:
        vastane.change_sprite('man_shoot.png')
    if joonistab:
        pintsel.render()

        brush_size = int(brush_size2)
        if brush_size < 10:
            brush_size2 += 0.5
        if alpha < 100:
            alpha += 10
        #image = fv.pencil_sprite(brush_size, brush_size)
        image = pygame.transform.scale(pygame.image.load("Sprites/draw_alpha3.png"), (brush_size, brush_size))
        image.set_alpha(alpha)
        mouse_pos = pygame.mouse.get_pos()
        if last_pos:
            vektor = [i - j for i, j in zip(mouse_pos, last_pos)]
            vektor_length = fv.get_vector_length(vektor)
            spaces = max(1, int(vektor_length / brush_size*3))

            for space in range(1, spaces + 1):
                factor = space / spaces
                new_pos = [lp + v * factor for lp, v in zip(last_pos, vektor)]
                strokes.append(Värv(image, new_pos))

        last_pos = mouse_pos

    fv.big_render(to_render)
    for stroke in strokes:
        stroke.render()
    to_render = []
    #iga kord kui on sündmus
    for event in pygame.event.get():
        #quit event
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        #klaviatuuri nupp alla
        elif event.type == pygame.KEYDOWN:
            #TODO: sptiteide vahetamiseks võiks objekt files mingi funktsiooni teha
            if event.key in fv.up:
                mikro.change_sprite("mikro_away.png")
                mikro.speed[1] -= mikro.base_speed
            if event.key in fv.down:
                mikro.change_sprite("mikro_forward.png")
                mikro.speed[1] += mikro.base_speed
            if event.key in fv.left:
                mikro.change_sprite("mikro_left.png")
                mikro.speed[0] -= mikro.base_speed
            if event.key in fv.right:
                mikro.change_sprite("mikro_right.png")
                mikro.speed[0] += mikro.base_speed
        #klaviatuuri nupp üles
        elif event.type == pygame.KEYUP:
            if event.key in fv.up:
                mikro.speed[1] += mikro.base_speed
            if event.key in fv.down:
                mikro.speed[1] -= mikro.base_speed
            if event.key in fv.left:
                mikro.speed[0] += mikro.base_speed
            if event.key in fv.right:
                mikro.speed[0] -= mikro.base_speed
        #hiire nupp alla
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                joonistab = True
                brush_size2, alpha, last_pos = 1,0, None
                speed_length = float('inf') #lõppmatus
                mouse_x, mouse_y = pygame.mouse.get_pos()
                a = [mouse_x,mouse_y,ekraan_laius-mouse_x,ekraan_pikkus-mouse_y]
                match a.index(min(a)):
                    case 0:
                        pintsel.pos = (-pintsel.sprite.get_width(), mouse_y - pintsel.sprite.get_height())
                    case 1:
                        pintsel.pos = (mouse_x, -pintsel.sprite.get_height())
                    case 2:
                        pintsel.pos = (ekraan_laius + pintsel.sprite.get_width(), mouse_y-pintsel.sprite.get_height())
                    case 3:
                        pintsel.pos = (mouse_x, ekraan_pikkus + pintsel.sprite.get_height())

        #hiire nupp üles
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                joonistab = False


    # Uuendame ekraani
    pygame.display.update()
    timer.tick(FPS)