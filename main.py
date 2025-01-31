import pygame, sys, math, random


import functions_values as fv


pygame.init()
pygame.font.init()

# Põhi sätted
font = pygame.font.Font('GOTHIC.TTF', 40)  # valib fondi ja selle suuruse
clock = pygame.time.Clock()
pygame.display.set_caption("Mäng")

# Ekraan
FPS = 60
ekraan_laius,ekraan_pikkus = 880, 700
ekraan_suurus = (ekraan_laius, ekraan_pikkus)  # kui suur on aken kus mäng toimub
aken = pygame.display.set_mode(ekraan_suurus) #pygame.NOFRAME
time = 0

# Mõned värvid
must = (0, 0, 0)
canvas = pygame.Surface(ekraan_suurus, pygame.SRCALPHA)
class Objekt(pygame.sprite.Sprite):
    def __init__(self,x=0,y=0,speed = None, sprite = None, width = None, base_speed = None):
        super().__init__()
        speed = speed or (0,0)

        self.speed = pygame.math.Vector2(speed)
        self.pos = pygame.math.Vector2(x,y)
        self.width = width
        self.change_sprite(sprite)
        self.rect = pygame.Rect(0,0, self.width, self.height)
        self.base_speed = base_speed or 0
    def update(self):
        self.pos = self.pos + self.speed
        self.rect = pygame.Rect(0,0, self.width, self.height)
        self.rect.topleft = self.pos

    def change_sprite(self, sprite = None):
        self.image = sprite or "placeholder.png"
        if self.image[-1].lower() == 'f':
            self.image = pygame.image.load("Sprites/" + self.image[0:-1])
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = pygame.image.load("Sprites/" + self.image)

        if self.width is not None:
            heightdivwidth = (self.image.get_height() / self.image.get_width())
            self.height = round(heightdivwidth * self.width)
            self.image = pygame.transform.scale(self.image, (self.width,self.height))


# kui spritei nime lõpus on f siis ta flippib spritei
class Character(Objekt):
    def set_sprites(self,up_sprites, down_sprites, left_sprites, right_sprites,still_sprites=None,hold_frame=None):
        self.up_sprites = up_sprites
        self.down_sprites = down_sprites
        self.left_sprites = left_sprites
        self.right_sprites = right_sprites
        self.still_sprites = still_sprites
        self.current_animation = self.still_sprites
        self.current_sprite = 0
        self.hold_frame = hold_frame or 11.5
        self.last_speed = self.speed
        self.animating = False
        self.change_speed()

    def change_speed(self,direction=None):
        x, y = 0, 0
        match direction:
            case 'up':
                y = -self.base_speed
            case 'down':
                y = self.base_speed
            case 'left':
                x = -self.base_speed
            case 'right':
                x = self.base_speed
            case _:
                x,y = -self.speed[0], -self.speed[1]
        self.speed = self.speed + (x,y)
        if self.last_speed != self.speed:
            self.last_speed = self.speed
            if self.speed.x < 0:  # vasakule
                self.current_animation = self.left_sprites
            elif self.speed.x > 0:  # paremale
                self.current_animation = self.right_sprites
            elif self.speed.y < 0:  # üles
                self.current_animation = self.up_sprites
            elif self.speed.y > 0:  # alla
                self.current_animation = self.down_sprites
            elif self.still_sprites:  # paigal
                self.current_animation = self.still_sprites
        if isinstance(self.current_animation, str):
            self.animating = False
            self.change_sprite(self.current_animation)
        else:
            self.animating = True
    def play_animation(self):
        if self.animating:
            self.current_sprite += 1 / self.hold_frame
            if int(self.current_sprite) >= len(self.current_animation):
                self.current_sprite = 0
            self.change_sprite(self.current_animation[int(self.current_sprite)])
    def update(self):
        global ekraan_suurus
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.pos = self.pos + self.speed
        self.pos.x = pygame.math.clamp(self.pos.x,0, ekraan_suurus[0])
        self.pos.y = pygame.math.clamp(self.pos.y,100 + self.rect.h, ekraan_suurus[1])
        self.rect.center = self.pos
