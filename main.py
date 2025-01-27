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
class Objekt(pygame.sprite.Sprite):
    def __init__(self, sprite = None, pos = None, width = None, base_speed = None):
        super().__init__()
        self.speed = [0,0]
        self.rect = pos or [0, 0]
        self.width = width
        self.change_sprite(sprite)
        self.base_speed = base_speed or [0,0]
    def update(self):
        self.rect = fv.get_vectors_sum(self.rect, self.speed)

    def change_sprite(self, sprite = None):
        self.image = sprite or "placeholder.png"
        if self.image[-1].lower() == 'f':
            self.image = pygame.image.load("Sprites/" + self.image[0:-1])
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = pygame.image.load("Sprites/" + self.image)

        if self.width is not None:
            heightdivwidth = (self.image.get_height() / self.image.get_width())
            self.image = pygame.transform.scale(self.image, (self.width, heightdivwidth * self.width))


# kui spritei nime lõpus on f siis ta flippib spritei
class Character(Objekt):
    def set_sprites(self,up_sprites, down_sprites, left_sprites, right_sprites,frames_per_sprite=None,still_sprites=None):
        self.up_sprites = up_sprites
        self.down_sprites = down_sprites
        self.left_sprites = left_sprites
        self.right_sprites = right_sprites
        self.frames_per_sprite = frames_per_sprite
        self.still_sprites = still_sprites
        self.current_animation = self.still_sprites
        self.current_sprite = 0
        self.hold_frame = 11.5
        self.change_speed(0,0)
    def change_speed(self,x=0,y=0):
        self.speed = fv.get_vectors_sum(self.speed,(x,y))
        if self.speed[0] < 0: #vasakule
            self.current_animation = self.left_sprites
        elif self.speed[0] > 0:  # paremale
            self.current_animation = self.right_sprites
        elif self.speed[1]  < 0:#üles
            self.current_animation = self.up_sprites
        elif self.speed[1] > 0:  # alla
            self.current_animation = self.down_sprites
        elif self.still_sprites: #paigal
            self.current_animation = self.still_sprites
        if isinstance(self.current_animation, str):
             self.animating = False
             self.change_sprite(self.current_animation)
        else: self.animating = True

    def play_animation(self):
        if self.animating:
            self.current_sprite += 1 / self.hold_frame
            if int(self.current_sprite) >= len(self.current_animation):
                self.current_sprite = 0
            self.change_sprite(self.current_animation[int(self.current_sprite)])

class Pintsel(Objekt):
    def __init__(self, sprite, width):
        super().__init__(sprite, pos=[0, 0], width=width)
        self.brush_textures = []
        self.load_brush_textures()

    # Siin saaks tglt optimeerida veel paremini dictionaryga: brush_textures{brush_size: [preloaded brushes], brush_size:[preloaded brushes, jne]}
    # siis ta cahce-iks koik tehtud texturid tulevikuks ara, juhul kui brush size jalle tagasi muudetakse
    def load_brush_textures(self):
        for angle in range(0, 360, 10):
            texture = pygame.image.load("Sprites/draw_texture.png")
            rotated_texture = pygame.transform.rotate(texture, angle)
            rotated_texture.convert_alpha()
            self.brush_textures.append(rotated_texture)

    def get_random_brush_texture(self):
        """ Return a random brush texture from the preloaded list """
        return random.choice(self.brush_textures)

    def update(self):
        global slow_speed
        mouse_x = self.mouse_pos[0]
        mouse_y = self.mouse_pos[1] -self.image.get_height() # selleks, et pintsli vasak alumine äär oleks kursori peal
        speed_x = mouse_x - self.rect[0]
        speed_y = mouse_y - self.rect[1]
        if slow_speed > 1.2:
            slow_speed -= 0.2
            self.speed = (speed_x/slow_speed, speed_y/slow_speed)
        else:
            self.speed = [0,0]
            self.rect = (mouse_x, mouse_y)
        super().update()

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
            spaces = max(1, int(vektor_length / brush_size * min(brush_size, 3)))
            for space in range(spaces):
                factor = space / spaces
                new_pos = [lp + v * factor for lp, v in zip(last_pos, vektor)]
                strokes.add(Värv(new_pos,alpha,brush_size))
        last_pos = self.mouse_pos

