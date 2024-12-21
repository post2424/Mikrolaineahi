import pygame, sys, threading, math, random
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
        self.width = width
        self.change_sprite(sprite)
        self.base_speed = base_speed or [0,0]
    def render(self):
        self.pos = fv.get_vectors_sum(self.pos, self.speed)
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
        global slow_speed
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1] -self.sprite.get_height() # selleks, et pintsli vasak alumine äär oleks kursori peal
        speed_x = mouse_x - self.pos[0]
        speed_y = mouse_y - self.pos[1]

        if slow_speed > 1.2:
            slow_speed -= 0.2
            self.speed = (speed_x/slow_speed, speed_y/slow_speed)
        else:
            self.speed = [0,0]
            self.pos = (mouse_x, mouse_y)
        super().render()
    def joonista(self):
        pass

#self.speed toimib nii et võtab asukoha kuhu saada tahab ja asukoha, kus on ja leieb nende vektori
#,suunaga sinna poole kuhu saada tahetakse ja jagab selle jump slow-iga


class Värv(Objekt):
    def __init__(self, pos, brush_size, alpha):
        global brush_image
        self.alpha = alpha
        self.sprite = pygame.transform.scale(brush_image,(brush_size,brush_size))
        self.sprite = pygame.transform.rotozoom(self.sprite,random.randint(0,359),1).convert_alpha()
        self.sprite.set_alpha(self.alpha)
        self.pos = pos
        self.speed = [0,0]
        self.kestvus = 20
    def render(self):
        global strokes, joonistab
        if joonistab == False:
            if self.kestvus == 0:
                del strokes[0]
                self.kestvus = 5
            else:
                self.kestvus -= 1
        super().render()
class Vastane(Objekt):
    pass
#laeme erinevaid textureid valmis, väljaspool objekti optimiseerimise jaoks
brush_image = pygame.image.load("Sprites/draw_texture.png")


taust = Objekt('background.png', width=ekraan_laius)
mikro = Objekt("mikro_left.png", [100,300], width=100, base_speed=8)
pintsel = Pintsel("pencil.png", width=200 )
vastane = Vastane("man_shoot.png",[700,300], speed=(-2.5,0), width=100, base_speed=8)
# Mängu tsükkel
joonistab = False
strokes = []
walk_change, brush_size,brush_size2,last_pos = 0,0,0,None
to_render = []
detection_positions = []
render_list2 = []
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
        mouse_pos = pygame.mouse.get_pos()
        detection_positions.append(mouse_pos)
        brush_size = int(brush_size2)
        if brush_size < 7:
            brush_size2 += 0.75
        if alpha < 200:
            alpha += 15
        if last_pos:
            vektor = fv.get_vector(mouse_pos,last_pos)
            vektor_length = fv.get_vector_length(vektor)
            spaces = max(1, int(vektor_length / brush_size*3))

            for space in range(1, spaces + 1):
                factor = space / spaces
                new_pos = [lp + v * factor for lp, v in zip(last_pos, vektor)]
                strokes.append(Värv(new_pos, brush_size, alpha))
        last_pos = mouse_pos


    if detection_positions and not joonistab:
        if fv.is_line(detection_positions):
            center = fv.get_vectors_sum(detection_positions[0],detection_positions[-1])
            center = (center[0]/2,center[1]/2)
            render_list2.append(Objekt(pos=center))

        detection_positions.clear()
    fv.big_render(to_render)
    fv.big_render(render_list2)
    for stroke in strokes:
        stroke.render()
    if joonistab:
        pintsel.render()

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
                slow_speed = 3.75
                fv.set_nearest_offscreen_pos(pygame.mouse.get_pos(),pintsel,ekraan_suurus)

        #hiire nupp üles
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                joonistab = False


    # Uuendame ekraani
    pygame.display.update()
    timer.tick(FPS)