import pygame, sys, math, random
from pygame.examples.sprite_texture import sprite
from pygame.transform import scale
import functions_values as fv
pygame.init()
pygame.font.init()




# Põhi sätted
font = pygame.font.Font('GOTHIC.TTF', 40)  # valib fondi ja selle suuruse
timer = pygame.time.Clock()
pygame.display.set_caption("Mäng")

# Ekraan
FPS = 60
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
        if sprite[-1].lower() == 'f':
            self.sprite = pygame.image.load("Sprites/" + sprite[0:-2])
            self.sprite = pygame.transform.flip(self.sprite, True, False)
        self.sprite = pygame.image.load("Sprites/"+sprite)
        heightdivwidth = (self.sprite.get_height() / self.sprite.get_width())
        if self.width is not None:
            self.sprite = pygame.transform.scale(self.sprite,(self.width, heightdivwidth*self.width))

# pmst kui  callid objekti siis objekt(sprite filei nimi, pos = (X,Y) /
#kiirus, kui suureks teha sprite), ainuke nõutud on sprite file

# kui spritei nime lõpus on f siis ta flippib spritei
class Character(Objekt):
    def set_sprites(self,up_sprites, down_sprites, left_sprites, right_sprites,frames_per_sprite=None,still_sprites=None):
        self.up_sprites = up_sprites
        self.down_sprites = down_sprites
        self.left_sprites = left_sprites
        self.right_sprites = right_sprites
        self.frames_per_sprite = frames_per_sprite
        self.still_sprites = still_sprites
    def play_animation(self,sprites):
        if isinstance(sprites,str):
            self.change_sprite(sprites)
        elif not self.frames_per_sprite:
            self.change_sprite(sprite[0])
        else:
            if 'sprite_num' not in locals() or sprite_num == Num_sprites:
                sprite_num = 0
            if 'walk_change' not in locals():
                walk_change = 0
            Num_sprites = len(sprites)
            if walk_change == self.frames_per_sprite:
                sprite_num += 1
                walk_change = 0
            self.change_sprite(sprites[sprite_num])
    def sprite_in_direction(self):
        if self.speed[0] < 0: #vasakule
            self.play_animation(self.left_sprites)
        elif self.speed[0] > 0:  # paremale
            self.play_animation(self.right_sprites)
        elif self.speed[1]  < 0:#üles
            self.play_animation(self.up_sprites)
        elif self.speed[1] > 0:  # alla
            self.play_animation(self.down_sprites)
        elif self.still_sprites:
            self.play_animation(self.still_sprites)




    def render(self):
        self.sprite_in_direction()
        super().render()
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
    def joonista(self,MAX_BRUSH_SIZE,BRUSH_CHANGE_RATE,MAX_ALPHA,ALPHA_CHANGE_RATE):
        global last_pos, strokes, detection_positions, brush_size, alpha
        mouse_pos = pygame.mouse.get_pos()
        detection_positions.append(mouse_pos)
        if brush_size < MAX_BRUSH_SIZE:
            brush_size += BRUSH_CHANGE_RATE
        if alpha < MAX_ALPHA:
            alpha += ALPHA_CHANGE_RATE
        if last_pos:
            vektor = fv.get_vector(mouse_pos, last_pos)
            vektor_length = fv.get_vector_length(vektor)
            spaces = max(1, int(vektor_length / brush_size * min(brush_size, 3)))

            for space in range(1, spaces + 1):
                factor = space / spaces
                new_pos = [lp + v * factor for lp, v in zip(last_pos, vektor)]
                strokes.append(Värv(new_pos, brush_size, alpha))
        last_pos = mouse_pos
#self.speed toimib nii et võtab asukoha kuhu saada tahab ja asukoha, kus on ja leieb nende vektori
#,suunaga sinna poole kuhu saada tahetakse ja jagab selle jump slow-iga


class Värv(Objekt):
    def __init__(self, pos, brush_size, alpha, speed=None):
        super().__init__(speed, pos)
        self.alpha = alpha
        self.sprite = pygame.transform.scale(pygame.image.load("Sprites/draw_texture.png"),(brush_size,brush_size))
        self.sprite = pygame.transform.rotozoom(self.sprite,random.randint(0,359),1).convert_alpha()
        self.sprite.set_alpha(self.alpha)
    def render(self):
        global strokes, joonistab, brush_size
        if joonistab == False and strokes[0].pos == self.pos:
            a = math.floor(len(strokes)/5)
            for i in range(a):
                del strokes[i]
            if a == 0:
                del strokes[0]
        super().render()
class Vastane(Character):
    pass

taust = Objekt('background.png', width=ekraan_laius)
mikro = Character("mikro_left.png", [100,300], width=100, base_speed=8)
mikro.set_sprites('mikro_away.png','mikro_forward.png','mikro_left.png','mikro_right.png')
pintsel = Pintsel("pencil.png", width=200 )
vastane = Vastane("man_shoot.png",[700,300], speed=(-2.5,0), width=100, base_speed=8)
vastane.set_sprites(['man_away.png','man_away.pngf'],['man_away2.png','man_away2.pngf'],['man_side.png','man_side2.png'],['man_side.pngf','man_side2.pngf'],10, 'man_shoot.png')
# Mängu tsükkel
joonistab = False
to_render = []
strokes = []
detection_positions = []
render_list2 = []
#constants

while True:

    time +=1
    #TODO: liigutada see vastasesse või objekti
    if time == 120:
        vastane.speed = [0,0]
    taust.render()
    to_render.append(vastane)
    to_render.append(mikro)

    if joonistab:
        pintsel.joonista(8,0.75,200,7)
    else:
        if detection_positions:
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
            if event.key in fv.up:
                mikro.speed[1] -= mikro.base_speed
            if event.key in fv.down:
                mikro.speed[1] += mikro.base_speed
            if event.key in fv.left:
                mikro.speed[0] -= mikro.base_speed
            if event.key in fv.right:
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
                brush_size, alpha, last_pos = 2,0, None
                slow_speed = 3.75
                strokes = []
                fv.set_nearest_offscreen_pos(pygame.mouse.get_pos(),pintsel,ekraan_suurus)

        #hiire nupp üles
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                joonistab = False


    # Uuendame ekraani
    pygame.display.update()
    timer.tick(FPS)