class Pintsel(Objekt):
    def __init__(self, sprite, width,BRUSH_START_SIZE, BRUSH_START_ALPHA):
        super().__init__(x=0,y=0,sprite=sprite, width=width)
        self.brush_textures = []
        self.load_brush_textures()
        self.brush_start = BRUSH_START_SIZE
        self.alpha_start = BRUSH_START_ALPHA
        self.strokes = pygame.sprite.Group()
        self.detection_positions = []
    def set_variables_to_defaults(self):
        global to_render,ekraan_suurus
        self.brush_size, self.alpha, self.last_pos = self.brush_start,self.alpha_start, None
        self.speed = pygame.math.Vector2()
        self.slow_speed = 4
        to_render.remove(self.strokes)
        self.strokes.empty()
        fv.set_nearest_offscreen_pos(pygame.mouse.get_pos(), self, ekraan_suurus)
        to_render.add(self, layer=4)
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
        pass
    def joonista(self,MAX_BRUSH_SIZE,BRUSH_CHANGE_RATE,MAX_ALPHA,ALPHA_CHANGE_RATE):
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pos = pygame.math.Vector2(self.mouse_pos[0],self.mouse_pos[1])
        #algab pintsli liikumise kood
        speed = self.mouse_pos - self.pos
        if self.slow_speed > 1.2:
            self.slow_speed -= 0.2
            self.speed = pygame.math.Vector2(speed/self.slow_speed)
            self.pos = self.pos + self.speed
        else:
            self.pos = pygame.math.Vector2(self.mouse_pos)
        self.rect.bottomleft = self.pos
        #lõppeb pintsli liikumise kood
        #algab joonistamise kood
        self.detection_positions.append(self.mouse_pos)
        if self.brush_size < MAX_BRUSH_SIZE:
            self.brush_size += BRUSH_CHANGE_RATE
        if self.alpha < MAX_ALPHA:
            self.alpha += ALPHA_CHANGE_RATE
        if self.last_pos:
            vektor =  self.mouse_pos - self.last_pos
            vektor_length = vektor.length()
            spaces = max(1, int(vektor_length / self.brush_size * min(self.brush_size, 3)))
            for space in range(spaces):
                factor = space / spaces
                new_pos = self.last_pos + vektor * factor
                self.strokes.add(Värv(new_pos,self.alpha,self.brush_size))
        self.last_pos = self.mouse_pos
    def värvi_ära_hajumine(self):
        global to_render
        mitu_eemaldada = max(1, math.floor(len(self.strokes) / 7))
        mida_eemaldada = list(self.strokes)[:mitu_eemaldada]
        self.strokes.remove(*mida_eemaldada)
        to_render.remove(*mida_eemaldada)
    def get_line_collide_rect(self):
        vektor = self.detection_positions[-1] - self.detection_positions[0]
        rect = pygame.Rect(0,0,0,0)



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
    def collided_with(self,other):
        pass
    def cut_in_half(self,cut_vektor):
        pass
taust = Objekt(sprite='background.png', width=ekraan_laius)
mikro = Character(0,0,sprite = "mikro_right.png", width=100, base_speed=8)
mikro.set_sprites('mikro_away.png','mikro_forward.png','mikro_left.png','mikro_right.png')
pintsel = Pintsel("pencil.png", width=200,BRUSH_START_SIZE=2,BRUSH_START_ALPHA=10)
vastane = Vastane(500,400, width=100, base_speed=4)
vastane.set_sprites(['man_away.png','man_away.pngf'],['man_forward.png','man_forward.pngf'],['man_side.png','man_side2.png'],['man_side.pngf','man_side2.pngf'], 'man_shoot.png')


joonistab = False
to_render = pygame.sprite.LayeredUpdates()
to_render.add(taust,vastane,mikro)

while True:

    time +=1
    if time == 100:
        vastane.change_speed("down")
    elif time == 150:
        vastane.change_speed()
    elif time == 200:
        vastane.change_speed("left")
    elif time == 250:
        vastane.change_speed()
    elif time == 300:
        vastane.change_speed("up")
    elif time == 350:
        vastane.change_speed()
    elif time == 400:
        vastane.change_speed("right")
    elif time == 500:
        vastane.change_speed()



    if joonistab:
        pintsel.joonista(10,0.75,200,7)
    else:
        if pintsel.strokes:
            pintsel.värvi_ära_hajumine()
        if pintsel.detection_positions:
            if fv.is_line(pintsel.detection_positions):
                center = pintsel.detection_positions[0] + pintsel.detection_positions[-1]
                to_render.add(pintsel.get_line_collide_rect())
            pintsel.detection_positions.clear()
    if vastane.rect.bottom > mikro.rect.bottom:
        to_render.change_layer(vastane,2)
        to_render.change_layer(mikro, 1)
    else:

        to_render.change_layer(vastane, 1)
        to_render.change_layer(mikro, 2)

    to_render.add(pintsel.strokes, layer=3)
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
                mikro.change_speed("up")
            if event.key in fv.down:
                mikro.change_speed("down")
            if event.key in fv.left:
                mikro.change_speed("left")
            if event.key in fv.right:
                mikro.change_speed("right")
        #klaviatuuri nupp üles
        elif event.type == pygame.KEYUP:
            if event.key in fv.up:
                mikro.change_speed("down")
            if event.key in fv.down:
                mikro.change_speed("up")
            if event.key in fv.left:
                mikro.change_speed("right")
            if event.key in fv.right:
                mikro.change_speed("left")

        #hiire nupp alla
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                joonistab = True
                pintsel.set_variables_to_defaults()


        #hiire nupp üles
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                joonistab = False
                to_render.remove(pintsel)


    # Uuendame ekraani
    pygame.display.update()
    clock.tick(FPS)