class Värv(pygame.sprite.Sprite):
    def __init__(self, pos,alpha, brush_size):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pos
        self.brush_size = brush_size
        self.alpha = alpha
        self.image = pintsel.get_random_brush_texture()
        self.image = pygame.transform.scale(self.image,(brush_size,brush_size))
        self.image.set_alpha(self.alpha)

class Vastane(Character):
    pass
taust = Objekt('background.png', width=ekraan_laius)
mikro = Character("mikro_left.png", [100,300], width=100, base_speed=8)
mikro.set_sprites('mikro_away.png','mikro_forward.png','mikro_left.png','mikro_right.png')
pintsel = Pintsel("pencil.png", width=200)
vastane = Vastane(pos=[500,300], width=100, base_speed=4)
vastane.set_sprites(['man_away.png','man_away.pngf'],['man_forward.png','man_forward.pngf'],['man_side.png','man_side2.png'],['man_side.pngf','man_side2.pngf'],10, 'man_shoot.png')


joonistab = False
to_render = pygame.sprite.LayeredUpdates()
strokes = pygame.sprite.Group()
detection_positions = []
BRUSH_START_SIZE = 2
BRUSH_START_ALPHA = 10

to_render.add(taust,vastane,mikro)


while True:

    time +=1
    if time == 100:
        vastane.change_speed(y=vastane.base_speed)

    elif time == 150:
        vastane.change_speed(y=-vastane.base_speed)


    if joonistab:
        pintsel.joonista(10,0.75,200,7)
    else:
        a = max(1,math.floor(len(strokes)/7))
        b = list(strokes)[:a]
        strokes.remove(*b)
        to_render.remove(*b)
        if detection_positions:
            if fv.is_line(detection_positions):
                center = fv.get_vectors_sum(detection_positions[0],detection_positions[-1])
                center = (center[0]/2,center[1]/2)
                to_render.add(Objekt(pos=center))
            detection_positions.clear()

    if vastane.rect[1]+vastane.image.get_height() > mikro.rect[1]+mikro.image.get_height():
        to_render.change_layer(vastane,2)
        to_render.change_layer(mikro, 1)
    else:
        to_render.change_layer(vastane, 1)
        to_render.change_layer(mikro, 2)

    to_render.add(strokes, layer=3)
    vastane.play_animation()
    to_render.update()
    to_render.draw(aken)

    #iga kord kui on sündmus
    for event in pygame.event.get():
        #quit event
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        #klaviatuuri nupp alla
        elif event.type == pygame.KEYDOWN:
            if event.key in fv.up:
                mikro.change_speed(y=-mikro.base_speed)
            if event.key in fv.down:
                mikro.change_speed(y=mikro.base_speed)
            if event.key in fv.left:
                mikro.change_speed(-mikro.base_speed)
            if event.key in fv.right:
                mikro.change_speed(mikro.base_speed)
        #klaviatuuri nupp üles
        elif event.type == pygame.KEYUP:
            if event.key in fv.up:
                mikro.change_speed(y=mikro.base_speed)
            if event.key in fv.down:
                mikro.change_speed(y=-mikro.base_speed)
            if event.key in fv.left:
                mikro.change_speed(mikro.base_speed)
            if event.key in fv.right:
                mikro.change_speed(-mikro.base_speed)

        #hiire nupp alla
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                joonistab = True
                brush_size, alpha, last_pos = BRUSH_START_SIZE,BRUSH_START_ALPHA, None
                slow_speed = 3.75
                strokes.empty()
                fv.set_nearest_offscreen_pos(pygame.mouse.get_pos(),pintsel,ekraan_suurus)
                to_render.add(pintsel,layer=4)

        #hiire nupp üles
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                joonistab = False
                to_render.remove(pintsel)


    # Uuendame ekraani
    pygame.display.update()
    timer.tick(FPS)