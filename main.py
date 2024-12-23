import pygame, sys, math, random
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
canvas = pygame.Surface(ekraan_suurus, pygame.SRCALPHA)
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
        self.sprite = sprite or "placeholder.png"
        if self.sprite[-1].lower() == 'f':
            self.sprite = pygame.image.load("Sprites/" + self.sprite[0:-1])
            self.sprite = pygame.transform.flip(self.sprite, True, False)
        else:
            self.sprite = pygame.image.load("Sprites/"+self.sprite)

        if self.width is not None:
            heightdivwidth = (self.sprite.get_height() / self.sprite.get_width())
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
        self.sprite_num = 0
        self.walk_change = 0
    def play_animation(self,sprites):
        if isinstance(sprites,str):
            self.change_sprite(sprites)
        elif not self.frames_per_sprite:
            self.change_sprite(sprites[0])
        else:
            self.walk_change += 1
            num_sprites = len(sprites)
            if self.walk_change == self.frames_per_sprite:
                self.sprite_num = (self.sprite_num + 1) % num_sprites  # Cycle through the sprites
                self.walk_change = 0

            self.change_sprite(sprites[self.sprite_num])
    def sprite_in_direction(self):
        if self.speed[0] < 0: #vasakule
            self.play_animation(self.left_sprites)
        elif self.speed[0] > 0:  # paremale
            self.play_animation(self.right_sprites)
        elif self.speed[1]  < 0:#üles
            self.play_animation(self.up_sprites)
        elif self.speed[1] > 0:  # alla
            self.play_animation(self.down_sprites)
        elif self.still_sprites: #paigal
            self.play_animation(self.still_sprites)
    def render(self):
        self.sprite_in_direction()
        super().render()

class Pintsel(Objekt):
    def __init__(self, sprite, width, brush_size=None):
        super().__init__(sprite, pos=[0, 0], width=width)
        self.brush_size = brush_size or 20 # siin ma panin defaultiks 20, jummala umbes lih
        self.brush_textures = []
        self.previous_brush_size = 0
        self.MAX_ITERATIONS = 125 # spaces ei saa olla suurem kui see

        self.load_brush_textures()

    # Siin saaks tglt optimeerida veel paremini dictionaryga: brush_textures{brush_size: [preloaded brushes], brush_size:[preloaded brushes, jne]}
    # siis ta cahce-iks koik tehtud texturid tulevikuks ara, juhul kui brush size jalle tagasi muudetakse
    def load_brush_textures(self):
        """ Preload brush textures with different rotations """
        if self.brush_size == self.previous_brush_size:
            return self.brush_textures
        else:
            self.brush_textures = []
            for angle in range(0, 360, 10):
                texture = pygame.image.load("Sprites/draw_texture.png").convert_alpha()
                scaled_texture = pygame.transform.scale(texture, (self.brush_size, self.brush_size))
                rotated_texture = pygame.transform.rotate(scaled_texture, angle)
                self.brush_textures.append(rotated_texture)

    def get_random_brush_texture(self):
        """ Return a random brush texture from the preloaded list """
        return random.choice(self.brush_textures)

    def render(self):
        global slow_speed
        mouse_x = self.mouse_pos[0]
        mouse_y = self.mouse_pos[1] -self.sprite.get_height() # selleks, et pintsli vasak alumine äär oleks kursori peal
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
        self.mouse_pos = pygame.mouse.get_pos()
        global last_pos, strokes, detection_positions, brush_size, alpha
        detection_positions.append(self.mouse_pos)
        if brush_size < MAX_BRUSH_SIZE:
            brush_size += BRUSH_CHANGE_RATE
        if alpha < MAX_ALPHA:
            alpha += ALPHA_CHANGE_RATE
        if last_pos:
            vektor = fv.get_vector(self.mouse_pos, last_pos)
            vektor_length = fv.get_vector_length(vektor)

            #Not gonna lie, suht low effort viis selle probleemi lahendamiseks, aga outcome enamvähem, kuskil sügavamal probleem, pole nii tuttav pygame-iga, et prg parandada
            spaces = min(max(1, int(vektor_length / brush_size * min(brush_size, 3))), self.MAX_ITERATIONS)
            print(spaces)
            for space in range(1, spaces + 1, 2):
                factor = space / spaces
                new_pos = [lp + v * factor for lp, v in zip(last_pos, vektor)]
                strokes.append(Värv(new_pos))
        last_pos = self.mouse_pos
#self.speed toimib nii et võtab asukoha kuhu saada tahab ja asukoha, kus on ja leieb nende vektori
#,suunaga sinna poole kuhu saada tahetakse ja jagab selle jump slow-iga


class Värv(Objekt):
    def __init__(self, pos):
        super().__init__(pos=pos)
        self.alpha = alpha
        self.sprite = pintsel.get_random_brush_texture()
        self.sprite.set_alpha(self.alpha)

    def render(self):
        global strokes, joonistab
        if joonistab == False and strokes[0].pos == self.pos:
            a = math.floor(len(strokes)/5)
            for i in range(a):
                del strokes[i]
            if a == 0:
                del strokes[0]
        aken.blit(self.sprite, self.pos)

class Vastane(Character):
    pass

taust = Objekt('background.png', width=ekraan_laius)
mikro = Character("mikro_left.png", [100,300], width=100, base_speed=8)
mikro.set_sprites('mikro_away.png','mikro_forward.png','mikro_left.png','mikro_right.png')
pintsel = Pintsel("pencil.png", width=200 )
vastane = Vastane("man_shoot.png",[100,300], speed=(2.5,0), width=100, base_speed=8)
vastane.set_sprites(['man_away.png','man_away.pngf'],['man_forward.png','man_forward.pngf'],['man_side.png','man_side2.png'],['man_side.pngf','man_side2.pngf'],10, 'man_shoot.png')


joonistab = False
to_render = []
strokes = []
detection_positions = []
render_list2 = []
BRUSH_START_SIZE = 2
BRUSH_START_ALPHA = 10



while True:

    time +=1
    if time == 1000:
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
                brush_size, alpha, last_pos = BRUSH_START_SIZE,BRUSH_START_ALPHA, None
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